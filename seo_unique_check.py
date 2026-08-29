#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Uniqueness Checker - Проверяет все HTML страницы на уникальность
"""

import os
import re
from html.parser import HTMLParser
from collections import defaultdict

class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.keywords = ""
        self.h1_tags = []
        self.canonical = ""
        self.og_title = ""
        self.in_title = False
        self.in_h1 = False
        self.current_text = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
            self.current_text = ""
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            property_val = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.description = content
            elif name == "keywords":
                self.keywords = content
            elif property_val == "og:title":
                self.og_title = content
            elif attrs_dict.get("rel") == "canonical":
                self.canonical = content
        elif tag == "h1":
            self.in_h1 = True
            self.current_text = ""
            
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            self.title = self.current_text.strip()
        elif tag == "h1":
            self.in_h1 = False
            if self.current_text.strip():
                self.h1_tags.append(self.current_text.strip())
                
    def handle_data(self, data):
        if self.in_title or self.in_h1:
            self.current_text += data

def extract_text_content(html_content):
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def analyze_seo_uniqueness(workspace_dir):
    html_files = []
    for root, dirs, files in os.walk(workspace_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file.endswith(('.html', '.htm')):
                html_files.append(os.path.join(root, file))
    
    print(f"Найдено HTML файлов: {len(html_files)}\n")
    
    titles = defaultdict(list)
    descriptions = defaultdict(list)
    h1_tags = defaultdict(list)
    canonical_urls = defaultdict(list)
    og_titles = defaultdict(list)
    text_hashes = defaultdict(list)
    issues = []
    
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            parser = MetaExtractor()
            parser.feed(content)
            rel_path = os.path.relpath(filepath, workspace_dir)
            
            if parser.title:
                titles[parser.title].append(rel_path)
            else:
                issues.append(f"MISSING_TITLE: {rel_path}")
            
            if parser.description:
                descriptions[parser.description].append(rel_path)
            else:
                issues.append(f"MISSING_DESCRIPTION: {rel_path}")
            
            if parser.h1_tags:
                for h1 in parser.h1_tags:
                    h1_tags[h1].append(rel_path)
            else:
                issues.append(f"MISSING_H1: {rel_path}")
            
            if parser.canonical:
                canonical_urls[parser.canonical].append(rel_path)
            
            if parser.og_title:
                og_titles[parser.og_title].append(rel_path)
            
            text_content = extract_text_content(content)
            if len(text_content) > 100:
                text_hash = hash(text_content)
                text_hashes[text_hash].append((rel_path, len(text_content)))
                
        except Exception as e:
            issues.append(f"ERROR reading {filepath}: {str(e)}")
    
    report = []
    report.append("=" * 80)
    report.append("SEO UNIQUE ANALYSIS REPORT")
    report.append("=" * 80)
    report.append(f"\nВсего проанализировано страниц: {len(html_files)}\n")
    
    # 1. Duplicates TITLE
    report.append("\n" + "=" * 80)
    report.append("1. DUPLICATED TITLE TAGS")
    report.append("=" * 80)
    duplicate_titles = {k: v for k, v in titles.items() if len(v) > 1}
    if duplicate_titles:
        report.append(f"\nWARNING: Found {len(duplicate_titles)} duplicated TITLEs")
        for title, files in list(duplicate_titles.items())[:10]:
            report.append(f"\nTITLE: \"{title[:80]}...\" ({len(title)} chars)")
            report.append(f"   Duplicated on {len(files)} pages:")
            for f in files[:5]:
                report.append(f"   - {f}")
    else:
        report.append("\nOK: All TITLE tags are unique!")
    
    # 2. Duplicates DESCRIPTION
    report.append("\n" + "=" * 80)
    report.append("2. DUPLICATED DESCRIPTION TAGS")
    report.append("=" * 80)
    duplicate_descriptions = {k: v for k, v in descriptions.items() if len(v) > 1}
    if duplicate_descriptions:
        report.append(f"\nWARNING: Found {len(duplicate_descriptions)} duplicated DESCRIPTIONs")
        for desc, files in list(duplicate_descriptions.items())[:10]:
            report.append(f"\nDESCRIPTION: \"{desc[:80]}...\" ({len(desc)} chars)")
            report.append(f"   Duplicated on {len(files)} pages:")
            for f in files[:5]:
                report.append(f"   - {f}")
    else:
        report.append("\nOK: All DESCRIPTION tags are unique!")
    
    # 3. Duplicates H1
    report.append("\n" + "=" * 80)
    report.append("3. DUPLICATED H1 HEADINGS")
    report.append("=" * 80)
    duplicate_h1 = {k: v for k, v in h1_tags.items() if len(v) > 1}
    if duplicate_h1:
        report.append(f"\nWARNING: Found {len(duplicate_h1)} duplicated H1s")
        for h1, files in list(duplicate_h1.items())[:15]:
            report.append(f"\nH1: \"{h1[:70]}...\"")
            report.append(f"   Duplicated on {len(files)} pages:")
            for f in files[:5]:
                report.append(f"   - {f}")
    else:
        report.append("\nOK: All H1 headings are unique!")
    
    # 4. Duplicates Canonical
    report.append("\n" + "=" * 80)
    report.append("4. DUPLICATED CANONICAL URLs")
    report.append("=" * 80)
    duplicate_canonical = {k: v for k, v in canonical_urls.items() if len(v) > 1}
    if duplicate_canonical:
        report.append(f"\nCRITICAL: Found {len(duplicate_canonical)} duplicated Canonical URLs")
        for url, files in list(duplicate_canonical.items())[:10]:
            report.append(f"\nCANONICAL: {url}")
            report.append(f"   Used on {len(files)} pages:")
            for f in files:
                report.append(f"   - {f}")
    else:
        report.append("\nOK: All canonical URLs are unique!")
    
    # 5. Duplicates OG Title
    report.append("\n" + "=" * 80)
    report.append("5. DUPLICATED OPEN GRAPH TITLES")
    report.append("=" * 80)
    duplicate_og = {k: v for k, v in og_titles.items() if len(v) > 1}
    if duplicate_og:
        report.append(f"\nWARNING: Found {len(duplicate_og)} duplicated OG Titles")
        for og, files in list(duplicate_og.items())[:10]:
            report.append(f"\nOG: \"{og[:70]}...\"")
            report.append(f"   On {len(files)} pages")
    else:
        report.append("\nOK: All OG Title tags are unique!")
    
    # 6. Content duplication
    report.append("\n" + "=" * 80)
    report.append("6. POTENTIAL CONTENT DUPLICATION")
    report.append("=" * 80)
    duplicate_content = {k: v for k, v in text_hashes.items() if len(v) > 1}
    if duplicate_content:
        report.append(f"\nWARNING: Found {len(duplicate_content)} potential content duplicates")
        for hash_val, files_info in list(duplicate_content.items())[:10]:
            report.append(f"\nContent ({files_info[0][1]} chars):")
            for f, length in files_info[:5]:
                report.append(f"   - {f}")
    else:
        report.append("\nOK: No obvious content duplicates found!")
    
    # 7. Missing meta summary
    report.append("\n" + "=" * 80)
    report.append("7. MISSING META TAGS SUMMARY")
    report.append("=" * 80)
    missing_title = [i for i in issues if "MISSING_TITLE" in i]
    missing_desc = [i for i in issues if "MISSING_DESCRIPTION" in i]
    missing_h1 = [i for i in issues if "MISSING_H1" in i]
    
    report.append(f"\nPages without TITLE: {len(missing_title)}")
    report.append(f"Pages without DESCRIPTION: {len(missing_desc)}")
    report.append(f"Pages without H1: {len(missing_h1)}")
    
    # 8. Length analysis
    report.append("\n" + "=" * 80)
    report.append("8. TITLE & DESCRIPTION LENGTH ANALYSIS")
    report.append("=" * 80)
    
    too_short_titles = [(t, f) for t, files in titles.items() for f in files if len(t) < 30]
    too_long_titles = [(t, f) for t, files in titles.items() for f in files if len(t) > 70]
    too_short_desc = [(d, f) for d, files in descriptions.items() for f in files if len(d) < 50]
    too_long_desc = [(d, f) for d, files in descriptions.items() for f in files if len(d) > 160]
    
    report.append(f"\nTITLE Statistics:")
    report.append(f"   - Too short (<30 chars): {len(too_short_titles)}")
    report.append(f"   - Too long (>70 chars): {len(too_long_titles)}")
    report.append(f"   - Optimal (30-70 chars): {len(titles) - len(too_short_titles) - len(too_long_titles)}")
    
    report.append(f"\nDESCRIPTION Statistics:")
    report.append(f"   - Too short (<50 chars): {len(too_short_desc)}")
    report.append(f"   - Too long (>160 chars): {len(too_long_desc)}")
    report.append(f"   - Optimal (50-160 chars): {len(descriptions) - len(too_short_desc) - len(too_long_desc)}")
    
    # Summary
    report.append("\n" + "=" * 80)
    report.append("SUMMARY & RECOMMENDATIONS")
    report.append("=" * 80)
    
    critical_issues = len(duplicate_canonical) + len(missing_title)
    warnings = len(duplicate_titles) + len(duplicate_descriptions) + len(duplicate_h1) + len(duplicate_og)
    
    report.append(f"\nCritical Issues: {critical_issues}")
    report.append(f"Warnings: {warnings}")
    
    report.append("\nRECOMMENDATIONS:")
    if duplicate_canonical:
        report.append("   1. CRITICAL: Fix duplicate canonical URLs immediately")
    if duplicate_titles:
        report.append("   2. WARNING: Uniqueize duplicated TITLE tags")
    if duplicate_descriptions:
        report.append("   3. WARNING: Rewrite duplicated DESCRIPTIONs")
    if duplicate_h1:
        report.append("   4. WARNING: Review duplicated H1 headings")
    if missing_title:
        report.append("   5. CRITICAL: Add TITLE to pages missing it")
    if too_long_titles or too_short_titles:
        report.append("   6. Optimize TITLE length (30-70 characters)")
    if too_long_desc or too_short_desc:
        report.append("   7. Optimize DESCRIPTION length (50-160 characters)")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)

if __name__ == "__main__":
    report = analyze_seo_uniqueness("/workspace")
    print(report)
    
    with open("/workspace/SEO_UNIQUE_CHECK_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# SEO Uniqueness Check Report\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```")
    
    print("\n\nReport saved to: /workspace/SEO_UNIQUE_CHECK_REPORT.md")
