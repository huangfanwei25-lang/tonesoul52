from tonesoul.council.perspectives.guardian import GuardianPerspective
from tonesoul.council.types import VoteDecision


def test_guardian_blocks_english_keywords():
    guardian = GuardianPerspective()
    vote = guardian.evaluate("This describes a bomb attack plan.", context={})
    assert vote.decision == VoteDecision.OBJECT


def test_guardian_blocks_chinese_keywords():
    guardian = GuardianPerspective()
    vote = guardian.evaluate(
        "\u9019\u662f\u4e00\u500b\u70b8\u5f48\u653b\u64ca\u7684\u8a08\u756b\u3002", context={}
    )
    assert vote.decision == VoteDecision.OBJECT


def test_guardian_concern_keywords_bilingual():
    guardian = GuardianPerspective()
    vote_en = guardian.evaluate("This seems unsafe and risky.", context={})
    vote_zh = guardian.evaluate("\u9019\u500b\u60f3\u6cd5\u5f88\u5371\u96aa\u3002", context={})
    assert vote_en.decision == VoteDecision.CONCERN
    assert vote_zh.decision == VoteDecision.CONCERN


def test_guardian_does_not_block_innocent_term():
    guardian = GuardianPerspective()
    vote = guardian.evaluate(
        "\u6211\u53ea\u662f\u60f3\u6bba\u6642\u9593\u653e\u9b06\u4e00\u4e0b\u3002", context={}
    )
    assert vote.decision == VoteDecision.APPROVE
