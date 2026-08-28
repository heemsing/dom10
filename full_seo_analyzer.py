#!/usr/bin/env python3
"""
Полный SEO анализатор HTML страниц
"""
import os
import re
import json
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime

class SEOAnalyzer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset_data()
        
    def reset_data(self):
        self.title = ""
        self.description = ""
        self.h1_tags = []
        self.h2_tags = []
        self.h3_tags = []
        self.canonical = ""
        self.viewport = ""
        self.robots = ""
        self.og_title = ""
        self.og_description = ""
        self.og_image = ""
        self.images = []
        self.internal_links = 0
        self.external_links = 0
        self.text_content = ""
        self.current_tag = None
        self.in_title = False
        self.in_h1 = False
        self.in_h2 = False
        self.in_h3 = False
        self.charset = ""
        self.lang = ""
        
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
            elif name == "viewport":
                self.viewport = content
            elif name == "robots":
                self.robots = content
            elif property_val == "og:title":
                self.og_title = content
            elif property_val == "og:description":
                self.og_description = content
            elif property_val == "og:image":
                self.og_image = content
                
            # Check charset
            http_equiv = attrs_dict.get("http-equiv", "").lower()
            if http_equiv == "content-type" and "charset" in content.lower():
                self.charset = content
            elif name == "charset":
                self.charset = content
                
        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            if rel == "canonical":
                self.canonical = attrs_dict.get("href", "")
                
        elif tag in ["h1", "h2", "h3"]:
            self.current_tag = tag
            
        elif tag == "img":
            img_info = {
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", None)
            }
            self.images.append(img_info)
            
        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                if href.startswith("http") and not href.startswith("http://дом-помощи.рф") and not href.startswith("https://дом-помощи.рф"):
                    self.external_links += 1
                else:
                    self.internal_links += 1
                    
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.current_tag = None
        elif tag == "h2":
            self.current_tag = None
        elif tag == "h3":
            self.current_tag = None
            
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.current_tag == "h1":
            self.h1_tags.append(data.strip())
        elif self.current_tag == "h2":
            self.h2_tags.append(data.strip())
        elif self.current_tag == "h3":
            self.h3_tags.append(data.strip())
        
        # Collect text content (simplified)
        if self.current_tag is None and tag not in ["script", "style"]:
            self.text_content += data

def analyze_file(filepath):
    """Анализ одного HTML файла"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract lang attribute from html tag
        lang_match = re.search(r'<html[^>]*\slang=["\']([^"\']+)["\']', content, re.IGNORECASE)
        lang = lang_match.group(1) if lang_match else ""
        
        # Extract charset
        charset_match = re.search(r'charset=["\']?([^"\'>\s]+)', content, re.IGNORECASE)
        charset = charset_match.group(1) if charset_match else ""
        
        analyzer = SEOAnalyzer()
        analyzer.lang = lang
        analyzer.charset = charset
        analyzer.feed(content)
        
        # Calculate metrics
        title_length = len(analyzer.title.strip())
        desc_length = len(analyzer.description.strip())
        images_without_alt = sum(1 for img in analyzer.images if img["alt"] is None or img["alt"].strip() == "")
        word_count = len(analyzer.text_content.split())
        
        return {
            "file": str(filepath),
            "url_path": str(filepath).replace("/workspace", "").replace("index.html", ""),
            "title": analyzer.title.strip(),
            "title_length": title_length,
            "description": analyzer.description.strip(),
            "description_length": desc_length,
            "h1_count": len(analyzer.h1_tags),
            "h1_tags": analyzer.h1_tags,
            "h2_count": len(analyzer.h2_tags),
            "h3_count": len(analyzer.h3_tags),
            "canonical": analyzer.canonical,
            "viewport": analyzer.viewport,
            "robots": analyzer.robots,
            "og_title": analyzer.og_title,
            "og_description": analyzer.og_description,
            "og_image": analyzer.og_image,
            "total_images": len(analyzer.images),
            "images_without_alt": images_without_alt,
            "internal_links": analyzer.internal_links,
            "external_links": analyzer.external_links,
            "word_count": word_count,
            "charset": charset,
            "lang": lang,
            "has_errors": False
        }
    except Exception as e:
        return {
            "file": str(filepath),
            "has_errors": True,
            "error": str(e)
        }

def main():
    workspace = Path("/workspace")
    html_files = list(workspace.rglob("*.html"))
    
    print(f"Найдено HTML файлов: {len(html_files)}")
    print("Начинаю анализ...")
    
    results = []
    for i, filepath in enumerate(html_files):
        if i % 50 == 0:
            print(f"Обработано {i}/{len(html_files)} файлов")
        result = analyze_file(filepath)
        results.append(result)
    
    # Generate statistics
    total_pages = len(results)
    pages_without_title = sum(1 for r in results if not r.get("title") and not r.get("has_errors"))
    pages_without_desc = sum(1 for r in results if not r.get("description") and not r.get("has_errors"))
    pages_without_h1 = sum(1 for r in results if r.get("h1_count", 0) == 0 and not r.get("has_errors"))
    pages_multiple_h1 = sum(1 for r in results if r.get("h1_count", 0) > 1 and not r.get("has_errors"))
    pages_without_canonical = sum(1 for r in results if not r.get("canonical") and not r.get("has_errors"))
    pages_without_viewport = sum(1 for r in results if not r.get("viewport") and not r.get("has_errors"))
    pages_short_content = sum(1 for r in results if r.get("word_count", 0) < 200 and not r.get("has_errors"))
    
    total_images = sum(r.get("total_images", 0) for r in results)
    images_without_alt = sum(r.get("images_without_alt", 0) for r in results)
    total_internal_links = sum(r.get("internal_links", 0) for r in results)
    total_external_links = sum(r.get("external_links", 0) for r in results)
    
    pages_without_og_title = sum(1 for r in results if not r.get("og_title") and not r.get("has_errors"))
    pages_without_og_desc = sum(1 for r in results if not r.get("og_description") and not r.get("has_errors"))
    pages_without_og_image = sum(1 for r in results if not r.get("og_image") and not r.get("has_errors"))
    
    # Title/Description length analysis
    long_titles = sum(1 for r in results if r.get("title_length", 0) > 70 and not r.get("has_errors"))
    short_titles = sum(1 for r in results if 0 < r.get("title_length", 0) < 30 and not r.get("has_errors"))
    long_descriptions = sum(1 for r in results if r.get("description_length", 0) > 160 and not r.get("has_errors"))
    short_descriptions = sum(1 for r in results if 0 < r.get("description_length", 0) < 70 and not r.get("has_errors"))
    
    # Missing lang/charset
    pages_without_lang = sum(1 for r in results if not r.get("lang") and not r.get("has_errors"))
    pages_without_charset = sum(1 for r in results if not r.get("charset") and not r.get("has_errors"))
    
    stats = {
        "total_pages": total_pages,
        "pages_with_errors": sum(1 for r in results if r.get("has_errors")),
        "pages_without_title": pages_without_title,
        "pages_without_description": pages_without_desc,
        "pages_without_h1": pages_without_h1,
        "pages_multiple_h1": pages_multiple_h1,
        "pages_without_canonical": pages_without_canonical,
        "pages_without_viewport": pages_without_viewport,
        "pages_short_content": pages_short_content,
        "total_images": total_images,
        "images_without_alt": images_without_alt,
        "total_internal_links": total_internal_links,
        "total_external_links": total_external_links,
        "pages_without_og_title": pages_without_og_title,
        "pages_without_og_description": pages_without_og_desc,
        "pages_without_og_image": pages_without_og_image,
        "long_titles": long_titles,
        "short_titles": short_titles,
        "long_descriptions": long_descriptions,
        "short_descriptions": short_descriptions,
        "pages_without_lang": pages_without_lang,
        "pages_without_charset": pages_without_charset
    }
    
    # Save detailed results
    with open("/workspace/full_seo_analysis.json", "w", encoding="utf-8") as f:
        json.dump({"statistics": stats, "pages": results}, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 СВОДНАЯ СТАТИСТИКА SEO АНАЛИЗА")
    print("="*60)
    print(f"Всего страниц проанализировано: {total_pages}")
    print(f"Страниц с ошибками парсинга: {stats['pages_with_errors']}")
    print()
    print("✅ КРИТИЧЕСКИЕ ПАРАМЕТРЫ:")
    print(f"  Страниц без Title: {pages_without_title} ({pages_without_title/total_pages*100:.1f}%)")
    print(f"  Страниц без Description: {pages_without_desc} ({pages_without_desc/total_pages*100:.1f}%)")
    print(f"  Страниц без H1: {pages_without_h1} ({pages_without_h1/total_pages*100:.1f}%)")
    print(f"  Страниц с несколькими H1: {pages_multiple_h1}")
    print(f"  Страниц без Canonical: {pages_without_canonical} ({pages_without_canonical/total_pages*100:.1f}%)")
    print(f"  Страниц без Viewport: {pages_without_viewport} ({pages_without_viewport/total_pages*100:.1f}%)")
    print()
    print("🖼️ ИЗОБРАЖЕНИЯ И ССЫЛКИ:")
    print(f"  Всего изображений: {total_images}")
    print(f"  Изображений без alt: {images_without_alt} ({images_without_alt/total_images*100:.1f}%)" if total_images > 0 else "  Изображений нет")
    print(f"  Внутренних ссылок: {total_internal_links}")
    print(f"  Внешних ссылок: {total_external_links}")
    print()
    print("📝 META-ТЕГИ:")
    print(f"  Страниц с длинным Title (>70): {long_titles} ({long_titles/total_pages*100:.1f}%)")
    print(f"  Страниц с коротким Title (<30): {short_titles}")
    print(f"  Страниц с длинным Description (>160): {long_descriptions} ({long_descriptions/total_pages*100:.1f}%)")
    print(f"  Страниц с коротким Description (<70): {short_descriptions}")
    print()
    print("🌐 OPEN GRAPH:")
    print(f"  Страниц без og:title: {pages_without_og_title}")
    print(f"  Страниц без og:description: {pages_without_og_desc}")
    print(f"  Страниц без og:image: {pages_without_og_image}")
    print()
    print("⚙️ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ:")
    print(f"  Страниц без lang атрибута: {pages_without_lang}")
    print(f"  Страниц без charset: {pages_without_charset}")
    print()
    print(f"💾 Детальные результаты сохранены в: /workspace/full_seo_analysis.json")
    
    return stats

if __name__ == "__main__":
    main()
