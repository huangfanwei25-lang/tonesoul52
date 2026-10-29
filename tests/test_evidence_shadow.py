import hashlib
import json

import pytest

from tonesoul.reviewer.report import review_text
from tonesoul.reviewer.shadow import review_shadow


def test_empty_sidecar_preserves_baseline(tmp_path):
    text = 'A bounded report.'
    sidecar = {'document_sha256': hashlib.sha256(text.encode()).hexdigest(),
               'case': {'schema_version': 1, 'sources': [], 'claims': []}, 'arguments': {}}
    p = tmp_path / 'case.json'
    p.write_text(json.dumps(sidecar))
    report = review_text(text, 'input.txt', generated_at='fixed')
    out = review_shadow(text, report, p)
    assert out['baseline'] == report
    assert out['mode'] == 'advisory_only'
    assert out['evidence']['claims'] == []


def test_wrong_document_rejected(tmp_path):
    p = tmp_path / 'case.json'
    p.write_text(json.dumps({'document_sha256': 'bad'}))
    with pytest.raises(ValueError, match='document'):
        review_shadow('text', {}, p)


def test_malformed_sidecar_rejected(tmp_path):
    p = tmp_path / 'case.json'
    p.write_text('[]')
    with pytest.raises(ValueError, match='object'):
        review_shadow('', {}, p)


def test_real_primary_source_replay():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / 'examples/evidence_shadow'
    text = (root / 'claims.txt').read_text()
    baseline = review_text(text, 'claims.txt')
    report = review_shadow(text, baseline, root / 'case.json')
    assert report['baseline'] == baseline
    claims = report['evidence']['claims']
    assert all(c['citation'] == 'exact' for c in claims)
    assert claims[0]['argument_review']['status'] == 'declared_review_current'
    assert claims[1]['semantic_support'] == 'reviewed_insufficient'
    assert claims[2]['semantic_support'] == 'reviewed_insufficient'
    assert all(not c['forecast_scoring_eligible'] for c in claims)
    assert all(not c['decision_authorized'] for c in claims)


def test_cli_bad_sidecar_returns_input_error(tmp_path, capsys):
    from tonesoul.cli.main import main

    text = tmp_path / 'draft.txt'
    text.write_text('A bounded report.')
    sidecar = tmp_path / 'case.json'
    sidecar.write_text('{}')
    assert main(['review', str(text), '--evidence-case', str(sidecar)]) == 3
    assert 'document hash mismatch' in capsys.readouterr().err


@pytest.mark.parametrize('mutation,expected', [
    ('scope', 'stale_or_missing_argument_review'),
    ('source', 'citation_not_exact'),
    ('claim', 'semantic_review_not_supporting'),
])
def test_source_claim_and_scope_changes_invalidate(tmp_path, mutation, expected):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / 'examples/evidence_shadow'
    data = json.loads((root / 'case.json').read_text())
    excerpt = (root / 'official_excerpt.txt').read_text()
    if mutation == 'scope':
        data['arguments']['TSMC-1']['scope'] = 'Future earnings are certain.'
    elif mutation == 'source':
        excerpt = 'changed source'
    else:
        data['case']['claims'][0]['text'] = 'Future earnings are certain.'
    (tmp_path / 'official_excerpt.txt').write_text(excerpt)
    sidecar = tmp_path / 'case.json'
    sidecar.write_text(json.dumps(data))
    text = (root / 'claims.txt').read_text()
    row = review_shadow(text, {}, sidecar)['evidence']['claims'][0]
    assert expected in row['argument_review']['blockers']
