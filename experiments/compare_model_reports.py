#!/usr/bin/env python3
"""
GPT-5.3 vs GPT-5.4 架構分析比對工具

用法:
  1. 將 GPT-5.3 的分析報告貼入 reports/analysis_gpt53.md
  2. 將 GPT-5.4 的分析報告貼入 reports/analysis_gpt54.md
  3. 執行: python experiments/compare_model_reports.py

※ 也可用 --a / --b 指定任意兩個報告檔
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"


# ─────────────────────────────────────────────
# 評估維度定義
# ─────────────────────────────────────────────

DIMENSIONS = [
    {
        "id": "depth",
        "name": "分析深度",
        "description": "是否深入到具體程式碼層級（檔案名、函數名、行號）",
        "indicators": [
            "提及具體檔案路徑",
            "引用函數/類別名稱",
            "指出具體行號或程式碼片段",
            "說明因果關係（為什麼有問題、會造成什麼後果）",
        ],
    },
    {
        "id": "coverage",
        "name": "覆蓋範圍",
        "description": "是否涵蓋了系統的主要元件",
        "indicators": [
            "提及 Council 治理層",
            "提及 Memory 記憶系統",
            "提及 LLM 整合層（Ollama/Gemini）",
            "提及 CI/CD 管線",
            "提及前端（Next.js / Vercel）",
            "提及安全性（Guardian / Red Team）",
            "提及 API 設計",
        ],
    },
    {
        "id": "actionability",
        "name": "可操作性",
        "description": "建議是否具體可執行",
        "indicators": [
            "提供優先級排序（P0/P1/P2）",
            "給出具體修改步驟",
            "估算工作量或風險",
            "建議驗證方法",
        ],
    },
    {
        "id": "accuracy",
        "name": "準確度",
        "description": "分析是否對應實際程式碼狀態",
        "indicators": [
            "引用的檔案確實存在",
            "描述的架構符合實際",
            "沒有幻覺（hallucination）",
            "理解正確的依賴關係",
        ],
    },
    {
        "id": "chinese_quality",
        "name": "中文品質",
        "description": "繁體中文表達的自然度和專業度",
        "indicators": [
            "使用正確的繁體中文（非簡體）",
            "技術術語翻譯準確",
            "語句通順不生硬",
            "格式排版清晰",
        ],
    },
    {
        "id": "insight",
        "name": "洞察力",
        "description": "是否發現非顯而易見的問題",
        "indicators": [
            "找到隱藏的耦合或依賴",
            "識別潛在的擴展性問題",
            "提出架構層級的改善（非只是 bug fix）",
            "有創意的解決方案",
        ],
    },
]


# ─────────────────────────────────────────────
# 自動化指標萃取（不需 LLM 的部分）
# ─────────────────────────────────────────────

@dataclass
class AutoMetrics:
    """從報告文字自動萃取的量化指標"""
    total_chars: int = 0
    total_lines: int = 0
    code_blocks: int = 0
    file_references: int = 0
    headings: int = 0
    bullet_points: int = 0
    tables: int = 0
    unique_files_mentioned: int = 0
    files_mentioned: List[str] = field(default_factory=list)

    # 語魂核心元件覆蓋
    mentions_council: bool = False
    mentions_memory: bool = False
    mentions_llm: bool = False
    mentions_guardian: bool = False
    mentions_pipeline: bool = False
    mentions_frontend: bool = False
    mentions_ci: bool = False
    mentions_api: bool = False


def extract_auto_metrics(text: str) -> AutoMetrics:
    """從報告文字萃取量化指標"""
    m = AutoMetrics()
    m.total_chars = len(text)
    m.total_lines = text.count("\n") + 1
    m.code_blocks = len(re.findall(r"```", text)) // 2
    m.headings = len(re.findall(r"^#{1,4}\s", text, re.MULTILINE))
    m.bullet_points = len(re.findall(r"^\s*[-*]\s", text, re.MULTILINE))
    m.tables = len(re.findall(r"^\|.*\|$", text, re.MULTILINE)) // 2

    # 檔案路徑萃取
    file_refs = re.findall(
        r"(?:tonesoul|tests|scripts|apps|docs|memory|spec|reports)[\\/][\w\\/.-]+\.\w+",
        text,
    )
    m.file_references = len(file_refs)
    m.files_mentioned = sorted(set(file_refs))
    m.unique_files_mentioned = len(m.files_mentioned)

    # 核心元件覆蓋
    text_lower = text.lower()
    m.mentions_council = any(w in text_lower for w in ["council", "治理", "審議", "三角"])
    m.mentions_memory = any(w in text_lower for w in ["memory", "記憶", "hippocampus", "consolidat"])
    m.mentions_llm = any(w in text_lower for w in ["ollama", "gemini", "llm", "lm studio", "模型"])
    m.mentions_guardian = any(w in text_lower for w in ["guardian", "守護", "red.team", "adversar"])
    m.mentions_pipeline = any(w in text_lower for w in ["pipeline", "管線", "unified", "dispatch"])
    m.mentions_frontend = any(w in text_lower for w in ["next.js", "vercel", "frontend", "前端", "react"])
    m.mentions_ci = any(w in text_lower for w in ["ci", "github.action", "workflow", "healthcheck"])
    m.mentions_api = any(w in text_lower for w in ["/api/", "api_spec", "endpoint", "flask"])

    return m


# ─────────────────────────────────────────────
# 比對報告產生
# ─────────────────────────────────────────────

def generate_comparison(
    name_a: str,
    text_a: str,
    name_b: str,
    text_b: str,
) -> str:
    """產生兩份報告的比對分析"""
    ma = extract_auto_metrics(text_a)
    mb = extract_auto_metrics(text_b)

    lines = [
        f"# 模型分析比對報告",
        f"",
        f"**產生時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## 基本統計",
        f"",
        f"| 指標 | {name_a} | {name_b} | 差異 |",
        f"|------|---------|---------|------|",
        f"| 總字數 | {ma.total_chars:,} | {mb.total_chars:,} | {mb.total_chars - ma.total_chars:+,} |",
        f"| 總行數 | {ma.total_lines:,} | {mb.total_lines:,} | {mb.total_lines - ma.total_lines:+,} |",
        f"| 程式碼區塊 | {ma.code_blocks} | {mb.code_blocks} | {mb.code_blocks - ma.code_blocks:+d} |",
        f"| 標題數 | {ma.headings} | {mb.headings} | {mb.headings - ma.headings:+d} |",
        f"| 要點列表 | {ma.bullet_points} | {mb.bullet_points} | {mb.bullet_points - ma.bullet_points:+d} |",
        f"| 表格 | {ma.tables} | {mb.tables} | {mb.tables - ma.tables:+d} |",
        f"| 引用檔案次數 | {ma.file_references} | {mb.file_references} | {mb.file_references - ma.file_references:+d} |",
        f"| 涉及獨立檔案 | {ma.unique_files_mentioned} | {mb.unique_files_mentioned} | {mb.unique_files_mentioned - ma.unique_files_mentioned:+d} |",
        f"",
        f"## 核心元件覆蓋",
        f"",
        f"| 元件 | {name_a} | {name_b} |",
        f"|------|---------|---------|",
        f"| Council 治理層 | {'✅' if ma.mentions_council else '❌'} | {'✅' if mb.mentions_council else '❌'} |",
        f"| Memory 記憶系統 | {'✅' if ma.mentions_memory else '❌'} | {'✅' if mb.mentions_memory else '❌'} |",
        f"| LLM 整合層 | {'✅' if ma.mentions_llm else '❌'} | {'✅' if mb.mentions_llm else '❌'} |",
        f"| Guardian 安全層 | {'✅' if ma.mentions_guardian else '❌'} | {'✅' if mb.mentions_guardian else '❌'} |",
        f"| Pipeline 管線 | {'✅' if ma.mentions_pipeline else '❌'} | {'✅' if mb.mentions_pipeline else '❌'} |",
        f"| 前端 (Next/Vercel) | {'✅' if ma.mentions_frontend else '❌'} | {'✅' if mb.mentions_frontend else '❌'} |",
        f"| CI/CD | {'✅' if ma.mentions_ci else '❌'} | {'✅' if mb.mentions_ci else '❌'} |",
        f"| API 設計 | {'✅' if ma.mentions_api else '❌'} | {'✅' if mb.mentions_api else '❌'} |",
        f"",
        f"## 引用檔案差異分析",
        f"",
    ]

    # Only-in-A / Only-in-B / Common
    set_a = set(ma.files_mentioned)
    set_b = set(mb.files_mentioned)
    common = sorted(set_a & set_b)
    only_a = sorted(set_a - set_b)
    only_b = sorted(set_b - set_a)

    lines.append(f"| 分類 | 數量 | 檔案 |")
    lines.append(f"|------|------|------|")
    lines.append(f"| 共同提及 | {len(common)} | {', '.join(f'`{f}`' for f in common[:10])}{'...' if len(common) > 10 else ''} |")
    lines.append(f"| 僅 {name_a} 提及 | {len(only_a)} | {', '.join(f'`{f}`' for f in only_a[:10])}{'...' if len(only_a) > 10 else ''} |")
    lines.append(f"| 僅 {name_b} 提及 | {len(only_b)} | {', '.join(f'`{f}`' for f in only_b[:10])}{'...' if len(only_b) > 10 else ''} |")

    # Coverage score
    coverage_a = sum([
        ma.mentions_council, ma.mentions_memory, ma.mentions_llm,
        ma.mentions_guardian, ma.mentions_pipeline, ma.mentions_frontend,
        ma.mentions_ci, ma.mentions_api,
    ])
    coverage_b = sum([
        mb.mentions_council, mb.mentions_memory, mb.mentions_llm,
        mb.mentions_guardian, mb.mentions_pipeline, mb.mentions_frontend,
        mb.mentions_ci, mb.mentions_api,
    ])

    lines.extend([
        f"",
        f"## 總評分（自動化指標）",
        f"",
        f"| 維度 | {name_a} | {name_b} |",
        f"|------|---------|---------|",
        f"| 元件覆蓋率 | {coverage_a}/8 ({coverage_a/8*100:.0f}%) | {coverage_b}/8 ({coverage_b/8*100:.0f}%) |",
        f"| 程式碼引用密度 | {ma.file_references / max(ma.total_lines, 1) * 100:.1f} refs/100行 | {mb.file_references / max(mb.total_lines, 1) * 100:.1f} refs/100行 |",
        f"| 結構化程度 | {ma.headings + ma.tables + ma.code_blocks} 元素 | {mb.headings + mb.tables + mb.code_blocks} 元素 |",
        f"",
        f"## 人工評估維度（需手動填寫）",
        f"",
        f"以下維度需要你人工判斷，在 1-5 之間評分：",
        f"",
        f"| 維度 | 說明 | {name_a} | {name_b} |",
        f"|------|------|---------|---------|",
    ])

    for dim in DIMENSIONS:
        lines.append(f"| {dim['name']} | {dim['description']} | _/5 | _/5 |")

    lines.extend([
        f"",
        f"### 評估指標細項",
        f"",
    ])
    for dim in DIMENSIONS:
        lines.append(f"**{dim['name']}** — 檢查以下項目：")
        for ind in dim["indicators"]:
            lines.append(f"  - [ ] {ind}")
        lines.append("")

    # JSON summary for programmatic use
    summary = {
        "generated_at": datetime.now().isoformat(),
        "model_a": {"name": name_a, **{k: v for k, v in asdict(ma).items() if k != "files_mentioned"}},
        "model_b": {"name": name_b, **{k: v for k, v in asdict(mb).items() if k != "files_mentioned"}},
        "coverage_score_a": coverage_a,
        "coverage_score_b": coverage_b,
    }

    json_path = REPORTS_DIR / "model_comparison_latest.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="比對兩份模型分析報告")
    parser.add_argument("--a", default=str(REPORTS_DIR / "analysis_gpt53.md"), help="報告 A 路徑")
    parser.add_argument("--b", default=str(REPORTS_DIR / "analysis_gpt54.md"), help="報告 B 路徑")
    parser.add_argument("--name-a", default="GPT-5.3", help="模型 A 名稱")
    parser.add_argument("--name-b", default="GPT-5.4", help="模型 B 名稱")
    parser.add_argument("--output", default=str(REPORTS_DIR / "model_comparison_latest.md"), help="輸出路徑")
    args = parser.parse_args()

    path_a, path_b = Path(args.a), Path(args.b)

    if not path_a.exists():
        print(f"❌ 報告 A 不存在: {path_a}")
        print(f"   請將 {args.name_a} 的分析報告存到這個路徑")
        sys.exit(1)
    if not path_b.exists():
        print(f"❌ 報告 B 不存在: {path_b}")
        print(f"   請將 {args.name_b} 的分析報告存到這個路徑")
        sys.exit(1)

    text_a = path_a.read_text(encoding="utf-8")
    text_b = path_b.read_text(encoding="utf-8")

    report = generate_comparison(args.name_a, text_a, args.name_b, text_b)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(f"✅ 比對報告已產生: {out_path}")
    print(f"   JSON 摘要: {REPORTS_DIR / 'model_comparison_latest.json'}")
    print()
    print(report)


if __name__ == "__main__":
    main()
