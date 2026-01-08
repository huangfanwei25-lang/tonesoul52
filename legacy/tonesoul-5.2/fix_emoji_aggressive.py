#!/usr/bin/env python3
"""
Aggressive fix: remove ALL non-ASCII characters except CJK Chinese.
"""
import os

TARGET_FILES = [
    "body/dashboard/app.py",
    "body/spine/controller.py",
]


def fix_aggressive(filepath):
    """Remove all non-ASCII except Chinese characters."""
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath}")
        return
    
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    # Remove BOM if present
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    
    # Decode
    try:
        content = raw.decode('utf-8')
    except:
        content = raw.decode('utf-8', errors='ignore')
    
    # Keep only ASCII (0x00-0x7F) and CJK (0x4E00-0x9FFF)
    cleaned = []
    for ch in content:
        cp = ord(ch)
        if cp <= 0x7F:  # ASCII
            cleaned.append(ch)
        elif 0x4E00 <= cp <= 0x9FFF:  # CJK
            cleaned.append(ch)
        elif 0x3000 <= cp <= 0x303F:  # CJK punctuation
            cleaned.append(ch)
        # else: skip (including all emoji)
    
    result = ''.join(cleaned)
    
    # Normalize line endings
    result = result.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive blank lines (more than 2 consecutive)
    while '\n\n\n\n' in result:
        result = result.replace('\n\n\n\n', '\n\n')
    
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(result)
    
    print(f"[OK] {filepath}")


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in TARGET_FILES:
        fix_aggressive(os.path.join(repo, f))
    print("Done!")
