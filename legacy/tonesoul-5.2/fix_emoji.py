#!/usr/bin/env python3
"""
Fix emoji and encoding issues in Python files.
Removes non-ASCII characters (emoji) and BOM, normalizes line endings.
"""
import os
import re

TARGET_FILES = [
    "body/dashboard/app.py",
    "body/spine/controller.py", 
    "body/memory/hippocampus.py",
    "body/memory/vector_store.py",
    "body/brain/llm_client.py",
    "body/surgeon/sandbox.py",
    "body/spine_system.py",
    "body/senses/vision.py",
    "body/dream/weaver.py",
    "body/council.py",
    "body/interactive_console.py",
    "body/force_lucid_dream.py",
    "body/run_dream_cycle.py",
    "body/live_demo.py",
    "body/multipath_engine.py",
    "body/vital_organs/heart.py",
    "body/yuhun_metrics.py",
    "body/yuhun_meta_gate.py",
    "body/yuhun_meta_attention.py",
    "body/yuhun_live.py",
    "body/yuhun_cot_monitor.py",
    "body/skill_acquisition_trigger.py",
    "body/skill_acquisition_librarian.py",
]

# Emoji pattern: matches common emoji ranges
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    "\U00002600-\U000026FF"  # misc symbols
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"             # zero width joiner
    "\U00002B50"             # star
    "]+", 
    flags=re.UNICODE
)

def fix_file(filepath):
    """Fix encoding issues in a single file."""
    if not os.path.exists(filepath):
        print(f"[SKIP] Not found: {filepath}")
        return False
    
    try:
        # Read with UTF-8
        with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
            content = f.read()
        
        original_len = len(content)
        
        # Normalize line endings
        content = content.replace('\r\r\r\n', '\n')
        content = content.replace('\r\r\n', '\n')
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        
        # Remove emoji
        content = EMOJI_PATTERN.sub('', content)
        
        # Remove any remaining non-printable non-ASCII (except CJK)
        # Keep: ASCII printable, newlines, tabs, CJK characters
        cleaned_lines = []
        for line in content.split('\n'):
            cleaned_chars = []
            for ch in line:
                cp = ord(ch)
                # Keep ASCII printable (32-126), tab (9), and CJK (0x4E00-0x9FFF, 0x3000-0x303F)
                if (32 <= cp <= 126) or cp == 9 or (0x4E00 <= cp <= 0x9FFF) or (0x3000 <= cp <= 0x303F) or (0xFF00 <= cp <= 0xFFEF):
                    cleaned_chars.append(ch)
            cleaned_lines.append(''.join(cleaned_chars))
        
        content = '\n'.join(cleaned_lines)
        
        # Write back with UTF-8 without BOM, Unix line endings
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        new_len = len(content)
        print(f"[OK] Fixed: {filepath} ({original_len} -> {new_len} chars)")
        return True
        
    except Exception as e:
        print(f"[ERR] {filepath}: {e}")
        return False


def main():
    print("=== Emoji & Encoding Fixer ===")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    fixed = 0
    for relpath in TARGET_FILES:
        fullpath = os.path.join(repo_root, relpath)
        if fix_file(fullpath):
            fixed += 1
    
    print(f"\n=== Done: {fixed}/{len(TARGET_FILES)} files fixed ===")


if __name__ == "__main__":
    main()
