"""Compliance-first outreach draft generator.

The generator deliberately stops at draft creation. It does not publish,
scrape, evade moderation, rotate accounts, or optimize for spam filters.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = Path("docs/outreach/tonesoul_cognitive_map_source.json")
DEFAULT_OUTPUT_DIR = Path("docs/outreach/generated")


@dataclass(frozen=True)
class PlatformProfile:
    slug: str
    name: str
    audience: str
    mode: str
    publish_mode: str
    max_chars: int | None
    requires_disclosure: bool
    requires_evidence_boundary: bool
    automation_policy: str
    context_rules: tuple[str, ...]
    avoid: tuple[str, ...]
    policy_sources: tuple[str, ...]


@dataclass(frozen=True)
class LanguageProfile:
    code: str
    label: str
    title: str
    opening: str
    evidence_boundary: str
    concept_intro: str
    concept_bullets: tuple[str, ...]
    comparison_intro: str
    closing: str
    disclosure: str
    social: str
    cta: str


@dataclass(frozen=True)
class Draft:
    platform: str
    language: str
    title: str
    body: str
    metadata: dict[str, Any]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    @property
    def status(self) -> str:
        if self.blockers:
            return "blocked"
        if self.warnings:
            return "review_required"
        return "ready_for_human_review"


LANGUAGES: dict[str, LanguageProfile] = {
    "zh-TW": LanguageProfile(
        code="zh-TW",
        label="繁體中文",
        title="ToneSoul 語魂系統認知地圖：把分歧、記憶與責任做成 AI 架構",
        opening=(
            "ToneSoul 不是在宣稱 AI 已經有靈魂，而是在問一個工程問題："
            "如果 AI 要對自己的話負責，系統裡需要哪些可檢查的結構？"
            "這篇文章把語魂整理成一張認知地圖，方便外部社群比較、質疑與延伸。"
        ),
        evidence_boundary=(
            "Evidence boundary: 這是公開架構與概念原型的整理，不是安全性證明、"
            "意識宣稱，也不是已完成的生產級保證。"
        ),
        concept_intro="語魂的核心不是單一模組，而是一組把「分歧保留下來」的設計約束：",
        concept_bullets=(
            "TensionTensor：把事實、邏輯、倫理阻力與語境權重分開，而不是把爭議壓成一個分數。",
            "Council deliberation：讓 Guardian、Analyst、Critic、Advocate 等視角留下可審計的分歧軌跡。",
            "Memory integration：把反覆出現的張力沉澱為系統性格，而不是只留下最近一輪反應。",
            "SelfCommit：把承諾寫成可回看、可被未來輸出追責的語義痕跡。",
        ),
        comparison_intro="放在現有 AI safety 語境裡，語魂比較接近這幾條研究線的交叉點：",
        closing=(
            "我希望得到的不是掌聲，而是精準的反駁：哪些部分只是隱喻，哪些部分能成為"
            "可測試的工程約束？如果分歧本身被當成狀態保存，AI governance 會不會更誠實？"
        ),
        disclosure="AI-use disclosure: 本稿由 AI 協助整理，發布前應由人類作者逐段審閱與負責。",
        social=(
            "ToneSoul 的核心問題：如果 AI 要對自己的話負責，系統裡需要哪些可檢查的結構？"
            "我把它整理成「分歧、記憶、承諾」三條線的認知地圖。"
        ),
        cta="歡迎指出薄弱處，尤其是可以被測試或被反例推翻的地方。",
    ),
    "zh-CN": LanguageProfile(
        code="zh-CN",
        label="简体中文",
        title="ToneSoul 语魂系统认知地图：把分歧、记忆与责任做成 AI 架构",
        opening=(
            "ToneSoul 并不是在宣称 AI 已经有灵魂，而是在提出一个工程问题："
            "如果 AI 要对自己的话负责，系统内部需要哪些可检查的结构？"
            "这篇文章把语魂整理成一张认知地图，方便外部社区比较、质疑和延伸。"
        ),
        evidence_boundary=(
            "Evidence boundary: 这是公开架构与概念原型的整理，不是安全性证明、"
            "意识宣称，也不是已完成的生产级保证。"
        ),
        concept_intro="语魂的核心不是单一模块，而是一组把“分歧保留下来”的设计约束：",
        concept_bullets=(
            "TensionTensor：把事实、逻辑、伦理阻力与语境权重分开，而不是把争议压成一个分数。",
            "Council deliberation：让 Guardian、Analyst、Critic、Advocate 等视角留下可审计的分歧轨迹。",
            "Memory integration：把反复出现的张力沉淀为系统性格，而不是只留下最近一轮反应。",
            "SelfCommit：把承诺写成可回看、可被未来输出追责的语义痕迹。",
        ),
        comparison_intro="放在现有 AI safety 语境里，语魂比较接近这几条研究线的交叉点：",
        closing=(
            "我希望得到的不是掌声，而是精确的反驳：哪些部分只是隐喻，哪些部分能成为"
            "可测试的工程约束？如果分歧本身被当成状态保存，AI governance 会不会更诚实？"
        ),
        disclosure="AI-use disclosure: 本稿由 AI 协助整理，发布前应由人类作者逐段审阅并负责。",
        social=(
            "ToneSoul 的核心问题：如果 AI 要对自己的话负责，系统里需要哪些可检查的结构？"
            "我把它整理成“分歧、记忆、承诺”三条线的认知地图。"
        ),
        cta="欢迎指出薄弱处，尤其是可以被测试或被反例推翻的地方。",
    ),
    "en": LanguageProfile(
        code="en",
        label="English",
        title="ToneSoul as a cognitive map for AI governance: disagreement, memory, and semantic responsibility",
        opening=(
            "ToneSoul is not a claim that AI already has a soul. It is an engineering question: "
            "if an AI system should be accountable for what it says, what inspectable structures "
            "must exist inside the system? This draft frames ToneSoul as a cognitive map that can "
            "be compared, criticized, and improved by adjacent AI safety communities."
        ),
        evidence_boundary=(
            "Evidence boundary: this is a public architecture and conceptual prototype summary. "
            "It is not a safety proof, a consciousness claim, or a production-grade guarantee."
        ),
        concept_intro=(
            "ToneSoul is not one module. It is a set of design constraints for preserving "
            "disagreement instead of flattening it away:"
        ),
        concept_bullets=(
            "TensionTensor separates factual, logical, and ethical resistance from contextual weight instead of compressing conflict into one score.",
            "Council deliberation leaves an auditable trail across Guardian, Analyst, Critic, Advocate, and related perspectives.",
            "Memory integration lets recurring tensions accumulate into system character rather than only shaping the latest response.",
            "SelfCommit turns commitments into reviewable traces that future outputs can be held against.",
        ),
        comparison_intro=(
            "In existing AI safety language, ToneSoul sits near the intersection of these lines of work:"
        ),
        closing=(
            "The useful response is not applause. It is precise criticism: which parts are only "
            "metaphor, and which parts can become testable engineering constraints? If unresolved "
            "disagreement is preserved as state, AI governance may become more honest."
        ),
        disclosure="AI-use disclosure: this draft was prepared with AI assistance and should be reviewed line by line by the human author before publication.",
        social=(
            "ToneSoul asks a concrete governance question: if an AI should be accountable for what "
            "it says, what inspectable structures must exist inside the system? I map it through "
            "disagreement, memory, and commitment."
        ),
        cta="Critique is welcome, especially where the idea can be tested or falsified.",
    ),
    "ja": LanguageProfile(
        code="ja",
        label="Japanese",
        title="ToneSoul の認知地図：分岐、記憶、意味上の責任を AI アーキテクチャにする",
        opening=(
            "ToneSoul は、AI にすでに魂があると主張するものではありません。問いはもっと工学的です。"
            "AI が自分の発言に責任を持つべきだとしたら、システム内部にどのような検査可能な構造が必要でしょうか。"
            "この草稿は、ToneSoul を外部コミュニティが比較し、批判し、改良できる認知地図として整理します。"
        ),
        evidence_boundary=(
            "Evidence boundary: これは公開アーキテクチャと概念プロトタイプの整理であり、"
            "安全性の証明、意識の主張、本番品質の保証ではありません。"
        ),
        concept_intro="ToneSoul は単一のモジュールではなく、対立を消さずに保持するための設計制約の集合です：",
        concept_bullets=(
            "TensionTensor は、事実・論理・倫理の抵抗と文脈重みを分け、対立を単一スコアに押し込めない。",
            "Council deliberation は、Guardian、Analyst、Critic、Advocate などの視点差を監査可能な履歴として残す。",
            "Memory integration は、反復する張力を単なる直近応答ではなく、システムの性格として沈殿させる。",
            "SelfCommit は、約束を後から照合できる意味的な痕跡として残す。",
        ),
        comparison_intro="既存の AI safety の文脈では、ToneSoul は次の研究線の交差点に近いものです：",
        closing=(
            "必要なのは称賛ではなく、精密な批判です。どこが比喩にすぎず、どこがテスト可能な"
            "工学制約になり得るのか。未解決の分岐を状態として保持することで、AI governance はより誠実になるかもしれません。"
        ),
        disclosure="AI-use disclosure: この草稿は AI の支援で作成されており、公開前に人間の著者が一文ずつ確認して責任を負う必要があります。",
        social=(
            "ToneSoul の問いは単純です。AI が自分の発言に責任を持つべきなら、内部にどんな検査可能な構造が必要か。"
            "私はそれを分岐、記憶、約束の三つで整理しました。"
        ),
        cta="特に、テスト可能または反証可能な弱点への批判を歓迎します。",
    ),
    "ko": LanguageProfile(
        code="ko",
        label="Korean",
        title="ToneSoul 인지 지도: 분기, 기억, 의미적 책임을 AI 구조로 만들기",
        opening=(
            "ToneSoul 은 AI 에 이미 영혼이 있다고 주장하는 프로젝트가 아닙니다. 질문은 더 공학적입니다. "
            "AI 가 자신의 말에 책임을 져야 한다면, 시스템 내부에는 어떤 점검 가능한 구조가 필요할까요? "
            "이 초안은 ToneSoul 을 외부 커뮤니티가 비교하고 비판하고 개선할 수 있는 인지 지도로 정리합니다."
        ),
        evidence_boundary=(
            "Evidence boundary: 이 글은 공개 아키텍처와 개념 프로토타입의 요약입니다. "
            "안전성 증명, 의식 주장, 또는 프로덕션 수준 보장이 아닙니다."
        ),
        concept_intro="ToneSoul 은 하나의 모듈이 아니라, 불일치를 지우지 않고 보존하기 위한 설계 제약의 묶음입니다:",
        concept_bullets=(
            "TensionTensor 는 사실, 논리, 윤리적 저항과 맥락 가중치를 분리해 갈등을 하나의 점수로 압축하지 않는다.",
            "Council deliberation 은 Guardian, Analyst, Critic, Advocate 등의 관점 차이를 감사 가능한 흔적으로 남긴다.",
            "Memory integration 은 반복되는 장력을 최근 응답이 아니라 시스템 성격으로 축적한다.",
            "SelfCommit 은 약속을 미래 출력과 대조할 수 있는 의미적 흔적으로 만든다.",
        ),
        comparison_intro="기존 AI safety 언어로 보면 ToneSoul 은 다음 연구 흐름들의 교차점에 가깝습니다:",
        closing=(
            "필요한 것은 박수가 아니라 정밀한 비판입니다. 무엇이 은유에 머물고, 무엇이 테스트 가능한 "
            "공학 제약이 될 수 있을까요? 해결되지 않은 불일치를 상태로 보존하면 AI governance 는 더 정직해질 수 있습니다."
        ),
        disclosure="AI-use disclosure: 이 초안은 AI 의 도움으로 작성되었으며, 공개 전 인간 작성자가 문장별로 검토하고 책임져야 합니다.",
        social=(
            "ToneSoul 의 질문은 구체적입니다. AI 가 자신의 말에 책임을 져야 한다면 내부에는 어떤 점검 가능한 구조가 필요할까요? "
            "저는 이를 불일치, 기억, 약속의 지도로 정리했습니다."
        ),
        cta="특히 테스트 가능하거나 반증 가능한 약점에 대한 비판을 환영합니다.",
    ),
    "es": LanguageProfile(
        code="es",
        label="Spanish",
        title="ToneSoul como mapa cognitivo para gobernanza de IA: desacuerdo, memoria y responsabilidad semantica",
        opening=(
            "ToneSoul no afirma que la IA ya tenga alma. La pregunta es de ingenieria: "
            "si un sistema de IA debe responder por lo que dice, que estructuras inspeccionables "
            "deben existir dentro del sistema? Este borrador presenta ToneSoul como un mapa cognitivo "
            "que otras comunidades de seguridad de IA pueden comparar, criticar y mejorar."
        ),
        evidence_boundary=(
            "Evidence boundary: este texto resume una arquitectura publica y un prototipo conceptual. "
            "No es una prueba de seguridad, una afirmacion de conciencia ni una garantia de produccion."
        ),
        concept_intro="ToneSoul no es un solo modulo. Es un conjunto de restricciones de diseno para preservar el desacuerdo:",
        concept_bullets=(
            "TensionTensor separa resistencia factual, logica y etica del peso contextual, en vez de comprimir el conflicto en una sola puntuacion.",
            "Council deliberation deja una traza auditable entre perspectivas como Guardian, Analyst, Critic y Advocate.",
            "Memory integration permite que las tensiones recurrentes se acumulen como caracter del sistema, no solo como respuesta reciente.",
            "SelfCommit convierte compromisos en rastros revisables contra los que se pueden comparar salidas futuras.",
        ),
        comparison_intro="En el lenguaje actual de AI safety, ToneSoul esta cerca de la interseccion de estas lineas:",
        closing=(
            "Lo util no es el aplauso, sino la critica precisa: que partes son solo metafora y que partes "
            "pueden convertirse en restricciones de ingenieria comprobables?"
        ),
        disclosure="AI-use disclosure: este borrador fue preparado con ayuda de IA y debe ser revisado linea por linea por la autora o el autor humano antes de publicarse.",
        social=(
            "ToneSoul hace una pregunta concreta: si una IA debe responder por lo que dice, que estructuras inspeccionables "
            "deben existir dentro del sistema? Lo mapeo mediante desacuerdo, memoria y compromiso."
        ),
        cta="La critica es bienvenida, sobre todo donde la idea pueda probarse o refutarse.",
    ),
    "fr": LanguageProfile(
        code="fr",
        label="French",
        title="ToneSoul comme carte cognitive de gouvernance IA : desaccord, memoire et responsabilite semantique",
        opening=(
            "ToneSoul ne pretend pas que l'IA possede deja une ame. La question est d'abord technique : "
            "si un systeme d'IA doit repondre de ce qu'il dit, quelles structures inspectables doivent exister "
            "dans le systeme ? Ce brouillon presente ToneSoul comme une carte cognitive que les communautes "
            "voisines de securite IA peuvent comparer, critiquer et ameliorer."
        ),
        evidence_boundary=(
            "Evidence boundary: ce texte resume une architecture publique et un prototype conceptuel. "
            "Ce n'est ni une preuve de surete, ni une affirmation de conscience, ni une garantie de production."
        ),
        concept_intro="ToneSoul n'est pas un module unique. C'est un ensemble de contraintes de conception pour conserver le desaccord :",
        concept_bullets=(
            "TensionTensor separe les resistances factuelles, logiques et ethiques du poids contextuel au lieu de reduire le conflit a un seul score.",
            "Council deliberation laisse une trace auditable entre Guardian, Analyst, Critic, Advocate et d'autres perspectives.",
            "Memory integration fait sedimenter les tensions recurrentes en caractere systemique, au lieu de ne garder que la derniere reponse.",
            "SelfCommit transforme les engagements en traces revisables auxquelles les sorties futures peuvent etre comparees.",
        ),
        comparison_intro="Dans le langage actuel de l'AI safety, ToneSoul se situe pres de l'intersection de ces axes :",
        closing=(
            "La reponse utile n'est pas l'approbation, mais la critique precise : quelles parties restent "
            "metaphoriques et lesquelles peuvent devenir des contraintes techniques testables ?"
        ),
        disclosure="AI-use disclosure: ce brouillon a ete prepare avec l'aide de l'IA et doit etre relu ligne par ligne par l'auteur humain avant publication.",
        social=(
            "ToneSoul pose une question concrete : si une IA doit repondre de ce qu'elle dit, quelles structures inspectables "
            "doivent exister dans le systeme ? Je le cartographie par desaccord, memoire et engagement."
        ),
        cta="Les critiques sont bienvenues, surtout la ou l'idee peut etre testee ou refutee.",
    ),
    "de": LanguageProfile(
        code="de",
        label="German",
        title="ToneSoul als kognitive Karte fur KI-Governance: Dissens, Gedachtnis und semantische Verantwortung",
        opening=(
            "ToneSoul behauptet nicht, dass KI bereits eine Seele hat. Die Frage ist technischer: "
            "Wenn ein KI-System fur seine Aussagen verantwortlich sein soll, welche inspizierbaren Strukturen "
            "mussen im System vorhanden sein? Dieser Entwurf beschreibt ToneSoul als kognitive Karte, die "
            "benachbarte AI-Safety-Communities vergleichen, kritisieren und verbessern konnen."
        ),
        evidence_boundary=(
            "Evidence boundary: Dieser Text fasst eine offentliche Architektur und einen konzeptionellen Prototyp zusammen. "
            "Er ist kein Sicherheitsbeweis, keine Bewusstseinsbehauptung und keine Produktionsgarantie."
        ),
        concept_intro="ToneSoul ist kein einzelnes Modul. Es ist ein Satz von Designbedingungen, um Dissens nicht wegzuglatten:",
        concept_bullets=(
            "TensionTensor trennt faktischen, logischen und ethischen Widerstand vom Kontextgewicht, statt Konflikt in eine einzelne Zahl zu pressen.",
            "Council deliberation hinterlasst eine auditierbare Spur uber Guardian, Analyst, Critic, Advocate und verwandte Perspektiven hinweg.",
            "Memory integration lasst wiederkehrende Spannungen zu Systemcharakter sedimentieren, statt nur die letzte Antwort zu pragen.",
            "SelfCommit macht Zusagen zu uberprufbaren Spuren, an denen spatere Ausgaben gemessen werden konnen.",
        ),
        comparison_intro="In der Sprache der AI Safety liegt ToneSoul nahe am Schnittpunkt dieser Forschungsrichtungen:",
        closing=(
            "Nutzlich ist nicht Applaus, sondern prazise Kritik: Welche Teile sind nur Metaphern, und welche "
            "konnen zu testbaren technischen Bedingungen werden?"
        ),
        disclosure="AI-use disclosure: Dieser Entwurf wurde mit KI-Unterstutzung vorbereitet und sollte vor der Veroffentlichung Zeile fur Zeile von einem menschlichen Autor gepruft werden.",
        social=(
            "ToneSoul stellt eine konkrete Governance-Frage: Wenn KI fur ihre Aussagen verantwortlich sein soll, "
            "welche inspizierbaren Strukturen mussen im System existieren? Ich kartiere es uber Dissens, Gedachtnis und Verpflichtung."
        ),
        cta="Kritik ist willkommen, besonders dort, wo die Idee testbar oder falsifizierbar ist.",
    ),
}


PLATFORMS: dict[str, PlatformProfile] = {
    "lesswrong": PlatformProfile(
        slug="lesswrong",
        name="LessWrong",
        audience="AI alignment and rationality readers who expect explicit claims and objections.",
        mode="alignment",
        publish_mode="manual_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual post only; do not use this as promotion-first content.",
        context_rules=(
            "Lead with the research question, not the brand.",
            "Make falsifiable claims and separate metaphor from mechanism.",
            "Invite objections rather than broad approval.",
        ),
        avoid=(
            "launch language",
            "sentience claims",
            "marketing slogans",
            "uncited broad safety claims",
        ),
        policy_sources=(
            "https://www.alignmentforum.org/posts/Yp2vYb4zHXEeoTkJc/welcome-and-faq",
            "https://www.lesswrong.com/posts/FoiiRDC3EhjHx7ayY/introducing-the-ai-alignment-forum-faq",
        ),
    ),
    "alignment-forum": PlatformProfile(
        slug="alignment-forum",
        name="AI Alignment Forum",
        audience="Specialist alignment researchers; non-members normally go through review or LessWrong promotion.",
        mode="alignment",
        publish_mode="manual_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual submission or LessWrong path only; expect review.",
        context_rules=(
            "Use only for the most technical version.",
            "State open problems and what evidence would change the design.",
            "Avoid introductory outreach framing.",
        ),
        avoid=(
            "general philosophy without technical claims",
            "call-to-action promotion",
            "claims above current evidence",
        ),
        policy_sources=(
            "https://www.alignmentforum.org/posts/Yp2vYb4zHXEeoTkJc/welcome-and-faq",
            "https://www.lesswrong.com/posts/FoiiRDC3EhjHx7ayY/introducing-the-ai-alignment-forum-faq",
        ),
    ),
    "ea-forum": PlatformProfile(
        slug="ea-forum",
        name="EA Forum",
        audience="Readers evaluating practical relevance, cause prioritization, and AI safety community value.",
        mode="community",
        publish_mode="manual_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual crosspost or linkpost with summary.",
        context_rules=(
            "Explain why the post is relevant to AI safety or governance.",
            "Prefer linkpost or crosspost with clear summary.",
            "Make uncertainty and cost-of-attention explicit.",
        ),
        avoid=(
            "community recruitment pressure",
            "duplicated crossposts without platform-specific summary",
            "overstated impact claims",
        ),
        policy_sources=(
            "https://forum.effectivealtruism.org/posts/8yDsenRQhNF4HEDwu/link-posting-is-an-act-of-community-service",
        ),
    ),
    "huggingface": PlatformProfile(
        slug="huggingface",
        name="Hugging Face Blog",
        audience="Machine-learning builders who expect technical originality and implementation detail.",
        mode="technical",
        publish_mode="manual_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual blog submission only; must be original and technical.",
        context_rules=(
            "Center architecture, reproducible examples, and limits.",
            "Avoid advertising paid or external solutions.",
            "Include diagrams or code references before publication.",
        ),
        avoid=(
            "low-technical overview",
            "LLM-generated article without scrutiny",
            "paid-solution advertising",
        ),
        policy_sources=("https://huggingface.co/blog-explorers",),
    ),
    "devto": PlatformProfile(
        slug="devto",
        name="DEV Community",
        audience="Developers who want practical implementation patterns and transparent AI assistance.",
        mode="developer",
        publish_mode="manual_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual article post; disclose AI assistance and check accuracy.",
        context_rules=(
            "Frame as an implementation pattern.",
            "Show how to evaluate or test the idea.",
            "Disclose AI assistance plainly.",
        ),
        avoid=(
            "unchecked generated content",
            "thin listicle format",
            "tool promotion without implementation value",
        ),
        policy_sources=("https://dev.to/devteam/guidelines-for-ai-assisted-articles-on-dev-17n6",),
    ),
    "substack": PlatformProfile(
        slug="substack",
        name="Substack",
        audience="Newsletter readers who expect editorial substance and a consistent author voice.",
        mode="editorial",
        publish_mode="manual_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual publication; not for conventional marketing or SEO-only distribution.",
        context_rules=(
            "Use as the canonical longform home.",
            "Keep the author voice and avoid generic marketing.",
            "Do not import or email anyone without opt-in.",
        ),
        avoid=(
            "SEO-only copy",
            "traffic-funnel framing",
            "spammy comments or Notes",
        ),
        policy_sources=("https://substack.com/content",),
    ),
    "hacker-news": PlatformProfile(
        slug="hacker-news",
        name="Hacker News",
        audience="Technical readers; original source submissions only, minimal self-promotion.",
        mode="aggregator",
        publish_mode="manual_only_no_generated_comments",
        max_chars=None,
        requires_disclosure=False,
        requires_evidence_boundary=False,
        automation_policy="Submit original source manually; do not paste AI-generated comments.",
        context_rules=(
            "Use the original source title or a plain title.",
            "Do not solicit votes or comments.",
            "Only discuss in your own words if readers ask.",
        ),
        avoid=(
            "generated comments",
            "editorialized titles",
            "promotion-first posting",
            "delete-and-repost behavior",
        ),
        policy_sources=("https://news.ycombinator.com/newsguidelines.html",),
    ),
    "reddit": PlatformProfile(
        slug="reddit",
        name="Reddit",
        audience="Subreddit-specific communities; rules vary and self-promotion is often unwelcome.",
        mode="social",
        publish_mode="manual_review",
        max_chars=1200,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual, one community at a time; check subreddit rules first.",
        context_rules=(
            "Adapt to one subreddit, not many.",
            "Lead with a question or critique request.",
            "Do not use sockpuppets, vote requests, or repeated link drops.",
        ),
        avoid=(
            "cross-subreddit duplicate posting",
            "generic link dump",
            "undisclosed affiliation",
        ),
        policy_sources=(
            "https://www.reddit.com/r/reddit.com/wiki/selfpromotion/",
            "https://www.reddit.com/r/modnews/comments/2oamgp/moderators_clarifications_around_our_101/",
        ),
    ),
    "bluesky": PlatformProfile(
        slug="bluesky",
        name="Bluesky",
        audience="Short-form social readers; transparency and non-disruptive behavior matter.",
        mode="social",
        publish_mode="manual_or_api_with_constraints",
        max_chars=300,
        requires_disclosure=False,
        requires_evidence_boundary=False,
        automation_policy="API possible, but this tool only drafts; avoid repeated or disruptive posts.",
        context_rules=(
            "Use one concise claim and one link.",
            "Do not mass-mention accounts.",
            "Do not repeat substantially similar posts.",
        ),
        avoid=(
            "bulk replies",
            "engagement manipulation",
            "undisclosed commercial content",
        ),
        policy_sources=("https://bsky.social/about/support/community-guidelines",),
    ),
    "mastodon": PlatformProfile(
        slug="mastodon",
        name="Mastodon",
        audience="Instance-specific fediverse readers; norms vary by server.",
        mode="social",
        publish_mode="manual_or_api_with_constraints",
        max_chars=500,
        requires_disclosure=False,
        requires_evidence_boundary=False,
        automation_policy="API possible depending on instance rules; this tool only drafts.",
        context_rules=(
            "Respect the target instance norms.",
            "Avoid thread flooding.",
            "Use content warnings if needed.",
        ),
        avoid=(
            "cross-instance spam",
            "duplicate automated posts",
            "unlabeled bot behavior",
        ),
        policy_sources=("https://docs.joinmastodon.org/methods/statuses/",),
    ),
    "x": PlatformProfile(
        slug="x",
        name="X",
        audience="Short-form social readers; automation rules are strict around spam and duplication.",
        mode="social",
        publish_mode="manual_or_api_with_constraints",
        max_chars=280,
        requires_disclosure=False,
        requires_evidence_boundary=False,
        automation_policy="API possible only within X rules; no duplicate/similar automated posts.",
        context_rules=(
            "One concise claim, no trending-topic hijack.",
            "Do not post duplicative variants across accounts.",
            "Avoid misleading links.",
        ),
        avoid=(
            "duplicate automated posts",
            "trend manipulation",
            "engagement bait",
        ),
        policy_sources=("https://help.x.com/en/rules-and-policies/x-automation",),
    ),
    "linkedin": PlatformProfile(
        slug="linkedin",
        name="LinkedIn",
        audience="Professional readers; generic AI thought-leadership performs poorly and may be demoted.",
        mode="social",
        publish_mode="manual_only",
        max_chars=1300,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Manual copy only; LinkedIn API terms prohibit using APIs to automate posting.",
        context_rules=(
            "Use a concrete practitioner framing.",
            "Avoid generic thought-leadership cadence.",
            "Do not automate posting through the API.",
        ),
        avoid=(
            "automated posting",
            "engagement bait",
            "generic AI-generated prose",
        ),
        policy_sources=(
            "https://www.linkedin.com/legal/l/api-terms-of-use",
            "https://learn.microsoft.com/en-us/linkedin/compliance/integrations/shares/ugc-post-api",
        ),
    ),
    "arxiv": PlatformProfile(
        slug="arxiv",
        name="arXiv",
        audience="Academic readers; CS review/position papers now require prior peer review.",
        mode="academic",
        publish_mode="do_not_post_without_peer_review",
        max_chars=None,
        requires_disclosure=True,
        requires_evidence_boundary=True,
        automation_policy="Do not submit generated review/position material without accepted peer review.",
        context_rules=(
            "Only use after producing original research or peer-reviewed position work.",
            "Verify every citation manually.",
            "Disclose AI assistance according to venue rules.",
        ),
        avoid=(
            "survey or position paper without peer review",
            "hallucinated references",
            "unchecked LLM text",
        ),
        policy_sources=(
            "https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/",
            "https://arxiv.org/category_taxonomy",
        ),
    ),
}


COMPARISON_NOTES = (
    (
        "Constitutional AI",
        "principle-based self-critique and revision",
        "https://arxiv.org/abs/2212.08073",
    ),
    (
        "AI safety via debate",
        "adversarial argumentation as scalable oversight",
        "https://arxiv.org/abs/1805.00899",
    ),
    (
        "Reflexion",
        "language agents improving through verbal memory",
        "https://arxiv.org/abs/2303.11366",
    ),
    (
        "Generative Agents",
        "memory, reflection, and planning for believable agents",
        "https://arxiv.org/abs/2304.03442",
    ),
)


BLOCKED_CLAIM_PATTERNS = {
    r"\bguaranteed\b": "Avoid guarantees. Use bounded evidence language.",
    r"\bproven safe\b": "Do not claim proven safety.",
    r"\bproduction[- ]ready\b": "Do not claim production readiness without matching evidence.",
    r"\bsentient\b": "Do not imply machine sentience.",
    r"\bconscious\b": "Do not imply machine consciousness.",
    r"不會被擋": "Do not promise platform acceptance; frame as compliance-oriented drafting.",
    r"保证通过": "Do not promise platform acceptance.",
    r"保證通過": "Do not promise platform acceptance.",
}


def load_source(path: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def known_platforms() -> tuple[str, ...]:
    return tuple(sorted(PLATFORMS))


def known_languages() -> tuple[str, ...]:
    return tuple(LANGUAGES)


def _language(code: str) -> LanguageProfile:
    try:
        return LANGUAGES[code]
    except KeyError as exc:
        known = ", ".join(known_languages())
        raise ValueError(f"Unsupported language '{code}'. Known languages: {known}") from exc


def _platform(slug: str) -> PlatformProfile:
    try:
        return PLATFORMS[slug]
    except KeyError as exc:
        known = ", ".join(known_platforms())
        raise ValueError(f"Unsupported platform '{slug}'. Known platforms: {known}") from exc


def _project_name(source: dict[str, Any]) -> str:
    return str(source.get("project_name") or "ToneSoul")


def _canonical_url(source: dict[str, Any]) -> str | None:
    value = source.get("canonical_url")
    return str(value) if value else None


def _comparison_lines() -> list[str]:
    return [f"- {name}: {summary}. Source: {url}" for name, summary, url in COMPARISON_NOTES]


def _platform_context(profile: PlatformProfile) -> str:
    lines = [
        "## Platform context",
        f"- Platform: {profile.name}",
        f"- Audience: {profile.audience}",
        f"- Publish mode: {profile.publish_mode}",
        f"- Automation policy: {profile.automation_policy}",
        "- Context rules:",
    ]
    lines.extend(f"  - {rule}" for rule in profile.context_rules)
    lines.append("- Avoid:")
    lines.extend(f"  - {item}" for item in profile.avoid)
    return "\n".join(lines)


def _longform_body(
    source: dict[str, Any], profile: PlatformProfile, language: LanguageProfile
) -> str:
    project = _project_name(source)
    canonical_url = _canonical_url(source)
    body = [
        language.opening,
        "",
        language.evidence_boundary,
        "",
        _platform_context(profile),
        "",
        "## Cognitive map",
        language.concept_intro,
        "",
    ]
    body.extend(f"- {bullet}" for bullet in language.concept_bullets)
    body.extend(
        [
            "",
            "## Adjacent work",
            language.comparison_intro,
            "",
            *_comparison_lines(),
            "",
            "## Publication stance",
            (
                f"This draft should describe {project} as a public governance architecture, "
                "not as a finished safety product. Keep claims bounded to public artifacts, "
                "tests, and conceptual design notes."
            ),
            "",
        ]
    )

    if profile.mode == "alignment":
        body.extend(
            [
                "## Open questions",
                "- Which parts are measurable mechanisms rather than metaphors?",
                "- What would count as a failed prediction for tension-preserving governance?",
                "- Does preserving disagreement improve auditability, or does it only create more text?",
                "",
            ]
        )
    elif profile.mode == "technical":
        body.extend(
            [
                "## Technical expansion needed before posting",
                "- Add a minimal runnable example or architecture diagram.",
                "- Link to public code only; do not include private evolution prompts or memory data.",
                "- Mark every claim as prototype, tested, or aspirational.",
                "",
            ]
        )
    elif profile.mode == "developer":
        body.extend(
            [
                "## Developer evaluation path",
                "- Start with a narrow agent workflow.",
                "- Preserve disagreement as structured state.",
                "- Add tests that fail when claims outrun observable behavior.",
                "",
            ]
        )
    elif profile.mode == "community":
        body.extend(
            [
                "## Why this may matter to this community",
                "- It treats governance as an inspectable system design problem.",
                "- It gives disagreement a place to live instead of hiding it in final prose.",
                "- It invites critique before making stronger claims.",
                "",
            ]
        )

    body.extend([language.closing, "", language.disclosure])
    if canonical_url:
        body.extend(["", f"Canonical source: {canonical_url}"])
    return "\n".join(body).strip() + "\n"


def _social_body(
    source: dict[str, Any], profile: PlatformProfile, language: LanguageProfile
) -> str:
    canonical_url = _canonical_url(source)
    parts = [language.social]
    if profile.requires_evidence_boundary:
        parts.append(language.evidence_boundary)
    parts.append(language.cta)
    if profile.requires_disclosure:
        parts.append(language.disclosure)
    if canonical_url:
        parts.append(canonical_url)
    body = "\n\n".join(parts).strip()

    if profile.max_chars and len(body) > profile.max_chars:
        # Keep the validator honest by producing a best-effort short form instead
        # of hiding that the platform needs manual editing.
        compact = language.social
        if canonical_url:
            compact = f"{compact}\n{canonical_url}"
        body = compact[: profile.max_chars].rstrip()
    return body + "\n"


def _aggregator_body(
    source: dict[str, Any], profile: PlatformProfile, language: LanguageProfile
) -> str:
    canonical_url = _canonical_url(source) or "[add original source URL]"
    lines = [
        "Manual submission packet only.",
        "",
        f"Suggested plain title: {language.title}",
        f"Original source URL: {canonical_url}",
        "",
        "Do not paste generated explanatory comments. If readers ask questions, answer personally in your own words.",
        "",
        _platform_context(profile),
    ]
    return "\n".join(lines).strip() + "\n"


def _academic_body(
    source: dict[str, Any], profile: PlatformProfile, language: LanguageProfile
) -> str:
    return (
        "\n".join(
            [
                "Do not submit this as-is.",
                "",
                language.evidence_boundary,
                "",
                "This platform profile is intentionally blocked unless there is original research or accepted peer-reviewed position work.",
                "Use this generator only to prepare a private outline for a future paper, then verify every citation manually.",
                "",
                _platform_context(profile),
                "",
                language.disclosure,
            ]
        ).strip()
        + "\n"
    )


def render_body(source: dict[str, Any], profile: PlatformProfile, language: LanguageProfile) -> str:
    if profile.mode == "social":
        return _social_body(source, profile, language)
    if profile.mode == "aggregator":
        return _aggregator_body(source, profile, language)
    if profile.mode == "academic":
        return _academic_body(source, profile, language)
    return _longform_body(source, profile, language)


def validate_draft(
    title: str, body: str, profile: PlatformProfile
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    warnings: list[str] = []
    blockers: list[str] = []
    text = f"{title}\n{body}"

    for pattern, reason in BLOCKED_CLAIM_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            blockers.append(reason)

    if profile.publish_mode.startswith("do_not_post"):
        blockers.append(f"{profile.name} profile is blocked: {profile.publish_mode}.")

    if profile.max_chars is not None and len(body) > profile.max_chars:
        blockers.append(
            f"{profile.name} draft is {len(body)} chars, above the {profile.max_chars} char profile limit."
        )

    if profile.requires_disclosure and "AI-use disclosure:" not in body:
        blockers.append("Required AI-use disclosure is missing.")

    if profile.requires_evidence_boundary and "Evidence boundary:" not in body:
        blockers.append("Required evidence boundary is missing.")

    if profile.mode == "social" and body.count("#") > 3:
        warnings.append("Social drafts should not rely on many hashtags.")

    if profile.publish_mode in {"manual_only", "manual_only_no_generated_comments"}:
        warnings.append(f"{profile.name} should be handled manually: {profile.automation_policy}")

    if profile.publish_mode == "manual_review":
        warnings.append(f"{profile.name} needs human review before posting.")

    if profile.publish_mode == "manual_or_api_with_constraints":
        warnings.append(
            f"{profile.name} may allow API posting, but this tool only drafts and does not publish."
        )

    return tuple(warnings), tuple(dict.fromkeys(blockers))


def build_draft(
    source: dict[str, Any],
    platform_slug: str,
    language_code: str,
) -> Draft:
    profile = _platform(platform_slug)
    language = _language(language_code)
    title = language.title
    body = render_body(source, profile, language)
    warnings, blockers = validate_draft(title, body, profile)
    metadata = {
        "platform": asdict(profile),
        "language": asdict(language),
        "policy_sources": profile.policy_sources,
        "publish_mode": profile.publish_mode,
        "automation_policy": profile.automation_policy,
        "char_count": len(body),
        "word_count": len(re.findall(r"\S+", body)),
    }
    return Draft(
        platform=platform_slug,
        language=language_code,
        title=title,
        body=body,
        metadata=metadata,
        warnings=warnings,
        blockers=blockers,
    )


def render_markdown(draft: Draft) -> str:
    policy_sources = "\n".join(f"  - {url}" for url in draft.metadata["policy_sources"])
    warnings = "\n".join(f"  - {item}" for item in draft.warnings) or "  - none"
    blockers = "\n".join(f"  - {item}" for item in draft.blockers) or "  - none"
    frontmatter = (
        "---\n"
        f"platform: {draft.platform}\n"
        f"language: {draft.language}\n"
        f"status: {draft.status}\n"
        f"publish_mode: {draft.metadata['publish_mode']}\n"
        f"char_count: {draft.metadata['char_count']}\n"
        f"word_count: {draft.metadata['word_count']}\n"
        "policy_sources:\n"
        f"{policy_sources}\n"
        "warnings:\n"
        f"{warnings}\n"
        "blockers:\n"
        f"{blockers}\n"
        "---\n\n"
    )
    return f"{frontmatter}# {draft.title}\n\n{draft.body}"


def write_draft(draft: Draft, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{draft.platform}.{draft.language}.md".replace("/", "-")
    path = output_dir / filename
    path.write_text(render_markdown(draft), encoding="utf-8")
    return path


def write_manifest(drafts: list[Draft], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "draft_count": len(drafts),
        "drafts": [
            {
                "platform": draft.platform,
                "language": draft.language,
                "status": draft.status,
                "publish_mode": draft.metadata["publish_mode"],
                "warnings": draft.warnings,
                "blockers": draft.blockers,
                "char_count": draft.metadata["char_count"],
            }
            for draft in drafts
        ],
    }
    path = output_dir / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def generate(
    source_path: Path,
    output_dir: Path,
    platforms: list[str],
    languages: list[str],
) -> list[Draft]:
    source = load_source(source_path)
    drafts: list[Draft] = []
    for platform_slug in platforms:
        for language_code in languages:
            draft = build_draft(source, platform_slug, language_code)
            write_draft(draft, output_dir)
            drafts.append(draft)
    write_manifest(drafts, output_dir)
    return drafts


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate compliance-first, platform-specific ToneSoul outreach drafts."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--platforms",
        default="lesswrong,ea-forum,huggingface,devto,substack,bluesky,linkedin,hacker-news,arxiv",
        help=f"Comma-separated platform slugs. Known: {', '.join(known_platforms())}",
    )
    parser.add_argument(
        "--languages",
        default="zh-TW,en",
        help=f"Comma-separated language codes. Known: {', '.join(known_languages())}",
    )
    parser.add_argument("--list-platforms", action="store_true")
    parser.add_argument("--list-languages", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_platforms:
        print("\n".join(known_platforms()))
        return 0
    if args.list_languages:
        print("\n".join(known_languages()))
        return 0

    platforms = _split_csv(args.platforms)
    languages = _split_csv(args.languages)
    drafts = generate(args.source, args.output_dir, platforms, languages)

    for draft in drafts:
        print(
            f"{draft.platform}.{draft.language}: {draft.status} "
            f"({draft.metadata['publish_mode']}, {draft.metadata['char_count']} chars)"
        )
    print(f"Manifest: {args.output_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
