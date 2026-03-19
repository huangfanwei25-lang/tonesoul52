import json
import os
import sys
import time
from pathlib import Path

import requests

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

PRIVATE_CACHE_PATH = REPO_ROOT / "memory" / "autonomous" / "market" / "market_sweep_cache.json"
LEGACY_CACHE_PATH = REPO_ROOT / "market_sweep_cache.json"
STATUS_REPORT_PATH = REPO_ROOT / "docs" / "status" / "market_sweep_latest.txt"

from tonesoul.market.gold_detector import GoldDetector
from tonesoul.market.data_ingest import MarketDataIngestor
from scripts.run_gold_scan import scan_single


def get_all_twse_stocks(ingestor):
    url = 'https://api.finmindtrade.com/api/v4/data'
    parameter = {
        'dataset': 'TaiwanStockInfo'
    }
    # TaiwanStockInfo is a public dataset, no token strictly required
    try:
        resp = requests.get(url, params=parameter, timeout=10)
        data = resp.json()
        if data['msg'] == 'success':
            return [
                (str(row['stock_id']), str(row['stock_name']), str(row['industry_category']))
                for row in data['data'] 
                if row['type'] == 'twse' and len(str(row['stock_id'])) == 4
            ]
    except Exception as e:
        print(f"Error fetching stock list: {e}")
    return []


def _load_scanned_cache() -> set[str]:
    for cache_path in (PRIVATE_CACHE_PATH, LEGACY_CACHE_PATH):
        if not cache_path.exists():
            continue
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError):
            continue
        if not isinstance(payload, list):
            continue
        return {str(stock_id) for stock_id in payload}
    return set()


def _write_scanned_cache(scanned: set[str]) -> None:
    PRIVATE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRIVATE_CACHE_PATH.write_text(
        json.dumps(sorted(scanned), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    print(f"\n{'═' * 70}")
    print(f"  ToneSoul Market Sweeper — 尋找全市場的真金")
    print(f"{'═' * 70}")

    ingestor = MarketDataIngestor()
    if not ingestor.is_available:
        print("❌ FinMind is not available. Install: pip install FinMind")
        return

    detector = GoldDetector()
    stocks = get_all_twse_stocks(ingestor)
    
    if not stocks:
        print("❌ Could not fetch stock list.")
        return
        
    print(f"📡 Found {len(stocks)} TWSE stocks. Starting scan...")
    print(f"⚠️ This might take a while. Only Gold and Silver (Score >= 0.5) will be logged.")
    print("-" * 70)
    
    found_gold = []
    found_silver = []
    
    # Resume state is local runtime memory, not a repo-root source artifact.
    scanned = _load_scanned_cache()
    if scanned:
        print(f"Resuming from cache, {len(scanned)} already scanned.")

    for i, (stock_id, name, tag) in enumerate(stocks):
        if stock_id in scanned:
            continue
            
        # Add basic progress print every 10 stocks so we know it's alive
        if i % 10 == 0:
            print(f"Processing {i}/{len(stocks)}... (Last checked: {stock_id} {name})", end="\r", flush=True)

        try:
            report = scan_single(ingestor, detector, stock_id)
            if report.verdict in ("GOLD", "SILVER"):
                emoji = "🥇" if report.verdict == "GOLD" else "🥈"
                print(f"\n {emoji} {stock_id} {name:<12} | Score: {report.gold_score:.3f} | EPS: {report.trailing_eps:.1f} | PE: {report.current_pe:.1f}x")
                for sig in report.signals:
                    print(f"      ✦ {sig.signal_type}: {sig.strength:.2f} — {sig.evidence}")
                print("-" * 70)
                
                if report.verdict == "GOLD":
                    found_gold.append((stock_id, name, report))
                else:
                    found_silver.append((stock_id, name, report))
            
            # Update cache
            scanned.add(stock_id)
            if i % 10 == 0:
                _write_scanned_cache(scanned)
                    
            time.sleep(1.0) # 2x slower to be kind to the FinMind API
        except Exception as e:
            # Silently ignore errors for individual stocks to keep the scan running
            # usually it's missing data for new listings etc.
            time.sleep(1.5)

    _write_scanned_cache(scanned)
            
    print(f"\n{'═' * 70}")
    print(f"  🏆 SWEEP COMPLETE")
    print(f"  🥇 Found {len(found_gold)} GOLD stocks")
    print(f"  🥈 Found {len(found_silver)} SILVER stocks")
    print(f"{'═' * 70}")

    # Generate the daily output report
    STATUS_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with STATUS_REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("ToneSoul Market Sweeper - Latest Results\n")
        f.write("=" * 40 + "\n")
        f.write(f"🥇 GOLD STOCKS ({len(found_gold)}):\n")
        for sid, name, r in found_gold:
            f.write(f"  - {sid} {name:<8} | Score: {r.gold_score:.3f} | PE: {r.current_pe:.1f}x\n")
        
        f.write(f"\n🥈 SILVER STOCKS ({len(found_silver)}):\n")
        for sid, name, r in found_silver:
            f.write(f"  - {sid} {name:<8} | Score: {r.gold_score:.3f} | PE: {r.current_pe:.1f}x\n")
            
    print(f"📄 Full report saved to: {STATUS_REPORT_PATH}")

if __name__ == "__main__":
    main()
