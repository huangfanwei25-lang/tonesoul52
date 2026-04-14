"""Tests for Phase 851: High-Risk Grounding Check."""

from tonesoul.grounding_check import GroundingResult, grounding_check


class TestGroundingCheckBasic:
    """Basic grounding check behavior."""

    def test_empty_response(self):
        result = grounding_check("", "hello")
        assert result.thin_support is False
        assert result.reason == "empty_response"

    def test_no_factual_claims(self):
        result = grounding_check(
            "我覺得這個點子很棒，繼續加油！",
            "你覺得怎樣？",
        )
        assert result.factual_claim_count == 0
        assert result.thin_support is False
        assert result.reason == "no_factual_claims"

    def test_grounded_claims_from_user_echo(self):
        result = grounding_check(
            "根據你提到的數據，去年的增長了 15%，報告顯示穩定。",
            "去年的報告增長了 15%",
        )
        # Claims reference user content — should be grounded
        assert result.thin_support is False

    def test_ungrounded_claims_trigger_thin_support(self):
        response = (
            "根據 2025 年的報告，該公司營收成長了 23%。"
            "分析顯示利潤率下降了 5.2%。"
            "數據表明第三季度增長了 $4.5 billion。"
        )
        result = grounding_check(response, "告訴我這家公司的情況")
        # Multiple factual claims with no grounding in user query
        assert result.factual_claim_count >= 2
        assert result.thin_support is True
        assert result.reason == "thin_support_detected"

    def test_caveats_prevent_thin_support(self):
        response = (
            "根據公開數據，營收可能增長了 23%，但無法確認。" "報告或許顯示利潤率約 5%，請自行查核。"
        )
        result = grounding_check(response, "告訴我情況")
        # Has caveats — should count as grounded
        assert result.caveat_count >= 1
        assert result.thin_support is False

    def test_context_keywords_ground_claims(self):
        response = "根據分析，TSMC 的營收成長了 15%。報告顯示 AMD 增長了 8%。"
        result = grounding_check(
            response,
            "比較一下",
            context_keywords=["TSMC", "AMD", "營收", "成長"],
        )
        # Keywords from context provide grounding
        assert result.thin_support is False


class TestGroundingResult:
    """GroundingResult serialization."""

    def test_to_dict(self):
        r = GroundingResult(
            factual_claim_count=3,
            grounded_count=1,
            caveat_count=0,
            ungrounded_ratio=0.6667,
            thin_support=True,
            reason="thin_support_detected",
        )
        d = r.to_dict()
        assert d["thin_support"] is True
        assert d["factual_claim_count"] == 3
        assert d["ungrounded_ratio"] == 0.6667

    def test_frozen(self):
        r = GroundingResult()
        try:
            r.thin_support = True  # type: ignore[misc]
            assert False, "Should be frozen"
        except AttributeError:
            pass


class TestGroundingThreshold:
    """Threshold behavior."""

    def test_single_ungrounded_claim_no_trigger(self):
        # Only 1 claim — below the minimum count of 2
        result = grounding_check(
            "根據報告，營收成長了 23%。",
            "隨便問",
        )
        assert result.factual_claim_count >= 1
        # Even if ungrounded, single claim doesn't trigger thin_support
        assert result.thin_support is False

    def test_custom_threshold(self):
        response = "在 2024 年，營收增長了 10%。" "報告顯示成長了 5%。" "根據你提供的數據趨勢上升。"
        # With a very low threshold, even partial ungrounding triggers
        result = grounding_check(response, "看看趨勢", thin_support_threshold=0.3)
        # At least some claims exist
        assert result.factual_claim_count >= 2
