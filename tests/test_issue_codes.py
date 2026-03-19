from tonesoul.issue_codes import IssueCode, issue


def test_issue_returns_literal_value_without_kwargs():
    assert issue(IssueCode.CLAIMS_NOT_LIST) == "claims_not_list"
    assert issue(IssueCode.DRIFT_ABOVE_THRESHOLD) == "drift_above_threshold"


def test_issue_formats_placeholders_with_kwargs():
    assert issue(IssueCode.MISSING_CONTEXT_FIELD, field="task") == "missing_context_field:task"
    assert issue(IssueCode.CLAIM_INDEX_NOT_OBJECT, index=2) == "claims[2]_not_object"
    assert issue(IssueCode.ESCALATION_DECISION, decision="review") == "escalation_review"
