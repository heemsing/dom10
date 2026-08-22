#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Analysis Script for дом-помощи.рф
Analyzes all HTML pages for SEO metrics
"""

import os
import re
from html.parser import HTMLParser
from collections import defaultdict
import json

class SEOHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.keywords = ""
        self.canonical = ""
        self.og_title = ""
        self.og_description = ""
        self.og_image = ""
        self.h1_tags = []
        self.h2_tags = []
        self.h3_tags = []
        self.images_without_alt = []
        self.images_count = 0
        self.links_internal = 0
        self.links_external = 0
        self.in_title = False
        self.in_h1 = False
        self.in_h2 = False
        self.in_h3 = False
        self.current_h1 = ""
        self.current_h2 = ""
        self.current_h3 = ""
        self.meta_robots = ""
        self.viewport = ""
        self.lang = ""
        self.body_text_length = 0
        self.in_body = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == "title":
            self.in_title = True
            
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            property_val = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            
            if name == "description":
                self.description = content
            elif name == "keywords":
                self.keywords = content
            elif name == "robots":
                self.meta_robots = content
            elif property_val == "og:title":
                self.og_title = content
            elif property_val == "og:description":
                self.og_description = content
            elif property_val == "og:image":
                self.og_image = content
            elif attrs_dict.get("name", "").lower() == "viewport":
                self.viewport = content
                
        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            if rel == "canonical":
                self.canonical = attrs_dict.get("href", "")
                
        elif tag == "h1":
            self.in_h1 = True
            self.current_h1 = ""
            
        elif tag == "h2":
            self.in_h2 = True
            self.current_h2 = ""
            
        elif tag == "h3":
            self.in_h3 = True
            self.current_h3 = ""
            
        elif tag == "img":
            self.images_count += 1
            alt = attrs_dict.get("alt", "")
            if not alt or alt.strip() == "":
                src = attrs_dict.get("src", "unknown")
                self.images_without_alt.append(src)
                
        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                if href.startswith("http") and "дом-помощи.рф" not in href and "dom-pomoshi" not in href:
                    self.links_external += 1
                else:
                    self.links_internal += 1
                    
        elif tag == "body":
            self.in_body = True
            lang = attrs_dict.get("lang", "")
            if lang:
                self.lang = lang
                
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            
        elif tag == "h1":
            self.in_h1 = False
            if self.current_h1.strip():
                self.h1_tags.append(self.current_h1.strip())
                
        elif tag == "h2":
            self.in_h2 = False
            if self.current_h2.strip():
                self.h2_tags.append(self.current_h2.strip())
                
        elif tag == "h3":
            self.in_h3 = False
            if self.current_h3.strip():
                self.h3_tags.append(self.current_h3.strip())
                
        elif tag == "body":
            self.in_body = False
            
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_h1:
            self.current_h1 += data
        elif self.in_h2:
            self.current_h2 += data
        elif self.in_h3:
            self.current_h3 += data
        elif self.in_body:
            # Count body text (simplified)
            text = data.strip()
            if text:
                self.body_text_length += len(text)

def analyze_file(filepath):
    """Analyze a single HTML file for SEO metrics"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}
    
    parser = SEOHTMLParser()
    try:
        parser.feed(content)
    except Exception as e:
        return {"error": str(e)}
    
    # Calculate issues
    issues = []
    
    # Title checks
    title_len = len(parser.title.strip())
    if title_len == 0:
        issues.append("CRITICAL: Отсутствует title")
    elif title_len < 30:
        issues.append("WARNING: Title слишком короткий (< 30 символов)")
    elif title_len > 70:
        issues.append("WARNING: Title слишком длинный (> 70 символов)")
    
    # Description checks
    desc_len = len(parser.description.strip())
    if desc_len == 0:
        issues.append("CRITICAL: Отсутствует meta description")
    elif desc_len < 50:
        issues.append("WARNING: Description слишком короткий (< 50 символов)")
    elif desc_len > 160:
        issues.append("WARNING: Description слишком длинный (> 160 символов)")
    
    # H1 checks
    if len(parser.h1_tags) == 0:
        issues.append("CRITICAL: Отсутствует H1 заголовок")
    elif len(parser.h1_tags) > 1:
        issues.append(f"WARNING: Несколько H1 заголовков ({len(parser.h1_tags)})")
    
    # Canonical check
    if not parser.canonical:
        issues.append("INFO: Отсутствует canonical URL")
    
    # Open Graph checks
    if not parser.og_title:
        issues.append("INFO: Отсутствует og:title")
    if not parser.og_description:
        issues.append("INFO: Отсутствует og:description")
    if not parser.og_image:
        issues.append("INFO: Отсутствует og:image")
    
    # Images check
    if parser.images_without_alt:
        issues.append(f"WARNING: {len(parser.images_without_alt)} изображений без alt атрибута")
    
    # Viewport check
    if not parser.viewport:
        issues.append("WARNING: Отсутствует viewport meta tag")
    
    # Body text check
    if parser.body_text_length < 300:
        issues.append("WARNING: Мало текстового контента (< 300 символов)")
    
    return {
        "title": parser.title.strip(),
        "title_length": title_len,
        "description": parser.description.strip(),
        "description_length": desc_len,
        "keywords": parser.keywords.strip(),
        "canonical": parser.canonical,
        "h1_count": len(parser.h1_tags),
        "h1_tags": parser.h1_tags,
        "h2_count": len(parser.h2_tags),
        "h3_count": len(parser.h3_tags),
        "images_total": parser.images_count,
        "images_without_alt_count": len(parser.images_without_alt),
        "links_internal": parser.links_internal,
        "links_external": parser.links_external,
        "meta_robots": parser.meta_robots,
        "viewport": parser.viewport,
        "lang": parser.lang,
        "body_text_length": parser.body_text_length,
        "og_title": parser.og_title,
        "og_description": parser.og_description,
        "og_image": parser.og_image,
        "issues": issues
    }

def get_relative_path(filepath, base_path):
    """Get relative path from base"""
    return os.path.relpath(filepath, base_path)

def main():
    base_path = "/workspace"
    html_files = []
    
    # Find all HTML files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.html', '.htm', '.php')):
                # Skip Google verification file
                if not file.startswith('google'):
                    html_files.append(os.path.join(root, file))
    
    print("=" * 120)
    print("SEO АНАЛИЗ САЙТА дом-помощи.рф")
    print("=" * 120)
    print(f"\nВсего страниц для анализа: {len(html_files)}\n")
    
    results = []
    critical_issues = []
    warnings = []
    
    # Analyze each file
    for filepath in sorted(html_files):
        rel_path = get_relative_path(filepath, base_path)
        result = analyze_file(filepath)
        result['file_path'] = rel_path
        results.append(result)
        
        # Collect critical issues
        for issue in result.get('issues', []):
            if issue.startswith("CRITICAL"):
                critical_issues.append((rel_path, issue))
            elif issue.startswith("WARNING"):
                warnings.append((rel_path, issue))
    
    # Summary statistics
    pages_without_title = sum(1 for r in results if r.get('title_length', 0) == 0)
    pages_without_description = sum(1 for r in results if r.get('description_length', 0) == 0)
    pages_without_h1 = sum(1 for r in results if r.get('h1_count', 0) == 0)
    pages_multiple_h1 = sum(1 for r in results if r.get('h1_count', 0) > 1)
    pages_without_canonical = sum(1 for r in results if not r.get('canonical'))
    pages_with_images_no_alt = sum(1 for r in results if r.get('images_without_alt_count', 0) > 0)
    pages_without_viewport = sum(1 for r in results if not r.get('viewport'))
    pages_low_content = sum(1 for r in results if r.get('body_text_length', 0) < 300)
    pages_without_og_title = sum(1 for r in results if not r.get('og_title'))
    pages_without_og_description = sum(1 for r in results if not r.get('og_description'))
    pages_without_og_image = sum(1 for r in results if not r.get('og_image'))
    
    total_images = sum(r.get('images_total', 0) for r in results)
    total_images_no_alt = sum(r.get('images_without_alt_count', 0) for r in results)
    total_internal_links = sum(r.get('links_internal', 0) for r in results)
    total_external_links = sum(r.get('links_external', 0) for r in results)
    
    print("=" * 120)
    print("СВОДНАЯ СТАТИСТИКА")
    print("=" * 120)
    print(f"\n📊 Общие показатели:")
    print(f"   Всего страниц: {len(results)}")
    print(f"   Страниц с критическими ошибками: {len(critical_issues)}")
    print(f"   Страниц с предупреждениями: {len(warnings)}")
    
    print(f"\n📝 Meta-теги:")
    print(f"   Страниц без Title: {pages_without_title} ({pages_without_title*100//len(results) if results else 0}%)")
    print(f"   Страниц без Description: {pages_without_description} ({pages_without_description*100//len(results) if results else 0}%)")
    print(f"   Страниц без H1: {pages_without_h1} ({pages_without_h1*100//len(results) if results else 0}%)")
    print(f"   Страниц с несколькими H1: {pages_multiple_h1}")
    print(f"   Страниц без Canonical: {pages_without_canonical} ({pages_without_canonical*100//len(results) if results else 0}%)")
    
    print(f"\n🖼️ Изображения:")
    print(f"   Всего изображений: {total_images}")
    print(f"   Изображений без alt: {total_images_no_alt} ({total_images_no_alt*100//total_images if total_images else 0}%)")
    print(f"   Страниц с изображениями без alt: {pages_with_images_no_alt}")
    
    print(f"\n📱 Мобильная оптимизация:")
    print(f"   Страниц без viewport: {pages_without_viewport}")
    
    print(f"\n🔗 Ссылки:")
    print(f"   Внутренних ссылок: {total_internal_links}")
    print(f"   Внешних ссылок: {total_external_links}")
    
    print(f"\n📄 Контент:")
    print(f"   Страниц с малым количеством текста (<300 символов): {pages_low_content}")
    
    print(f"\n🌐 Open Graph:")
    print(f"   Страниц без og:title: {pages_without_og_title}")
    print(f"   Страниц без og:description: {pages_without_og_description}")
    print(f"   Страниц без og:image: {pages_without_og_image}")
    
    # Detailed report by page type
    print("\n" + "=" * 120)
    print("ДЕТАЛЬНЫЙ АНАЛИЗ ПО СТРАНИЦАМ С КРИТИЧЕСКИМИ ПРОБЛЕМАМИ")
    print("=" * 120)
    
    if critical_issues:
        print(f"\n⚠️  КРИТИЧЕСКИЕ ОШИБКИ ({len(critical_issues)}):")
        for filepath, issue in sorted(critical_issues, key=lambda x: x[0]):
            print(f"   ❌ {filepath}")
            print(f"      → {issue}")
    else:
        print("\n✅ Критических ошибок не найдено!")
    
    # Sample of pages with warnings
    print("\n" + "=" * 120)
    print("ПРИМЕРЫ СТРАНИЦ С ПРЕДУПРЕЖДЕНИЯМИ (первые 30)")
    print("=" * 120)
    
    warning_by_page = defaultdict(list)
    for filepath, issue in warnings:
        warning_by_page[filepath].append(issue)
    
    for i, (filepath, issues_list) in enumerate(sorted(warning_by_page.items())):
        if i >= 30:
            break
        print(f"\n📄 {filepath}:")
        for issue in issues_list[:5]:  # Show max 5 issues per page
            print(f"   ⚠️  {issue}")
    
    # Title analysis
    print("\n" + "=" * 120)
    print("АНАЛИЗ TITLE ТЕГОВ")
    print("=" * 120)
    
    titles_too_short = [(r['file_path'], r['title'], r['title_length']) for r in results if 0 < r.get('title_length', 0) < 30]
    titles_too_long = [(r['file_path'], r['title'], r['title_length']) for r in results if r.get('title_length', 0) > 70]
    
    if titles_too_short:
        print(f"\n📏 Слишком короткие Title (< 30 символов) - {len(titles_too_short)} страниц:")
        for path, title, length in titles_too_short[:10]:
            print(f"   • {path}: '{title[:50]}...' ({length} симв.)")
    
    if titles_too_long:
        print(f"\n📏 Слишком длинные Title (> 70 символов) - {len(titles_too_long)} страниц:")
        for path, title, length in titles_too_long[:10]:
            print(f"   • {path}: '{title[:50]}...' ({length} симв.)")
    
    # Description analysis
    print("\n" + "=" * 120)
    print("АНАЛИЗ DESCRIPTION ТЕГОВ")
    print("=" * 120)
    
    desc_too_short = [(r['file_path'], r['description'], r['description_length']) for r in results if 0 < r.get('description_length', 0) < 50]
    desc_too_long = [(r['file_path'], r['description'], r['description_length']) for r in results if r.get('description_length', 0) > 160]
    
    if desc_too_short:
        print(f"\n📏 Слишком короткие Description (< 50 символов) - {len(desc_too_short)} страниц:")
        for path, desc, length in desc_too_short[:10]:
            print(f"   • {path}: '{desc[:50]}...' ({length} симв.)")
    
    if desc_too_long:
        print(f"\n📏 Слишком длинные Description (> 160 символов) - {len(desc_too_long)} страниц:")
        for path, desc, length in desc_too_long[:10]:
            print(f"   • {path}: '{desc[:50]}...' ({length} симв.)")
    
    # H1 analysis
    print("\n" + "=" * 120)
    print("АНАЛИЗ H1 ЗАГОЛОВКОВ")
    print("=" * 120)
    
    pages_no_h1 = [r['file_path'] for r in results if r.get('h1_count', 0) == 0]
    pages_multi_h1 = [(r['file_path'], r['h1_tags']) for r in results if r.get('h1_count', 0) > 1]
    
    if pages_no_h1:
        print(f"\n❌ Страницы без H1 - {len(pages_no_h1)}:")
        for path in pages_no_h1[:15]:
            print(f"   • {path}")
    
    if pages_multi_h1:
        print(f"\n⚠️  Страницы с несколькими H1 - {len(pages_multi_h1)}:")
        for path, h1s in pages_multi_h1[:10]:
            print(f"   • {path}: {h1s}")
    
    # Recommendations
    print("\n" + "=" * 120)
    print("РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ SEO")
    print("=" * 120)
    
    recommendations = []
    
    if pages_without_title > 0:
        recommendations.append(f"1. 🔴 ВЫСОКИЙ ПРИОРИТЕТ: Добавить уникальные Title для {pages_without_title} страниц")
    
    if pages_without_description > 0:
        recommendations.append(f"2. 🔴 ВЫСОКИЙ ПРИОРИТЕТ: Добавить meta Description для {pages_without_description} страниц")
    
    if pages_without_h1 > 0:
        recommendations.append(f"3. 🔴 ВЫСОКИЙ ПРИОРИТЕТ: Добавить H1 заголовки для {pages_without_h1} страниц")
    
    if total_images_no_alt > 0:
        recommendations.append(f"4. 🟡 СРЕДНИЙ ПРИОРИТЕТ: Добавить alt атрибуты для {total_images_no_alt} изображений")
    
    if pages_without_canonical > 0:
        recommendations.append(f"5. 🟡 СРЕДНИЙ ПРИОРИТЕТ: Добавить canonical URL для {pages_without_canonical} страниц")
    
    if pages_without_og_title > 0 or pages_without_og_description > 0:
        recommendations.append(f"6. 🟢 НИЗКИЙ ПРИОРИТЕТ: Добавить Open Graph разметку для социальных сетей")
    
    if pages_low_content > 0:
        recommendations.append(f"7. 🟡 СРЕДНИЙ ПРИОРИТЕТ: Увеличить количество контента на {pages_low_content} страницах")
    
    if titles_too_short or titles_too_long:
        recommendations.append(f"8. 🟡 СРЕДНИЙ ПРИОРИТЕТ: Оптимизировать длину Title (оптимально 50-70 символов)")
    
    if desc_too_short or desc_too_long:
        recommendations.append(f"9. 🟡 СРЕДНИЙ ПРИОРИТЕТ: Оптимизировать длину Description (оптимально 150-160 символов)")
    
    for rec in recommendations:
        print(f"\n{rec}")
    
    if not recommendations:
        print("\n✅ Все основные SEO параметры в порядке!")
    
    # Save detailed report to JSON
    report_data = {
        "summary": {
            "total_pages": len(results),
            "pages_without_title": pages_without_title,
            "pages_without_description": pages_without_description,
            "pages_without_h1": pages_without_h1,
            "pages_with_multiple_h1": pages_multiple_h1,
            "pages_without_canonical": pages_without_canonical,
            "total_images": total_images,
            "images_without_alt": total_images_no_alt,
            "pages_without_viewport": pages_without_viewport,
            "pages_low_content": pages_low_content,
            "critical_issues_count": len(critical_issues),
            "warnings_count": len(warnings)
        },
        "detailed_results": results,
        "critical_issues": critical_issues,
        "recommendations": recommendations
    }
    
    report_path = "/workspace/seo_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 120}")
    print(f"📁 Полный отчет сохранен в: {report_path}")
    print(f"{'=' * 120}\n")

if __name__ == "__main__":
    main()
