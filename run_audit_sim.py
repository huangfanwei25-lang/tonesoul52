import subprocess
import json


def run():
    try:
        res = subprocess.check_output(["python", "tools/audit_node.py"], text=True)
        # Parse output to find JSON blocks
        # (Since audit_node.py prints two JSON blocks, we'll just capture everything for now)
        with open("audit_simulation_v1.json", "w", encoding="utf-8") as f:
            f.write(res)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run()
