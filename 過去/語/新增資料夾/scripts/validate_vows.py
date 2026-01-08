import yaml, json
from pathlib import Path

def load_yaml(path): return yaml.safe_load(open(path))
def load_json(path): return json.load(open(path))

def validate_vows(vows_path, persona_path):
    vows = load_yaml(vows_path)['vows']
    persona = load_json(persona_path)

    report = []
    for vow in vows:
        missing_modules = [m for m in vow['modules'] if m not in persona]
        if missing_modules:
            report.append(f"❗ ∑{vow['id']}｜{vow['name']} 缺少模組定義：{', '.join(missing_modules)}")
        else:
            report.append(f"✅ ∑{vow['id']}｜{vow['name']} 誓語完整")
    return "\n".join(report)

if __name__ == "__main__":
    import sys
    result = validate_vows(sys.argv[1], sys.argv[2])
    Path("artifacts/report.md").write_text("# 語魂誓語責任驗證報告\n\n" + result)