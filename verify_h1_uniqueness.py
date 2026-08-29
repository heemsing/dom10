#!/usr/bin/env python3
import os
import re
from pathlib import Path
from collections import defaultdict

def extract_h1(filepath):
    """Extract H1 text from a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    h1_pattern = r'<h1[^>]*>(.*?)</h1>'
    match = re.search(h1_pattern, content, re.DOTALL)
    
    if match:
        # Remove HTML tags and normalize whitespace
        h1_text = re.sub(r'<[^>]+>', '', match.group(1))
        h1_text = ' '.join(h1_text.split())
        return h1_text
    return None

def main():
    metro_dir = Path('/workspace/metro')
    h1_map = defaultdict(list)
    
    for filepath in metro_dir.glob('*.html'):
        h1 = extract_h1(filepath)
        if h1:
            h1_map[h1].append(filepath.name)
    
    # Find duplicates
    duplicates = {h1: files for h1, files in h1_map.items() if len(files) > 1}
    
    if duplicates:
        print("❌ Found duplicated H1s:")
        for h1, files in duplicates.items():
            print(f"\nH1: \"{h1}\"")
            print(f"   Duplicated on {len(files)} pages:")
            for f in files:
                print(f"   - {f}")
        print(f"\nTotal duplicated H1 groups: {len(duplicates)}")
    else:
        print("✅ All H1 tags are unique!")
    
    print(f"\nTotal files checked: {len(h1_map)}")

if __name__ == '__main__':
    main()
