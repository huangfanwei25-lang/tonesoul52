import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.data_ingest import MarketDataIngestor


def main():
    ingestor = MarketDataIngestor()

    print("Fetching 2324 Compal data...")
    profile = ingestor.fetch_full_profile("2324", start_date="2024-01-01")

    def print_schema(dataset, name):
        print(f"\n--- {name} Types ---")
        if dataset:
            # Filter to one quarter to get a clean list
            q1_data = [item.data for item in dataset if item.data.get("date") == "2024-03-31"]
            for d in q1_data:
                print(f"type: '{d.get('type')}' -> origin_name: '{d.get('origin_name')}'")

    print_schema(profile["income_statement"], "Income Statement")
    print_schema(profile["balance_sheet"], "Balance Sheet")
    print_schema(profile["cash_flow"], "Cash Flow")


if __name__ == "__main__":
    main()
