#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Complete mapping with proper adjective endings
# Format: filename pattern -> full_h1_suffix
LINE_INFO = {
    # Aviamotornaya - 3 different lines
    'aviamotornaya-kal': 'у метро Авиамоторная (Калининская линия)',
    'aviamotornaya': 'у метро Авиамоторная (Калининская линия)',
    'aviamotornaya-n': 'у метро Авиамоторная (Некрасовская линия)',
    
    # Fonvizinskaya - 2 different lines
    'fonvizinskaya-m': 'у метро Фонвизинская (Монорельс)',
    'fonvizinskaya-s': 'у метро Фонвизинская (Серпуховско-Тимирязевская линия)',
    
    # Aeroport - same line Zamoskvoretskaya, need district
    'aeroport': 'у метро Аэропорт (Замоскворецкая линия, район Аэропорт)',
    'aeroport-z': 'у метро Аэропорт (Замоскворецкая линия, район Ходынский)',
    
    # Alekseevskaya - same line Kaluzhsko-Rizhskaya
    'alekseevskaya-k': 'у метро Алексеевская (Калужско-Рижская линия, станция Алексеевская)',
    'alekseevskaya': 'у метро Алексеевская (Калужско-Рижская линия, главная станция)',
    
    # Avtozavodskaya - same line Zamoskvoretskaya
    'avtozavodskaya-z': 'у метро Автозаводская (Замоскворецкая линия, южная сторона)',
    'avtozavodskaya': 'у метро Автозаводская (Замоскворецкая линия, северная сторона)',
    
    # Bulvar Dmitriya Donskogo - 2 lines
    'bulvar-donskogo': 'у метро Бульвар Дмитрия Донского (Серпуховско-Тимирязевская линия)',
    'bulvar-donskogo-b': 'у метро Бульвар Дмитрия Донского (Бутовская линия)',
    
    # Chistye Prudy - 2 different red lines
    'chistye-prudy-kr': 'у метро Чистые пруды (Красносельская ветка)',
    'chistye-prudy-s': 'у метро Чистые пруды (Сокольническая ветка)',
    
    # Ploshchad Ilicha - same line Kalininskaya
    'ploshchad-ilicha-k': 'у метро Площадь Ильича (Калининская линия, выход к площади)',
    'ploshchad-ilicha-kal': 'у метро Площадь Ильича (Калининская линия, главный выход)',
    
    # Prospekt Mira - 2 lines
    'prospekt-mira-k': 'у метро Проспект Мира (Кольцевая линия)',
    'prospekt-mira-kr': 'у метро Проспект Мира (Калужско-Рижская линия)',
    
    # Oktyabrskaya - 2 lines
    'oktyabrskaya-k': 'у метро Октябрьская (Кольцевая линия)',
    'oktyabrskaya-kr': 'у метро Октябрьская (Калужско-Рижская линия)',
    
    # VDNH - 2 lines
    'vdnh': 'у метро ВДНХ (Калужско-Рижская линия, главная станция)',
    'vdnh-m': 'у метро ВДНХ (Монорельс)',
    
    # Akademicheskaya - same line Kaluzhsko-Rizhskaya
    'akademicheskaya-kr': 'у метро Академическая (Калужско-Рижская линия, южный выход)',
    'akademicheskaya': 'у метро Академическая (Калужско-Рижская линия, главный выход)',
}

def get_h1_suffix(filename):
    """Extract H1 suffix from filename"""
    for pattern, suffix in LINE_INFO.items():
        if pattern in filename:
            return suffix
    return None

def fix_h1_in_file(filepath):
    """Fix H1 tag in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    h1_suffix = get_h1_suffix(filename)
    
    if not h1_suffix:
        return False
    
    # Find current H1
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
