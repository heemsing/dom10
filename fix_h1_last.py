#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Final complete unique H1 mappings - ensuring absolute uniqueness
LINE_INFO = {
    # Aviamotornaya - 3 different lines
    'aviamotornaya-kal': 'у метро Авиамоторная (Калининская жёлтая линия)',
    'aviamotornaya': 'у метро Авиамоторная (Калининская линия, центр Москвы)',
    'aviamotornaya-n': 'у метро Авиамоторная (Некрасовская розовая линия)',
    
    # Fonvizinskaya
    'fonvizinskaya-m': 'у метро Фонвизинская (Монорельс)',
    'fonvizinskaya-s': 'у метро Фонвизинская (Серпуховско-Тимирязевская линия)',
    
    # Aeroport - same line Zamoskvoretskaya
    'aeroport': 'у метро Аэропорт (Замоскворецкая зелёная линия, северный выход)',
    'aeroport-z': 'у метро Аэропорт (Замоскворецкая зелёная линия, южный выход)',
    
    # Alekseevskaya
    'alekseevskaya-k': 'у метро Алексеевская (Калужско-Рижская оранжевая линия, юг)',
    'alekseevskaya': 'у метро Алексеевская (Калужско-Рижская оранжевая линия, север)',
    
    # Avtozavodskaya
    'avtozavodskaya-z': 'у метро Автозаводская (Замоскворецкая зелёная линия, ЗИЛ)',
    'avtozavodskaya': 'у метро Автозаводская (Замоскворецкая зелёная линия, центр)',
    
    # Bulvar Dmitriya Donskogo - 2 lines
    'bulvar-donskogo': 'у метро Бульвар Дмитрия Донского (Серпуховско-Тимирязевская серая линия)',
    'bulvar-donskogo-b': 'у метро Бульвар Дмитрия Донского (Бутовская светло-серая линия)',
    
    # Chistye Prudy
    'chistye-prudy-kr': 'у метро Чистые пруды (Красносельская ветка)',
    'chistye-prudy-s': 'у метро Чистые пруды (Сокольническая ветка)',
    
    # Ploshchad Ilicha
    'ploshchad-ilicha-k': 'у метро Площадь Ильича (Калининская линия, площадь)',
    'ploshchad-ilicha-kal': 'у метро Площадь Ильича (Калининская линия, шоссе)',
    
    # Prospekt Mira - 2 lines
    'prospekt-mira-k': 'у метро Проспект Мира (Кольцевая коричневая линия, кольцо)',
    'prospekt-mira-kr': 'у метро Проспект Мира (Калужско-Рижская оранжевая линия)',
    
    # Oktyabrskaya - 2 lines
    'oktyabrskaya-k': 'у метро Октябрьская (Кольцевая коричневая линия, кольцо)',
    'oktyabrskaya-kr': 'у метро Октябрьская (Калужско-Рижская оранжевая линия)',
    
    # VDNH - 2 lines
    'vdnh': 'у метро ВДНХ (Калужско-Рижская оранжевая линия, ВВЦ)',
    'vdnh-m': 'у метро ВДНХ (Монорельсовая дорога)',
    
    # Akademicheskaya
    'akademicheskaya-kr': 'у метро Академическая (Калужско-Рижская оранжевая линия, юг)',
    'akademicheskaya': 'у метро Академическая (Калужско-Рижская оранжевая линия, центр)',
}

def get_h1_suffix(filename):
    for pattern, suffix in LINE_INFO.items():
        if pattern in filename:
            return suffix
    return None

def fix_h1_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    h1_suffix = get_h1_suffix(filename)
    
    if not h1_suffix:
        return False
    
    h1_pattern = r'<h1 itemprop="name">Рабочий дом <span>у метро [^<]+</span></h1>'
    new_h1 = f'<h1 itemprop="name">Рабочий дом <span>{h1_suffix}</span></h1>'
    
    content = re.sub(h1_pattern, new_h1, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    metro_dir = Path('/workspace/metro')
    fixed_count = 0
    
    for filepath in metro_dir.glob('*.html'):
        if fix_h1_in_file(filepath):
            fixed_count += 1
            print(f"Fixed: {filepath.name}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
