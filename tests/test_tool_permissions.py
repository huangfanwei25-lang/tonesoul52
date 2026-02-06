from memory.genesis import Genesis
from tools.schema import enforce_responsibility_tier


def test_enforce_responsibility_tier_allows_higher_tier():
    result = enforce_responsibility_tier(
        genesis=Genesis.AUTONOMOUS,
        minimum="TIER_2",
        action="post",
    )
    assert result is None


def test_enforce_responsibility_tier_blocks_lower_tier():
    result = enforce_responsibility_tier(
        genesis=Genesis.MANDATORY,
        minimum="TIER_2",
        action="post",
    )
    assert result is not None
    assert result["success"] is False
    assert result["error"]["code"] == "E010"
    assert result["error"]["details"]["required_tier"] == "TIER_2"
    assert result["error"]["details"]["actual_tier"] == "TIER_3"
