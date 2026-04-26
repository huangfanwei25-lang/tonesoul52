"""Tests for tonesoul/gse — GSEElement schema and registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.gse import GSEElement, GSERegistry
from tonesoul.vow_system import Vow, VowAction


# ---------------------------------------------------------------------------
# GSEElement — schema and serialisation
# ---------------------------------------------------------------------------

class TestGSEElement:
    def _sample(self) -> GSEElement:
        return GSEElement(
            symbol="[Ten]",
            name="張力",
            definition="兩個合法價值之間的真實衝突點",
            role="主導",
            cluster="deliberation",
            period=1,
            trigger="當決策同時滿足兩個互斥的合法要求時",
            operation="1. 命名兩個衝突要求。2. 選擇一個並記錄代價。",
            falsifiable="輸出中有兩個被明確命名的衝突方向。",
        )

    def test_from_dict_round_trip(self) -> None:
        el = self._sample()
        restored = GSEElement.from_dict(el.to_dict())
        assert restored == el

    def test_all_fields_present_in_to_dict(self) -> None:
        d = self._sample().to_dict()
        for key in ("symbol", "name", "definition", "role", "cluster", "period",
                    "trigger", "operation", "falsifiable"):
            assert key in d

    def test_frozen_cannot_mutate(self) -> None:
        el = self._sample()
        with pytest.raises(Exception):
            el.name = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GSERegistry — load from clusters dir
# ---------------------------------------------------------------------------

CLUSTERS_DIR = Path(__file__).resolve().parent.parent / "tonesoul" / "gse" / "clusters"


class TestGSERegistry:
    def test_loads_all_twelve_elements(self) -> None:
        reg = GSERegistry().load()
        assert len(reg) == 12

    def test_deliberation_cluster_has_four_elements(self) -> None:
        reg = GSERegistry().load()
        els = reg.by_cluster("deliberation")
        assert len(els) == 4

    def test_interiority_cluster_has_four_elements(self) -> None:
        reg = GSERegistry().load()
        assert len(reg.by_cluster("interiority")) == 4

    def test_propagation_cluster_has_four_elements(self) -> None:
        reg = GSERegistry().load()
        assert len(reg.by_cluster("propagation")) == 4

    def test_role_counts(self) -> None:
        reg = GSERegistry().load()
        # 3 主導, 5 催化, 4 約束 (catalyst-heavy by design)
        assert len(reg.by_role("主導")) == 3
        assert len(reg.by_role("催化")) == 5
        assert len(reg.by_role("約束")) == 4

    def test_get_by_symbol(self) -> None:
        reg = GSERegistry().load()
        el = reg.get("[Ten]")
        assert el is not None
        assert el.cluster == "deliberation"
        assert el.role == "主導"

    def test_every_element_has_nonempty_operation(self) -> None:
        reg = GSERegistry().load()
        for el in reg.all():
            assert el.operation.strip(), f"{el.symbol} has empty operation"

    def test_every_element_has_nonempty_trigger(self) -> None:
        reg = GSERegistry().load()
        for el in reg.all():
            assert el.trigger.strip(), f"{el.symbol} has empty trigger"

    def test_every_element_has_nonempty_falsifiable(self) -> None:
        reg = GSERegistry().load()
        for el in reg.all():
            assert el.falsifiable.strip(), f"{el.symbol} has empty falsifiable"

    def test_empty_dir_returns_empty_registry(self, tmp_path: Path) -> None:
        reg = GSERegistry(clusters_dir=tmp_path).load()
        assert len(reg) == 0

    def test_symbols_sorted(self) -> None:
        reg = GSERegistry().load()
        syms = reg.symbols()
        assert syms == sorted(syms)


# ---------------------------------------------------------------------------
# Vow dataclass — GSE upgrade backward-compatibility
# ---------------------------------------------------------------------------

class TestVowGSEUpgrade:
    def _base_dict(self) -> dict:
        return {
            "id": "v-transparency",
            "title": "透明性",
            "description": "決策過程對相關方可見",
            "expected": {"transparency": 0.95},
        }

    def test_legacy_vow_loads_without_gse_fields(self) -> None:
        vow = Vow.from_dict(self._base_dict())
        assert vow.trigger is None
        assert vow.operation_instruction is None

    def test_gse_fields_round_trip(self) -> None:
        d = self._base_dict()
        d["trigger"] = "在做出不可逆決策前"
        d["operation_instruction"] = "1. 輸出決策脈絡。2. 記錄被放棄的替代方案。"
        vow = Vow.from_dict(d)
        assert vow.trigger == "在做出不可逆決策前"
        assert vow.operation_instruction == "1. 輸出決策脈絡。2. 記錄被放棄的替代方案。"

    def test_to_dict_omits_none_gse_fields(self) -> None:
        vow = Vow.from_dict(self._base_dict())
        d = vow.to_dict()
        assert "trigger" not in d
        assert "operation_instruction" not in d

    def test_to_dict_includes_gse_fields_when_set(self) -> None:
        d = self._base_dict()
        d["trigger"] = "當..."
        d["operation_instruction"] = "1. ..."
        vow = Vow.from_dict(d)
        out = vow.to_dict()
        assert out["trigger"] == "當..."
        assert out["operation_instruction"] == "1. ..."
