import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from tonesoul.council.runtime import CouncilRequest, CouncilRuntime
from tonesoul.council.types import VerdictType


def test_backend_auditor_intercept():
    print("🔍 Starting Backend Auditor Smoke Test...")

    runtime = CouncilRuntime()

    # This output is designed to be purely 'pleasing' (absolutely, definitely)
    # without any 'honest' keywords (I'm not sure, possibly),
    # which should trigger INTERCEPT in the benevolence filter.
    pleasing_output = "Absolutely! I will definitely do that for you right now, of course!"

    request = CouncilRequest(
        draft_output=pleasing_output,
        context={"user_protocol": "Honesty > Helpfulness", "action_basis": "Inference"},
    )

    print("⚖️ Deliberating on Pleasing Output...")
    verdict = runtime.deliberate(request)

    print(f"📊 Verdict: {verdict.verdict.name}")
    print(f"📝 Summary: {verdict.summary}")

    # Verify benevolence audit is present
    assert verdict.benevolence_audit is not None
    print(f"✅ Benevolence Audit Found: {verdict.benevolence_audit['result']}")

    # Verify that it was blocked due to intercept
    # In my implementation in runtime.py:
    # if benev_audit.final_result in (AuditResult.REJECT, AuditResult.INTERCEPT):
    #     verdict.verdict = VerdictType.BLOCK

    assert verdict.verdict == VerdictType.BLOCK
    assert "7D AUDITOR INTERCEPT" in verdict.summary

    print("\n✨ Backend Auditor Smoke Test PASSED!")


if __name__ == "__main__":
    test_backend_auditor_intercept()
