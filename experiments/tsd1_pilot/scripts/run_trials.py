import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.tsr_metrics import score as tsr_score
from tonesoul.ystm.representation import embed_text, EmbeddingConfig


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _variance(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return sum((val - mean) ** 2 for val in values) / len(values)


def _pearson(x: List[float], y: List[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    mx = _mean(x)
    my = _mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def _rankdata(values: List[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks[indexed[k][0]] = rank
        i = j
    return ranks


def _spearman(x: List[float], y: List[float]) -> float | None:
    rx = _rankdata(x)
    ry = _rankdata(y)
    return _pearson(rx, ry)


def _embedding_variance(embeddings: List[List[float]]) -> float:
    if not embeddings:
        return 0.0
    dims = len(embeddings[0])
    if dims == 0:
        return 0.0
    return _mean([_variance([vec[d] for vec in embeddings]) for d in range(dims)])


def _load_json(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _format_float(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def _load_existing_runs(summary_path: Path) -> List[str]:
    if not summary_path.exists():
        return []
    text = summary_path.read_text(encoding="utf-8")
    runs: List[str] = []
    in_runs = False
    for line in text.splitlines():
        if line.strip().lower() == "runs:":
            in_runs = True
            continue
        if in_runs:
            if line.startswith("- "):
                runs.append(line[2:])
                continue
            if line.strip() and (line.startswith("#") or line.lower().startswith("notes")):
                break
    return runs


def _write_summary_md(
    summary_path: Path,
    summary: Dict[str, object],
    response_count: int,
    timestamp: str,
) -> None:
    correlation = summary.get("correlation", {}) if isinstance(summary, dict) else {}
    settings = summary.get("settings", {}) if isinstance(summary, dict) else {}
    prompt_count = correlation.get("prompt_count")
    pearson = correlation.get("pearson")
    spearman = correlation.get("spearman")
    dims = settings.get("embedding_dims")

    entry = (
        f"{timestamp} | prompts={prompt_count} responses={response_count} | "
        f"pearson={_format_float(pearson)} | spearman={_format_float(spearman)} | dims={dims}"
    )
    existing = _load_existing_runs(summary_path)
    runs = [entry] + [line for line in existing if line != entry]

    lines = [
        "# TSD-1 Pilot Summary",
        "",
        "Latest Run",
        f"- Timestamp: {timestamp}",
        f"- Prompt count: {prompt_count}",
        f"- Response count: {response_count}",
        f"- Pearson r: {_format_float(pearson)}",
        f"- Spearman rho: {_format_float(spearman)}",
        f"- Embedding dims: {dims}",
        "",
        "Runs:",
    ]
    lines.extend(f"- {line}" for line in runs)
    lines.extend(["", "Notes", "-"])

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="TSD-1 pilot: tension vs diversity correlation")
    parser.add_argument("--prompts", required=True, help="Path to prompts.json")
    parser.add_argument("--responses", required=True, help="Path to responses.json")
    parser.add_argument("--out-dir", required=True, help="Output directory for results")
    parser.add_argument("--dims", type=int, default=12, help="Embedding dimensions")
    parser.add_argument("--summary-md", help="Optional summary markdown path")
    args = parser.parse_args()

    prompts = _load_json(Path(args.prompts))
    responses = _load_json(Path(args.responses))

    responses_by_prompt: Dict[str, List[Dict[str, str]]] = {}
    for item in responses:
        prompt_id = item.get("prompt_id")
        if not prompt_id:
            continue
        responses_by_prompt.setdefault(prompt_id, []).append(item)

    config = EmbeddingConfig(dims=args.dims)
    trials_path = Path(args.out_dir) / "trials.jsonl"
    summary_path = Path(args.out_dir) / "summary.json"
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    prompt_metrics = []
    trial_rows = []

    for prompt in prompts:
        prompt_id = prompt.get("id")
        if not prompt_id:
            continue
        items = responses_by_prompt.get(prompt_id, [])
        if len(items) < 2:
            continue

        tensions = []
        embeddings = []

        for item in items:
            text = item.get("text", "")
            tsr = tsr_score(text)
            tension = tsr.get("tsr", {}).get("T", 0.0)
            emb = embed_text(text, config)
            embeddings.append(emb.tolist())
            tensions.append(float(tension))
            trial_rows.append(
                {
                    "prompt_id": prompt_id,
                    "response_id": item.get("response_id"),
                    "tension": float(tension),
                }
            )

        prompt_metrics.append(
            {
                "prompt_id": prompt_id,
                "mean_tension": _mean(tensions),
                "diversity": _embedding_variance(embeddings),
                "response_count": len(items),
            }
        )

    x = [row["mean_tension"] for row in prompt_metrics]
    y = [row["diversity"] for row in prompt_metrics]

    summary = {
        "prompt_metrics": prompt_metrics,
        "correlation": {
            "pearson": _pearson(x, y),
            "spearman": _spearman(x, y),
            "prompt_count": len(prompt_metrics),
        },
        "settings": {
            "embedding_dims": args.dims,
        },
    }
    response_count = sum(row["response_count"] for row in prompt_metrics)

    with trials_path.open("w", encoding="utf-8") as handle:
        for row in trial_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    summary_md = (
        Path(args.summary_md)
        if args.summary_md
        else Path(args.out_dir).resolve().parent / "analysis" / "summary.md"
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_summary_md(summary_md, summary, response_count, timestamp)


if __name__ == "__main__":
    main()
