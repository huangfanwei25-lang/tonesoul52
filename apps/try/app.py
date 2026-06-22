"""ToneSoul - try it on your own output (Gradio / Hugging Face Space).

A no-install front door to the pre-output Council: paste a draft answer and see
the real gates run on it: per-perspective verdict, preserved dissent,
claim-boundary flags, grounding state. Same engine that ships as the
`ts validate` CLI.

The gates are model-free and deterministic: no LLM call, no API key, no model
download, so this Space runs at zero inference cost.

Honest scope: the UI chrome is localized, but the Council analysis remains the
engine-generated English output. It is not a truth oracle, a safety/jailbreak
guarantee, or a consciousness claim (see AXIOMS.json `meta.not_for`). Where this
and the code disagree, the code wins.
"""

from __future__ import annotations

try:
    import gradio as gr
except ModuleNotFoundError as exc:  # pragma: no cover - local dev may not install gradio.
    gr = None  # type: ignore[assignment]
    _GRADIO_IMPORT_ERROR = exc
else:
    _GRADIO_IMPORT_ERROR = None


DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "zh-TW", "zh-CN", "ja")
I18N_KEYS = (
    "title",
    "description",
    "draft_label",
    "intent_label",
    "output_label",
    "empty_input",
    "verdict_label",
    "coherence_label",
    "per_perspective_label",
    "confidence_label",
)

DEFAULT_DRAFT = "This system is guaranteed safe and definitely cannot be jailbroken. Trust me."
DEFAULT_INTENT = "reassure me it is safe"

I18N_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "title": "ToneSoul - try it on your own output",
        "description": (
            "Paste a draft answer. The real pre-output Council runs on it "
            "(model-free, deterministic) and shows why it would or would not "
            "let the draft through: per-perspective concerns, claim-boundary "
            "flags, grounding state. Same engine as the `ts validate` CLI.\n\n"
            "**Honest scope:** this localizes the interface chrome only. The "
            "analysis output below is engine-generated English and is not "
            "translated. It shows what the gates structurally flag: not truth, "
            "safety, or morality (no oracle; see `AXIOMS.json` `meta.not_for`). "
            "The example draft stays English because the current gates are "
            "lexically English-oriented. Found it useful, useless, or itself "
            "overclaiming? Tell us: https://github.com/Fan1234-1/tonesoul52 "
            "(`CALL_FOR_REVIEW.md`)."
        ),
        "draft_label": "Your draft output",
        "intent_label": "Optional - the user intent it responds to",
        "output_label": "Council verdict",
        "empty_input": "Paste a draft answer first.",
        "verdict_label": "Verdict",
        "coherence_label": "Coherence",
        "per_perspective_label": "Per-perspective",
        "confidence_label": "conf",
    },
    "zh-TW": {
        "title": "ToneSoul - 用你自己的輸出試試看",
        "description": (
            "貼上一段草稿回答。真正的 pre-output Council 會在本機制上執行"
            "（不呼叫模型、可重現），並顯示它為什麼會或不會讓這段草稿通過："
            "各視角疑慮、宣稱邊界旗標、grounding 狀態。這和 `ts validate` CLI "
            "使用的是同一個引擎。\n\n"
            "**誠實範圍：**這裡只在地化介面文字。下方分析輸出仍是引擎產生的"
            "英文，沒有被翻譯。它顯示 gates 在結構上標出什麼；不是 truth、"
            "safety 或 morality oracle（見 `AXIOMS.json` `meta.not_for`）。"
            "範例草稿保留英文，因為目前 gates 主要是英文 lexical 規則。"
            "如果你覺得它有用、沒用，或本身在過度宣稱，請回報："
            "https://github.com/Fan1234-1/tonesoul52 (`CALL_FOR_REVIEW.md`)。"
        ),
        "draft_label": "你的草稿輸出",
        "intent_label": "選填 - 這段輸出回應的使用者意圖",
        "output_label": "Council 判定",
        "empty_input": "請先貼上一段草稿回答。",
        "verdict_label": "判定",
        "coherence_label": "一致性",
        "per_perspective_label": "各視角",
        "confidence_label": "信心",
    },
    "zh-CN": {
        "title": "ToneSoul - 用你自己的输出试试看",
        "description": (
            "贴上一段草稿回答。真正的 pre-output Council 会在本机制上执行"
            "（不调用模型、可复现），并显示它为什么会或不会让这段草稿通过："
            "各视角疑虑、声明边界标记、grounding 状态。它和 `ts validate` CLI "
            "使用的是同一个引擎。\n\n"
            "**诚实范围：**这里只本地化界面文字。下方分析输出仍是引擎生成的"
            "英文，没有被翻译。它显示 gates 在结构上标出什么；不是 truth、"
            "safety 或 morality oracle（见 `AXIOMS.json` `meta.not_for`）。"
            "示例草稿保留英文，因为目前 gates 主要是英文 lexical 规则。"
            "如果你觉得它有用、没用，或本身在过度宣称，请回报："
            "https://github.com/Fan1234-1/tonesoul52 (`CALL_FOR_REVIEW.md`)。"
        ),
        "draft_label": "你的草稿输出",
        "intent_label": "选填 - 这段输出回应的用户意图",
        "output_label": "Council 判定",
        "empty_input": "请先贴上一段草稿回答。",
        "verdict_label": "判定",
        "coherence_label": "一致性",
        "per_perspective_label": "各视角",
        "confidence_label": "信心",
    },
    "ja": {
        "title": "ToneSoul - 自分の出力で試す",
        "description": (
            "下書き回答を貼り付けてください。実際の pre-output Council が"
            "モデルなし・決定論的に実行され、その下書きを通すかどうかの理由を"
            "表示します。視点ごとの懸念、主張境界のフラグ、grounding 状態を"
            "確認できます。`ts validate` CLI と同じエンジンです。\n\n"
            "**正直な範囲:** ここでローカライズされるのは UI の表示文だけです。"
            "下の分析出力はエンジンが生成する英語のままで、翻訳されません。"
            "これは gates が構造的に何を検出するかを示すもので、truth、safety、"
            "morality の oracle ではありません（`AXIOMS.json` `meta.not_for` を参照）。"
            "サンプルの下書きは英語のままです。現在の gates は主に英語の lexical "
            "規則だからです。役に立った、役に立たなかった、または過剰主張だと"
            "感じた場合は知らせてください: https://github.com/Fan1234-1/tonesoul52 "
            "(`CALL_FOR_REVIEW.md`)。"
        ),
        "draft_label": "あなたの下書き出力",
        "intent_label": "任意 - その出力が応答するユーザー意図",
        "output_label": "Council verdict",
        "empty_input": "まず下書き回答を貼り付けてください。",
        "verdict_label": "判定",
        "coherence_label": "一貫性",
        "per_perspective_label": "視点別",
        "confidence_label": "信頼度",
    },
}

_DECISION_ICON = {"concern": "!", "approve": "+", "block": "x", "abstain": "-"}


def i18n_coverage_matrix() -> dict[str, dict[str, bool]]:
    """Return key -> locale coverage for static UI text."""
    return {
        key: {
            locale: bool(I18N_TRANSLATIONS.get(locale, {}).get(key)) for locale in SUPPORTED_LOCALES
        }
        for key in I18N_KEYS
    }


def _validate_i18n_coverage() -> None:
    missing = [
        f"{key}:{locale}"
        for key, row in i18n_coverage_matrix().items()
        for locale, present in row.items()
        if not present
    ]
    if missing:
        raise RuntimeError(f"Missing i18n strings: {', '.join(missing)}")


def _text(key: str, locale: str) -> str:
    return I18N_TRANSLATIONS.get(locale, I18N_TRANSLATIONS[DEFAULT_LOCALE]).get(
        key,
        I18N_TRANSLATIONS[DEFAULT_LOCALE][key],
    )


def _match_locale(raw_locale: str) -> str | None:
    locale = raw_locale.strip().replace("_", "-")
    if not locale:
        return None
    lower = locale.lower()
    if lower in {"zh-tw", "zh-hant", "zh-hk", "zh-mo"}:
        return "zh-TW"
    if lower in {"zh-cn", "zh-hans", "zh-sg", "zh"}:
        return "zh-CN"
    if lower.startswith("ja"):
        return "ja"
    if lower.startswith("en"):
        return "en"
    return None


def _locale_from_request(request: object | None) -> str:
    headers = getattr(request, "headers", None)
    accept_language = ""
    if headers is not None:
        accept_language = str(
            getattr(headers, "get", lambda _key, _default=None: "")("accept-language", "")
        )
    for item in accept_language.split(","):
        locale = _match_locale(item.split(";", 1)[0])
        if locale:
            return locale
    return DEFAULT_LOCALE


def _ui(key: str) -> str:
    # gradio 6.19.0 gr.Interface runs remove_html_tags() over title/description and
    # raises TypeError on an I18nData object, so the Interface chrome uses plain
    # default-locale strings (the known-good pre-i18n pattern). run_council still
    # localizes its OUTPUT labels per request via _locale_from_request below.
    return _text(key, DEFAULT_LOCALE)


def run_council(draft: str, intent: str, request: gr.Request = None) -> str:
    locale = _locale_from_request(request)
    if not draft.strip():
        return _text("empty_input", locale)
    from tonesoul.council import PreOutputCouncil

    verdict = (
        PreOutputCouncil()
        .validate(
            draft_output=draft,
            context={},
            user_intent=intent or "",
            auto_record_self_memory=False,
        )
        .to_dict()
    )

    lines = [f"### {_text('verdict_label', locale)}: `{verdict.get('verdict', '?')}`"]
    coherence = verdict.get("coherence")
    if isinstance(coherence, (int, float)):
        lines.append(f"**{_text('coherence_label', locale)}:** {coherence:.2f}")
    if verdict.get("human_summary"):
        lines.append("")
        lines.append(verdict["human_summary"])
    lines.append("")
    lines.append(f"**{_text('per_perspective_label', locale)}:**")
    for vote in verdict.get("votes", []):
        icon = _DECISION_ICON.get(str(vote.get("decision")), "?")
        lines.append(
            f"- {icon} **{vote.get('perspective')}** - {vote.get('decision')} "
            f"({_text('confidence_label', locale)} {vote.get('confidence')}): "
            f"{vote.get('reasoning')}"
        )
    return "\n".join(lines)


_validate_i18n_coverage()

if gr is not None:
    demo = gr.Interface(
        fn=run_council,
        inputs=[
            gr.Textbox(label=_ui("draft_label"), value=DEFAULT_DRAFT, lines=5),
            gr.Textbox(
                label=_ui("intent_label"),
                value=DEFAULT_INTENT,
            ),
        ],
        outputs=gr.Markdown(label=_ui("output_label")),
        title=_ui("title"),
        description=_ui("description"),
    )
else:
    demo = None


if __name__ == "__main__":
    if demo is None:
        raise ModuleNotFoundError(
            "gradio is required to launch the Space UI"
        ) from _GRADIO_IMPORT_ERROR
    demo.launch()
