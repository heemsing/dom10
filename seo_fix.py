#!/usr/bin/env python3
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

ADRESA_DIR = "/workspace/adresa"

def get_all_files():
    return sorted(Path(ADRESA_DIR).glob("*.html"))

def extract_city_name(filepath):
    # Извлекаем название города из имени файла
    # rabochij-dom-saburovo.html -> saburovo
    match = re.search(r'rabochij-dom-(.+)\.html', filepath.name)
    if match:
        return match.group(1)
    return None

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_main_content(html):
    """Извлекаем основной текстовый контент между <main> и </main>"""
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL | re.IGNORECASE)
    if main_match:
        main_content = main_match.group(1)
        # Удаляем HTML теги, оставляем только текст
        text = re.sub(r'<script[^>]*>.*?</script>', '', main_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        # Нормализуем пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ""

def extract_geo_position(html):
    """Извлекаем geo.position координаты"""
    match = re.search(r'<meta name="geo\.position" content="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def extract_h1(html):
    """Извлекаем H1 заголовок"""
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if match:
        return re.sub(r'<[^>]+>', '', match.group(1)).strip()
    return None

def similarity(a, b):
    """Вычисляет схожесть двух строк"""
    return SequenceMatcher(None, a, b).ratio()

def find_similar_pages(files_data):
    """Находит пары страниц со схожестью > 85%"""
    similar_pairs = []
    file_list = list(files_data.items())
    
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            file1, data1 = file_list[i]
            file2, data2 = file_list[j]
            
            sim = similarity(data1['content'], data2['content'])
            if sim > 0.85:
                similar_pairs.append((file1.name, file2.name, sim))
    
    return sorted(similar_pairs, key=lambda x: -x[2])

def find_duplicate_coords(files_data):
    """Находит страницы с одинаковыми координатами"""
    coords_map = {}
    for filepath, data in files_data.items():
        coords = data['geo_position']
        if coords:
            if coords not in coords_map:
                coords_map[coords] = []
            coords_map[coords].append(filepath)
    
    duplicates = {coords: files for coords, files in coords_map.items() if len(files) > 1}
    return duplicates

# Загружаем все файлы
print("Загрузка файлов...")
files_data = {}
for filepath in get_all_files():
    html = read_file(filepath)
    city = extract_city_name(filepath)
    content = extract_main_content(html)
    geo = extract_geo_position(html)
    h1 = extract_h1(html)
    
    files_data[filepath] = {
        'city': city,
        'content': content,
        'geo_position': geo,
        'h1': h1,
        'html': html
    }

print(f"Загружено {len(files_data)} файлов")

# Находим похожие страницы
print("\n=== Страницы со схожестью > 85% ===")
similar = find_similar_pages(files_data)
for f1, f2, sim in similar[:20]:  # Показываем топ-20
    print(f"{sim*100:.1f}%: {f1} <-> {f2}")

# Находим дубликаты координат
print("\n=== Страницы с одинаковыми координатами ===")
duplicates = find_duplicate_coords(files_data)
for coords, files in duplicates.items():
    if len(files) > 1:
        print(f"Координаты {coords}: {[f.name for f in files]}")

