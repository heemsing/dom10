#!/usr/bin/env python3
"""
Полный SEO аудит HTML страниц с использованием регулярных выражений
"""
import re
import json
from pathlib import Path
from datetime import datetime

def analyze_html_file(filepath):
    """Анализ одного HTML файла с помощью regex"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Title
        title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        
        # Description (два возможных формата)
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not desc_match:
            desc_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', content, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # H1 заголовки
        h1_matches = re.findall(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        h1_tags = [h.strip() for h in h1_matches]
        
        # H2 заголовки
        h2_matches = re.findall(r'<h2[^>]*>([^<]+)</h2>', content, re.IGNORECASE)
        h2_count = len(h2_matches)
        
        # H3 заголовки
        h3_matches = re.findall(r'<h3[^>]*>([^<]+)</h3>', content, re.IGNORECASE)
        h3_count = len(h3_matches)
        
        # Canonical (два возможных формата)
        canonical_match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not canonical_match:
            canonical_match = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', content, re.IGNORECASE)
        canonical = canonical_match.group(1).strip() if canonical_match else ""
        
        # Viewport (два возможных формата)
        viewport_match = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not viewport_match:
            viewport_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']viewport["\']', content, re.IGNORECASE)
        viewport = viewport_match.group(1).strip() if viewport_match else ""
        
        # Robots
        robots_match = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not robots_match:
            robots_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']robots["\']', content, re.IGNORECASE)
        robots = robots_match.group(1).strip() if robots_match else ""
        
        # Open Graph
        og_title_match = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not og_title_match:
            og_title_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']', content, re.IGNORECASE)
        og_title = og_title_match.group(1).strip() if og_title_match else ""
        
        og_desc_match = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not og_desc_match:
            og_desc_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:description["\']', content, re.IGNORECASE)
        og_description = og_desc_match.group(1).strip() if og_desc_match else ""
        
        og_image_match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not og_image_match:
            og_image_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', content, re.IGNORECASE)
        og_image = og_image_match.group(1).strip() if og_image_match else ""
        
        # Изображения
        img_matches = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
        images_without_alt = sum(1 for img in img_matches if 'alt=' not in img.lower())
        
        # Ссылки
        internal_links = len(re.findall(r'<a[^>]*href=["\'](?:/|https?://дом-помощи\.рф|https?://localhost)[^"\']*["\']', content, re.IGNORECASE))
        external_links = len(re.findall(r'<a[^>]*href=["\']https?://(?!дом-помощи\.рф|localhost)[^"\']+["\']', content, re.IGNORECASE))
        
        # Lang атрибут
        lang_match = re.search(r'<html[^>]*\slang=["\']([^"\']+)["\']', content, re.IGNORECASE)
        lang = lang_match.group(1) if lang_match else ""
        
        # Charset
        charset_match = re.search(r'charset=["\']?([^"\'>\s]+)', content, re.IGNORECASE)
        charset = charset_match.group(1) if charset_match else ""
        
        # Word count (текст без тегов)
        text_only = re.sub(r'<[^>]+>', ' ', content)
        word_count = len(text_only.split())
        
        return {
            "file": str(filepath),
            "url_path": str(filepath).replace("/workspace", "").replace("index.html", ""),
            "title": title,
            "title_length": len(title),
            "description": description,
            "description_length": len(description),
            "h1_count": len(h1_tags),
            "h1_tags": h1_tags,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "canonical": canonical,
            "viewport": viewport,
            "robots": robots,
            "og_title": og_title,
            "og_description": og_description,
            "og_image": og_image,
            "total_images": len(img_matches),
            "images_without_alt": images_without_alt,
            "internal_links": internal_links,
            "external_links": external_links,
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
    
    print(f"🔍 Найдено HTML файлов: {len(html_files)}")
    print("⏳ Начинаю полный SEO анализ...")
    
    results = []
    for i, filepath in enumerate(html_files, 1):
        result = analyze_html_file(filepath)
        results.append(result)
        if i % 100 == 0:
            print(f"   Обработано {i}/{len(html_files)} файлов")
    
    # Статистика
    total_pages = len(results)
    error_pages = sum(1 for r in results if r.get("has_errors"))
    valid_pages = total_pages - error_pages
    
    # Критические параметры
    no_title = sum(1 for r in results if not r.get("title") and not r.get("has_errors"))
    no_desc = sum(1 for r in results if not r.get("description") and not r.get("has_errors"))
    no_h1 = sum(1 for r in results if r.get("h1_count", 0) == 0 and not r.get("has_errors"))
    multi_h1 = sum(1 for r in results if r.get("h1_count", 0) > 1 and not r.get("has_errors"))
    no_canonical = sum(1 for r in results if not r.get("canonical") and not r.get("has_errors"))
    no_viewport = sum(1 for r in results if not r.get("viewport") and not r.get("has_errors"))
    short_content = sum(1 for r in results if r.get("word_count", 0) < 200 and not r.get("has_errors"))
    
    # Изображения и ссылки
    total_images = sum(r.get("total_images", 0) for r in results)
    imgs_no_alt = sum(r.get("images_without_alt", 0) for r in results)
    total_internal = sum(r.get("internal_links", 0) for r in results)
    total_external = sum(r.get("external_links", 0) for r in results)
    
    # Длина мета-тегов
    long_titles = sum(1 for r in results if r.get("title_length", 0) > 70 and not r.get("has_errors"))
    short_titles = sum(1 for r in results if 0 < r.get("title_length", 0) < 30 and not r.get("has_errors"))
    long_descs = sum(1 for r in results if r.get("description_length", 0) > 160 and not r.get("has_errors"))
    short_descs = sum(1 for r in results if 0 < r.get("description_length", 0) < 70 and not r.get("has_errors"))
    
    # Open Graph
    no_og_title = sum(1 for r in results if not r.get("og_title") and not r.get("has_errors"))
    no_og_desc = sum(1 for r in results if not r.get("og_description") and not r.get("has_errors"))
    no_og_image = sum(1 for r in results if not r.get("og_image") and not r.get("has_errors"))
    
    # Технические параметры
    no_lang = sum(1 for r in results if not r.get("lang") and not r.get("has_errors"))
    no_charset = sum(1 for r in results if not r.get("charset") and not r.get("has_errors"))
    no_robots = sum(1 for r in results if not r.get("robots") and not r.get("has_errors"))
    
    stats = {
        "total_pages": total_pages,
        "valid_pages": valid_pages,
        "error_pages": error_pages,
        "no_title": no_title,
        "no_description": no_desc,
        "no_h1": no_h1,
        "multi_h1": multi_h1,
        "no_canonical": no_canonical,
        "no_viewport": no_viewport,
        "short_content": short_content,
        "total_images": total_images,
        "images_without_alt": imgs_no_alt,
        "total_internal_links": total_internal,
        "total_external_links": total_external,
        "long_titles": long_titles,
        "short_titles": short_titles,
        "long_descriptions": long_descs,
        "short_descriptions": short_descs,
        "no_og_title": no_og_title,
        "no_og_description": no_og_desc,
        "no_og_image": no_og_image,
        "no_lang": no_lang,
        "no_charset": no_charset,
        "no_robots": no_robots
    }
    
    # Сохраняем результаты
    with open("/workspace/complete_seo_analysis.json", "w", encoding="utf-8") as f:
        json.dump({"statistics": stats, "pages": results}, f, ensure_ascii=False, indent=2)
    
    # Вывод отчета
    print("\n" + "="*70)
    print(" " * 20 + "📊 ПОЛНЫЙ SEO АНАЛИЗ САЙТА")
    print("="*70)
    print(f"\n📁 ВСЕГО СТРАНИЦ: {total_pages}")
    print(f"   ✓ Успешно проанализировано: {valid_pages}")
    print(f"   ✗ Ошибки парсинга: {error_pages}")
    
    print("\n" + "-"*70)
    print("✅ КРИТИЧЕСКИЕ SEO ПАРАМЕТРЫ:")
    print("-"*70)
    def status_badge(count, total, inverse=False):
        pct = (count/total*100) if total > 0 else 0
        if inverse:
            return "✅" if pct == 0 else ("⚠️" if pct < 10 else "🔴")
        return "✅" if pct == 0 else ("⚠️" if pct < 10 else "🔴")
    
    print(f"  {status_badge(no_title, valid_pages)} Страниц без Title: {no_title} ({no_title/valid_pages*100:.1f}%)")
    print(f"  {status_badge(no_desc, valid_pages)} Страниц без Description: {no_desc} ({no_desc/valid_pages*100:.1f}%)")
    print(f"  {status_badge(no_h1, valid_pages)} Страниц без H1: {no_h1} ({no_h1/valid_pages*100:.1f}%)")
    print(f"  {status_badge(multi_h1, valid_pages, inverse=True)} Страниц с несколькими H1: {multi_h1}")
    print(f"  {status_badge(no_canonical, valid_pages)} Страниц без Canonical: {no_canonical} ({no_canonical/valid_pages*100:.1f}%)")
    print(f"  {status_badge(no_viewport, valid_pages)} Страниц без Viewport: {no_viewport} ({no_viewport/valid_pages*100:.1f}%)")
    print(f"  ⚠️ Страниц с малым контентом (<200 слов): {short_content}")
    
    print("\n" + "-"*70)
    print("🖼️ ИЗОБРАЖЕНИЯ И ССЫЛКИ:")
    print("-"*70)
    print(f"  📸 Всего изображений: {total_images}")
    if total_images > 0:
        alt_pct = imgs_no_alt/total_images*100
        badge = "✅" if alt_pct == 0 else ("⚠️" if alt_pct < 20 else "🔴")
        print(f"  {badge} Изображений без alt: {imgs_no_alt} ({alt_pct:.1f}%)")
    print(f"  🔗 Внутренних ссылок: {total_internal}")
    print(f"  🌐 Внешних ссылок: {total_external}")
    
    print("\n" + "-"*70)
    print("📝 ОПТИМИЗАЦИЯ МЕТА-ТЕГОВ:")
    print("-"*70)
    print(f"  {'⚠️' if long_titles > 0 else '✅'} Длинный Title (>70 симв): {long_titles} ({long_titles/valid_pages*100:.1f}%)")
    print(f"  {'⚠️' if short_titles > 0 else '✅'} Короткий Title (<30 симв): {short_titles}")
    print(f"  {'⚠️' if long_descs > 0 else '✅'} Длинный Description (>160 симв): {long_descs} ({long_descs/valid_pages*100:.1f}%)")
    print(f"  {'⚠️' if short_descs > 0 else '✅'} Короткий Description (<70 симв): {short_descs}")
    
    print("\n" + "-"*70)
    print("🌐 OPEN GRAPH РАЗМЕТКА:")
    print("-"*70)
    print(f"  {'✅' if no_og_title == 0 else '⚠️'} Страниц без og:title: {no_og_title}")
    print(f"  {'✅' if no_og_desc == 0 else '⚠️'} Страниц без og:description: {no_og_desc}")
    print(f"  {'✅' if no_og_image == 0 else '⚠️'} Страниц без og:image: {no_og_image}")
    
    print("\n" + "-"*70)
    print("⚙️ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ:")
    print("-"*70)
    print(f"  {'✅' if no_lang == 0 else '⚠️'} Страниц без lang атрибута: {no_lang}")
    print(f"  {'✅' if no_charset == 0 else '⚠️'} Страниц без charset: {no_charset}")
    print(f"  {'✅' if no_robots == 0 else '⚠️'} Страниц без robots meta: {no_robots}")
    
    # Оценка
    print("\n" + "="*70)
    print("📈 ОБЩАЯ ОЦЕНКА SEO:")
    print("="*70)
    
    score = 100
    score -= min(no_title/valid_pages*100, 20) * 2  # Max -20
    score -= min(no_desc/valid_pages*100, 20) * 2  # Max -20
    score -= min(no_h1/valid_pages*100, 15) * 1.5  # Max -15
    score -= min(long_titles/valid_pages*100, 15) * 0.5  # Max -7.5
    score -= min(long_descs/valid_pages*100, 15) * 0.5  # Max -7.5
    score -= min(imgs_no_alt/(total_images if total_images > 0 else 1)*100, 15) * 0.5  # Max -7.5
    
    score = max(0, min(100, score))
    
    if score >= 90:
        grade = "ОТЛИЧНО" 
        emoji = "⭐⭐⭐⭐⭐"
    elif score >= 75:
        grade = "ХОРОШО"
        emoji = "⭐⭐⭐⭐"
    elif score >= 60:
        grade = "УДОВЛЕТВОРИТЕЛЬНО"
        emoji = "⭐⭐⭐"
    elif score >= 40:
        grade = "ТРЕБУЕТ УЛУЧШЕНИЙ"
        emoji = "⭐⭐"
    else:
        grade = "КРИТИЧЕСКОЕ СОСТОЯНИЕ"
        emoji = "⭐"
    
    print(f"\n  {emoji} {score:.1f}/100 — {grade}")
    
    print("\n" + "="*70)
    print(f"💾 Детальные данные сохранены: /workspace/complete_seo_analysis.json")
    print("="*70)
    
    return stats

if __name__ == "__main__":
    main()
