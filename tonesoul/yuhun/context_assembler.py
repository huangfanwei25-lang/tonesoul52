"""
YUHUN Core Protocol v1.0 — Context Assembler
上下文組裝器

根據 DPR 路由決策，組裝合規的 context 包。
規格文件：docs/architecture/CONTEXT_BUDGET_SPEC.md

設計原則：
  - 永遠不帶禁止源（FORBIDDEN_PREFIXES）
  - FAST_PATH 只帶 Layer 0 + Layer 1
  - COUNCIL_PATH 按衝突類型載入 Layer 2-4
  - token 超限時按優先順序裁剪

參考：
  Hermes Agent trajectory_compressor.py — 軌跡壓縮思路
  Vpon AI-Ready — 語義清晰的元數據體系
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from tonesoul.yuhun.dpr import DPRResult, RoutingDecision

# ─────────────────────────────────────────────
# 禁止源清單（永遠不進提示詞）
# ─────────────────────────────────────────────

FORBIDDEN_PREFIXES = (
    "docs/chronicles/task_archive",
    ".archive/",
    "memory/",
    "data/chromadb/",
    "graphify-out/",
    "tonesoul_evolution/",
    "temp/",
)


class ContextViolationError(Exception):
    """context 來源違反 CONTEXT_BUDGET_SPEC 禁止清單"""

    pass


# ─────────────────────────────────────────────
# 衝突類型 → 對應架構契約
# ─────────────────────────────────────────────

_CONFLICT_CONTRACT_MAP = {
    "legal_ethics": "docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md",
    "uncertainty": "docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md",
    "research": "docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md",
}

_LEGAL_KEYWORDS = {"法律", "倫理", "隱私", "個資", "legal", "ethics", "privacy"}
_UNCERTAINTY_KEYWORDS = {"應該", "最佳", "風險", "可行", "best", "should", "risk"}
_RESEARCH_KEYWORDS = {"架構", "系統", "算法", "研究", "architecture", "algorithm", "research"}


def _classify_conflict_type(triggers: list[str]) -> str:
    """根據 DPR 觸發的模式，分類衝突類型以選擇對應契約"""
    text = " ".join(triggers).lower()
    if any(kw in text for kw in _LEGAL_KEYWORDS):
        return "legal_ethics"
    if any(kw in text for kw in _UNCERTAINTY_KEYWORDS):
        return "uncertainty"
    if any(kw in text for kw in _RESEARCH_KEYWORDS):
        return "research"
    return "uncertainty"  # 預設


# ─────────────────────────────────────────────
# 輸出結構
# ─────────────────────────────────────────────


@dataclass
class ContextPackage:
    """
    組裝完成的 Context 包

    Layers:
        0: axioms_content — AXIOMS.json 內容（必帶）
        1: user_request   — 使用者原始輸入（必帶）
        2: anchor_memory  — 穩定錨點記憶（COUNCIL_PATH 才帶）
        3: contracts      — 相關架構契約摘要（COUNCIL_PATH 才帶）
        4: council_frame  — 議會框架摘要（COUNCIL_PATH 才帶）
    """

    routing: RoutingDecision
    user_request: str
    axioms_content: str = ""
    anchor_memory: list[str] = field(default_factory=list)
    contracts: list[str] = field(default_factory=list)
    council_frame: str = ""
    # 診斷資訊
    sources_used: list[str] = field(default_factory=list)
    estimated_tokens: int = 0

    def to_prompt_sections(self) -> list[str]:
        """
        輸出給 LLM 使用的 prompt section 列表
        順序：公理 → 錨點記憶 → 契約 → 議會框架 → 請求
        """
        sections = []
        if self.axioms_content:
            sections.append(f"[AXIOMS]\n{self.axioms_content}")
        if self.anchor_memory:
            sections.append("[STABLE ANCHORS]\n" + "\n---\n".join(self.anchor_memory))
        if self.contracts:
            sections.append("[ARCHITECTURE CONTRACTS]\n" + "\n---\n".join(self.contracts))
        if self.council_frame:
            sections.append(f"[COUNCIL FRAME]\n{self.council_frame}")
        sections.append(f"[USER REQUEST]\n{self.user_request}")
        return sections


# ─────────────────────────────────────────────
# 驗證器
# ─────────────────────────────────────────────


def validate_context_sources(sources: list[str], repo_root: Optional[Path] = None) -> bool:
    """
    驗證 context 來源不包含禁止源

    Args:
        sources: 文件路徑列表
        repo_root: 倉庫根目錄（用於相對路徑解析）

    Returns:
        True 如果全部合法

    Raises:
        ContextViolationError: 如果任何來源在禁止清單中
    """
    for src in sources:
        normalized = str(src).replace("\\", "/")
        for forbidden in FORBIDDEN_PREFIXES:
            if normalized.startswith(forbidden):
                raise ContextViolationError(
                    f"'{src}' 違反 CONTEXT_BUDGET_SPEC 禁止清單\n"
                    f"  禁止前綴：'{forbidden}'\n"
                    f"  規格來源：docs/architecture/CONTEXT_BUDGET_SPEC.md"
                )
    return True


# ─────────────────────────────────────────────
# 核心組裝器
# ─────────────────────────────────────────────


class ContextAssembler:
    """
    根據 DPR 路由決策組裝合規的 Context 包

    使用方式：
        assembler = ContextAssembler(repo_root=Path("."))
        dpr_result = route(user_input)
        package = assembler.assemble(dpr_result, user_input)
        for section in package.to_prompt_sections():
            print(section)
    """

    # token 近似估算（4 chars ≈ 1 token）
    _CHARS_PER_TOKEN = 4
    # Layer budget（token 估算上限）
    _AXIOMS_BUDGET = 1_500
    _ANCHOR_BUDGET = 600
    _CONTRACT_BUDGET = 2_000
    _COUNCIL_FRAME_BUDGET = 800

    def __init__(self, repo_root: Optional[Path] = None):
        self._repo_root = repo_root or Path(__file__).resolve().parents[3]
        self._axioms_cache: Optional[str] = None
        self._contract_cache: dict[str, str] = {}

    # ─── 私有載入器 ───

    def _load_axioms(self) -> str:
        """Layer 0：載入 AXIOMS.json（快取）"""
        if self._axioms_cache is not None:
            return self._axioms_cache

        axioms_path = self._repo_root / "AXIOMS.json"
        try:
            raw = json.loads(axioms_path.read_text(encoding="utf-8"))
            # 只取一行版公理，避免太長
            lines = []
            for axiom in raw.get("axioms", []):
                lines.append(f"P{axiom.get('id', '?')}: {axiom.get('one_line', '')}")
            self._axioms_cache = "\n".join(lines)
        except Exception:
            self._axioms_cache = ""  # 失敗靜默降級，不阻塞

        return self._axioms_cache

    def _load_contract(self, contract_type: str) -> str:
        """Layer 3：載入架構契約（前 _CONTRACT_BUDGET token，快取）"""
        if contract_type in self._contract_cache:
            return self._contract_cache[contract_type]

        rel_path = _CONFLICT_CONTRACT_MAP.get(contract_type, "")
        if not rel_path:
            return ""

        filepath = self._repo_root / rel_path
        try:
            content = filepath.read_text(encoding="utf-8")
            # 取前 budget chars
            max_chars = self._CONTRACT_BUDGET * self._CHARS_PER_TOKEN
            truncated = content[:max_chars]
            if len(content) > max_chars:
                truncated += "\n… [已截斷至 context budget]"
            self._contract_cache[contract_type] = truncated
        except Exception:
            self._contract_cache[contract_type] = ""

        return self._contract_cache[contract_type]

    @staticmethod
    def _get_council_frame_summary() -> str:
        """Layer 4：議會框架精簡版（固定格式，不從文件讀取）"""
        return (
            "議會框架：四向平行推演\n"
            "  理則家（Logician）：L1 事實阻力分析\n"
            "  創想者（Creator）：L2 突破口探索\n"
            "  安全防護員（Safety Guard）：紅線偵測\n"
            "  共情者（Empath）：整合最終裁決\n"
            "分歧可見協議（VoD）：語義距離 > 0.8 強制雙軌輸出"
        )

    def _load_anchor_memory(self, top_n: int = 3) -> list[str]:
        """
        Layer 2：嘗試從 WorldSense 取穩定錨點記憶

        WorldSense.stable_anchors() 回傳 StableAnchor dataclass，
        包含 home_vector, low_drift_steps, mean_drift, stability_score。
        這裡將其轉為 LLM 可讀的字串格式。

        top_n: 目前未使用（WorldSense 不支援 top_n），留作未來擴充
        失敗時靜默返回空列表（錨點記憶是可選的）
        """
        try:
            from tonesoul.yuhun.world_sense import WorldSense

            ws = WorldSense()
            anchor = ws.stable_anchors()

            # 無觀測資料時不輸出錨點（穩定分數為 0 且沒有低漂移步驟）
            if anchor.stability_score == 0.0 and not anchor.low_drift_steps:
                return []

            lines = [
                f"穩定性分數：{anchor.stability_score:.0%}",
                f"平均漂移值：{anchor.mean_drift:.3f}",
                f"語義原點（home_vector）：{anchor.home_vector}",
            ]
            if anchor.low_drift_steps:
                steps_str = ", ".join(str(s) for s in anchor.low_drift_steps[:top_n])
                lines.append(f"低漂移步驟（最近 {top_n} 個）：{steps_str}")

            return lines
        except Exception:
            return []

    # ─── 公開 API ───

    def assemble(
        self,
        dpr_result: DPRResult,
        user_request: str,
        *,
        include_anchor_memory: bool = True,
    ) -> ContextPackage:
        """
        組裝合規 Context 包

        Args:
            dpr_result:          DPR 路由結果
            user_request:        使用者輸入
            include_anchor_memory: 是否嘗試載入錨點記憶（僅 COUNCIL_PATH 有效）

        Returns:
            ContextPackage — 含 to_prompt_sections() 方法
        """
        routing = dpr_result.decision
        sources_used = []
        total_chars = 0

        # ── Layer 0：AXIOMS（必帶）
        axioms = self._load_axioms()
        sources_used.append("AXIOMS.json")
        total_chars += len(axioms)

        # ── Layer 1：使用者請求（必帶）
        total_chars += len(user_request)

        # FAST_PATH 到此結束
        if routing == RoutingDecision.FAST_PATH:
            package = ContextPackage(
                routing=routing,
                user_request=user_request,
                axioms_content=axioms,
                sources_used=sources_used,
                estimated_tokens=total_chars // self._CHARS_PER_TOKEN,
            )
            return package

        # ── COUNCIL_PATH: Layer 2-4 ──

        # Layer 2：錨點記憶
        anchors: list[str] = []
        if include_anchor_memory:
            anchors = self._load_anchor_memory(top_n=3)
            if anchors:
                sources_used.append("world_sense.stable_anchors()")
                total_chars += sum(len(a) for a in anchors)

        # Layer 3：架構契約
        conflict_type = _classify_conflict_type(dpr_result.conflict_triggers)
        contract_text = self._load_contract(conflict_type)
        contracts = [contract_text] if contract_text else []
        if contracts:
            contract_path = _CONFLICT_CONTRACT_MAP.get(conflict_type, "unknown")
            sources_used.append(contract_path)
            total_chars += len(contract_text)

        # Layer 4：議會框架
        council_frame = self._get_council_frame_summary()
        sources_used.append("council_frame_summary")
        total_chars += len(council_frame)

        # 驗證來源合法性
        validate_context_sources(sources_used)

        return ContextPackage(
            routing=routing,
            user_request=user_request,
            axioms_content=axioms,
            anchor_memory=anchors,
            contracts=contracts,
            council_frame=council_frame,
            sources_used=sources_used,
            estimated_tokens=total_chars // self._CHARS_PER_TOKEN,
        )


# ─────────────────────────────────────────────
# 快速測試
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from tonesoul.yuhun.dpr import route

    assembler = ContextAssembler()

    print("=" * 60)
    print("Context Assembler — 快速驗證")
    print("=" * 60)

    test_cases = [
        ("FAST_PATH 測試", "幫我寫一個 hello world"),
        ("COUNCIL_PATH 測試", "這個 AI 系統存在法律漏洞嗎？如何評估倫理風險？"),
    ]

    for label, text in test_cases:
        result = route(text)
        package = assembler.assemble(result, text)
        print(f"\n[{label}] → {result.decision.value}")
        print(f"  預估 token：{package.estimated_tokens}")
        print(f"  使用來源：{package.sources_used}")
        print(f"  Sections 數量：{len(package.to_prompt_sections())}")

    # 驗證禁止源偵測
    print("\n[禁止源偵測測試]")
    try:
        validate_context_sources(["docs/chronicles/task_archive_2026.md"])
        print("  ❌ 應該拋出 ContextViolationError 但沒有")
    except ContextViolationError as e:
        print(f"  ✅ 正確偵測到禁止源：{e}")
