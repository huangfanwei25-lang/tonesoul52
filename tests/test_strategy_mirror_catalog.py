"""Tests for tonesoul/gse/strategy_mirror — dataclasses + catalog loader.

Covers:
  - StrategyMove serialisation round-trip + frozen contract
  - DetectedMove + StrategySignature class-filtered queries + flags
  - CatalogLoader load + admission gate + duplicate-id guard +
    declared/actual count consistency check
  - Period 1 catalog actually loads and matches its declared shape
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.gse.strategy_mirror import (
    CatalogLoader,
    DetectedMove,
    StrategyMove,
    StrategySignature,
)

# ---------------------------------------------------------------------------
# StrategyMove — schema + provenance preservation
# ---------------------------------------------------------------------------


class TestStrategyMove:
    def _sample(self) -> StrategyMove:
        return StrategyMove(
            id="1.999.Test",
            symbol="[Test]",
            name="測試構造",
            pse_keyword="TestKeyword",
            pse_chinese_name="測試招",
            period=1,
            family="測試族",
            pse_definition="A test element for round-trip validation.",
            pse_operation="Operation text used in tests only.",
            transparency_class="yellow",
            rationale="One-sentence rationale used for admission gate testing.",
            surface_signals=["test", "marker"],
            structural_signals=["test_pattern"],
        )

    def test_round_trip_to_dict(self) -> None:
        move = self._sample()
        assert StrategyMove.from_dict(move.to_dict()) == move

    def test_all_required_fields_in_to_dict(self) -> None:
        d = self._sample().to_dict()
        for key in (
            "id",
            "symbol",
            "name",
            "pse_keyword",
            "pse_chinese_name",
            "period",
            "family",
            "pse_definition",
            "pse_operation",
            "transparency_class",
            "rationale",
            "surface_signals",
            "structural_signals",
        ):
            assert key in d, f"missing field: {key}"

    def test_frozen_cannot_mutate(self) -> None:
        move = self._sample()
        with pytest.raises(Exception):
            move.name = "changed"  # type: ignore[misc]

    def test_pse_provenance_preserved_verbatim(self) -> None:
        """Per spec §4.1: PSE source fields must be preserved verbatim."""
        move = self._sample()
        d = move.to_dict()
        # PSE side fields are the provenance pair
        assert d["pse_keyword"] == "TestKeyword"
        assert d["pse_chinese_name"] == "測試招"
        assert d["pse_definition"] == "A test element for round-trip validation."
        assert d["pse_operation"] == "Operation text used in tests only."


# ---------------------------------------------------------------------------
# DetectedMove + StrategySignature — class filtering and flags
# ---------------------------------------------------------------------------


def _make_move(id_: str, cls: str) -> StrategyMove:
    return StrategyMove(
        id=id_,
        symbol=f"[{id_}]",
        name=f"name-{id_}",
        pse_keyword=f"kw-{id_}",
        pse_chinese_name=f"中-{id_}",
        period=1,
        family="天文學",
        pse_definition="def",
        pse_operation="op",
        transparency_class=cls,  # type: ignore[arg-type]
        rationale="r",
    )


class TestStrategySignature:
    def test_class_filtered_queries(self) -> None:
        sig = StrategySignature(
            detected_moves=[
                DetectedMove(move=_make_move("g1", "green")),
                DetectedMove(move=_make_move("y1", "yellow")),
                DetectedMove(move=_make_move("y2", "yellow"), declared=True),
                DetectedMove(move=_make_move("r1", "red")),
            ]
        )
        assert len(sig.green_moves()) == 1
        assert len(sig.yellow_moves()) == 2
        assert len(sig.red_moves()) == 1

    def test_undeclared_yellow_filter(self) -> None:
        declared = DetectedMove(move=_make_move("y_d", "yellow"), declared=True)
        undeclared = DetectedMove(move=_make_move("y_u", "yellow"), declared=False)
        sig = StrategySignature(detected_moves=[declared, undeclared])
        u = sig.undeclared_yellow_moves()
        assert len(u) == 1
        assert u[0].move.id == "y_u"

    def test_has_red_flag_set_when_red_present(self) -> None:
        sig = StrategySignature(detected_moves=[DetectedMove(move=_make_move("r1", "red"))])
        assert sig.has_red is True
        assert sig.requires_council_re_review() is True

    def test_has_red_flag_false_when_no_red(self) -> None:
        sig = StrategySignature(
            detected_moves=[
                DetectedMove(move=_make_move("g1", "green")),
                DetectedMove(move=_make_move("y1", "yellow"), declared=True),
            ]
        )
        assert sig.has_red is False
        assert sig.requires_council_re_review() is False

    def test_undeclared_yellow_triggers_block(self) -> None:
        sig = StrategySignature(
            detected_moves=[DetectedMove(move=_make_move("y1", "yellow"), declared=False)]
        )
        assert sig.has_undeclared_yellow is True
        assert sig.requires_block() is True

    def test_declared_yellow_does_not_trigger_block(self) -> None:
        sig = StrategySignature(
            detected_moves=[DetectedMove(move=_make_move("y1", "yellow"), declared=True)]
        )
        assert sig.has_undeclared_yellow is False
        assert sig.requires_block() is False

    def test_to_dict_contains_counts_and_flags(self) -> None:
        sig = StrategySignature(
            detected_moves=[
                DetectedMove(move=_make_move("g1", "green")),
                DetectedMove(move=_make_move("y1", "yellow"), declared=False),
                DetectedMove(move=_make_move("r1", "red")),
            ]
        )
        d = sig.to_dict()
        assert d["counts"]["total"] == 3
        assert d["counts"]["green"] == 1
        assert d["counts"]["yellow"] == 1
        assert d["counts"]["red"] == 1
        assert d["counts"]["undeclared_yellow"] == 1
        assert d["flags"]["has_red"] is True
        assert d["flags"]["has_undeclared_yellow"] is True
        assert d["flags"]["requires_council_re_review"] is True
        assert d["flags"]["requires_block"] is True

    def test_empty_signature(self) -> None:
        sig = StrategySignature.empty()
        assert sig.detected_moves == []
        assert sig.has_red is False
        assert sig.has_undeclared_yellow is False
        assert "No strategy moves" in sig.summary


# ---------------------------------------------------------------------------
# CatalogLoader — admission gate, duplicate-id guard, declared/actual count
# ---------------------------------------------------------------------------


def _write_minimal_catalog(tmp_path: Path, elements: list, period: int = 1) -> Path:
    """Helper: write a minimal period_*.json with the given elements."""
    catalog = {
        "schema_version": "1.0",
        "period": period,
        "period_name": "test",
        "source": "test fixture",
        "ingestion_date": "2026-04-26",
        "elements_count": len(elements),
        "elements": elements,
    }
    path = tmp_path / f"period_{period}_test.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
    return path


class TestCatalogLoader:
    def _minimal_element(
        self,
        id_: str = "1.001.X",
        cls: str = "green",
        rationale: str = "test rationale",
    ) -> dict:
        return {
            "id": id_,
            "symbol": "[X]",
            "name": "test name",
            "pse_keyword": "kw",
            "pse_chinese_name": "中",
            "period": 1,
            "family": "測試",
            "pse_definition": "def",
            "pse_operation": "op",
            "transparency_class": cls,
            "rationale": rationale,
            "surface_signals": [],
            "structural_signals": [],
        }

    def test_load_minimal_catalog(self, tmp_path: Path) -> None:
        _write_minimal_catalog(tmp_path, [self._minimal_element()])
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        assert len(loader) == 1
        assert "1.001.X" in loader

    def test_admission_gate_blocks_empty_rationale(self, tmp_path: Path) -> None:
        bad = self._minimal_element(rationale="")
        _write_minimal_catalog(tmp_path, [bad])
        with pytest.raises(ValueError, match="empty rationale"):
            CatalogLoader(catalog_dir=tmp_path).load()

    def test_admission_gate_blocks_whitespace_rationale(self, tmp_path: Path) -> None:
        bad = self._minimal_element(rationale="   \n  ")
        _write_minimal_catalog(tmp_path, [bad])
        with pytest.raises(ValueError, match="empty rationale"):
            CatalogLoader(catalog_dir=tmp_path).load()

    def test_admission_gate_blocks_unknown_class(self, tmp_path: Path) -> None:
        bad = self._minimal_element(cls="purple")  # type: ignore[arg-type]
        _write_minimal_catalog(tmp_path, [bad])
        with pytest.raises(ValueError, match="unknown transparency_class"):
            CatalogLoader(catalog_dir=tmp_path).load()

    def test_duplicate_id_raises(self, tmp_path: Path) -> None:
        a = self._minimal_element(id_="1.001.X")
        b = self._minimal_element(id_="1.001.X")
        _write_minimal_catalog(tmp_path, [a, b])
        with pytest.raises(ValueError, match="duplicate id"):
            CatalogLoader(catalog_dir=tmp_path).load()

    def test_count_mismatch_raises(self, tmp_path: Path) -> None:
        # elements_count says 2 but only 1 element present
        catalog = {
            "schema_version": "1.0",
            "period": 1,
            "elements_count": 2,
            "elements": [self._minimal_element()],
        }
        path = tmp_path / "period_1_mismatch.json"
        path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(ValueError, match="out of sync"):
            CatalogLoader(catalog_dir=tmp_path).load()

    def test_query_by_class(self, tmp_path: Path) -> None:
        elements = [
            self._minimal_element(id_="1.001.A", cls="green"),
            self._minimal_element(id_="1.002.B", cls="yellow"),
            self._minimal_element(id_="1.003.C", cls="red"),
        ]
        _write_minimal_catalog(tmp_path, elements)
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        assert len(loader.by_class("green")) == 1
        assert len(loader.by_class("yellow")) == 1
        assert len(loader.by_class("red")) == 1

    def test_get_by_symbol_handles_multiple(self, tmp_path: Path) -> None:
        # PSE has heavy symbol collisions; loader must return all matches
        elements = [
            {**self._minimal_element(id_="1.001.Sp"), "symbol": "[Sp]"},
            {**self._minimal_element(id_="1.012.Sp"), "symbol": "[Sp]"},
        ]
        _write_minimal_catalog(tmp_path, elements)
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        sps = loader.get_by_symbol("[Sp]")
        assert len(sps) == 2

    def test_class_distribution_diagnostic(self, tmp_path: Path) -> None:
        elements = [
            self._minimal_element(id_="1.001.A", cls="green"),
            self._minimal_element(id_="1.002.B", cls="green"),
            self._minimal_element(id_="1.003.C", cls="yellow"),
            self._minimal_element(id_="1.004.D", cls="red"),
        ]
        _write_minimal_catalog(tmp_path, elements)
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        d = loader.class_distribution()
        assert d == {"green": 2, "yellow": 1, "red": 1}


# ---------------------------------------------------------------------------
# Period 1 — actual catalog file loads with declared shape
# ---------------------------------------------------------------------------


class TestPeriod1Catalog:
    def test_period_1_loads(self) -> None:
        loader = CatalogLoader().load()
        assert len(loader) == 150

    def test_period_1_class_distribution_matches_declared(self) -> None:
        loader = CatalogLoader().load()
        d = loader.class_distribution()
        # These match the values declared in period_1_foundation.json header
        # transparency_class_summary; if the catalog file is edited, this
        # test will catch the drift.
        assert d["green"] == 57
        assert d["yellow"] == 73
        assert d["red"] == 20

    def test_period_1_all_three_families_present(self) -> None:
        loader = CatalogLoader().load()
        f = loader.family_distribution()
        assert f["天文學"] == 50
        assert f["物理學"] == 50
        assert f["地質學"] == 50

    def test_period_1_all_ids_unique(self) -> None:
        loader = CatalogLoader().load()
        ids = loader.ids()
        assert len(ids) == len(set(ids))

    def test_period_1_all_have_rationale(self) -> None:
        loader = CatalogLoader().load()
        for m in loader.all():
            assert m.rationale, f"{m.id} missing rationale"
            assert len(m.rationale) > 10, f"{m.id} rationale too short"

    def test_period_1_pse_provenance_complete(self) -> None:
        """Every entry must carry PSE source verbatim per §4.1."""
        loader = CatalogLoader().load()
        for m in loader.all():
            assert m.pse_keyword, f"{m.id} missing pse_keyword"
            assert m.pse_chinese_name, f"{m.id} missing pse_chinese_name"
            assert m.pse_definition, f"{m.id} missing pse_definition"
            assert m.pse_operation, f"{m.id} missing pse_operation"

    def test_period_1_observation_pov_naming(self) -> None:
        """Spec §3.1: ToneSoul names must not literally equal PSE keywords.

        This is a soft check — many ToneSoul names will contain or echo
        the PSE concept, but exact equality of `name` to `pse_keyword`
        means the rename did not happen.
        """
        loader = CatalogLoader().load()
        for m in loader.all():
            assert (
                m.name != m.pse_keyword
            ), f"{m.id}: name={m.name!r} equals pse_keyword — rename per §3.1 missing"

    def test_period_1_metadata_present(self) -> None:
        loader = CatalogLoader().load()
        meta = loader.period_metadata(1)
        assert meta is not None
        assert "period_name" in meta
        assert "source" in meta
