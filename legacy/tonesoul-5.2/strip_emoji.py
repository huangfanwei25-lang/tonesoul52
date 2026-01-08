import pathlib

REPLACEMENTS = {
    "\U0001f9e0": "[Brain]",
    "\U0001f525": "[Fire]",
    "\u2705": "[OK]",
    "\u274c": "[FAIL]",
    "\u26a0\ufe0f": "[WARN]",
}

paths = [
    pathlib.Path(r"C:\Users\user\Desktop\倉庫\body\dashboard\app.py"),
    pathlib.Path(r"C:\Users\user\Desktop\倉庫\body\spine\controller.py"),
]

def strip_bom_and_replace(path: pathlib.Path):
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    text = data.decode("utf-8", errors="replace")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print(f"Processed {path}")

for p in paths:
    if p.exists():
        strip_bom_and_replace(p)
    else:
        print(f"Missing: {p}")
