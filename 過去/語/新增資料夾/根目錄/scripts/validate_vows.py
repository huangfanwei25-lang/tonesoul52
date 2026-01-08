import os
import yaml

def validate_vow_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            data = yaml.safe_load(file)
            assert '誓語編號' in data, "缺少誓語編號"
            assert '誓語條文' in data, "缺少誓語條文"
            assert '模組對應' in data, "缺少模組對應"
            print(f"✅ 驗證通過：{filepath}")
        except Exception as e:
            print(f"❌ 驗證失敗：{filepath} 錯誤：{e}")
            exit(1)

def main():
    root_dir = '.vows'
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.yml'):
                validate_vow_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
