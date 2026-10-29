"""Compose existing citation audit with a bound, declared argument review."""
from .evidence_audit import audit, fingerprint

__ts_layer__ = "surface"
__ts_purpose__ = "Bounded argument review attached to quotation evidence."


def binding(row, argument):
    return fingerprint({'citation_review_binding': row['review_binding'],
                        'argument': {k: v for k, v in argument.items() if k != 'assessment'}})

def inspect_argument(row, argument):
    if argument is None:
        return {'status': 'missing_argument', 'blockers': ['document_support_relation']}
    blockers = []
    for field in ('warrant', 'scope', 'does_not_establish', 'defeaters', 'assumptions'):
        if not argument.get(field):
            blockers.append('missing_' + field)
    for assumption in argument.get('assumptions', []):
        if assumption.get('status') != 'reviewed_for_this_scope' or not assumption.get('basis'):
            blockers.append('unresolved_assumption')
    if row['citation'] != 'exact':
        blockers.append('citation_not_exact')
    if row['semantic_support'] != 'reviewed_supports':
        blockers.append('semantic_review_not_supporting')
    assessment = argument.get('assessment', {})
    if assessment.get('binding') != binding(row, argument):
        blockers.append('stale_or_missing_argument_review')
    if not assessment.get('reviewer') or not assessment.get('reason'):
        blockers.append('missing_review_explanation')
    return {'status': 'blocked' if blockers else 'declared_review_current',
            'blockers': sorted(set(blockers)), 'warrant': argument.get('warrant'),
            'scope': argument.get('scope'),
            'does_not_establish': argument.get('does_not_establish'),
            'defeaters': argument.get('defeaters'),
            'limitations': '審閱內容與身分是聲明；本程式不自動證明邏輯或事實真偽。'}

def integrate(case, arguments, root):
    result = audit(case, root)
    valid_ids = {r['id'] for r in result['claims']}
    if set(arguments) - valid_ids:
        raise ValueError('argument points to unknown claim')
    for row in result['claims']:
        row['argument_review'] = inspect_argument(row, arguments.get(row['id']))
        row['decision_authorized'] = False
        row['forecast_scoring_eligible'] = False
    result['integration_version'] = '0.1'
    result['limitations'].append('Current argument review is not prediction validity or trading permission.')
    return result
