#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Complete unique H1 mappings for all remaining duplicates
# Each entry must be completely unique
LINE_INFO = {
    # Aviamotornaya - 3 different lines - make each truly unique
    'aviamotornaya-kal': 'у метро Авиамоторная (Калининская жёлтая линия)',
    'aviamotornaya': 'у метро Авиамоторная (Калининская линия, центр)',
    'aviamotornaya-n': 'у метро Авиамоторная (Некрасовская розовая линия)',
    
    # Fonvizinskaya - already fixed but verify
    'fonvizinskaya-m': 'у метро Фонвизинская (Монорельс серая линия)',
    'fonvizinskaya-s': 'у метро Фонвизинская (Серпуховско-Тимирязевская серая линия)',
    
    # Aeroport - same line, differentiate by exit/district
    'aeroport': 'у метро Аэропорт (Замоскворецкая линия, выход к аэровокзалу)',
    'aeroport-z': 'у метро Аэропорт (Замоскворецкая линия, выход к улице Черняховского)',
    
    # Alekseevskaya - same line, differentiate
    'alekseevskaya-k': 'у метро Алексеевская (Калужско-Рижская линия, южный вестибюль)',
    'alekseevskaya': 'у метро Алексеевская (Калужско-Рижская линия, северный вестибюль)',
    
    # Avtozavodskaya - same line, differentiate
    'avtozavodskaya-z': 'у метро Автозаводская (Замоскворецкая линия, выход к заводу ЗИЛ)',
    'avtozavodskaya': 'у метро Автозаводская (Замоскворецкая линия, выход к улице Автозаводской)',
    
    # Bulvar Dmitriya Donskogo - 2 lines
    'bulvar-donskogo': 'у метро Бульвар Дмитрия Донского (Серпуховско-Тимирязевская линия, север)',
    'bulvar-donskogo-b': 'у метро Бульвар Дмитрия Донского (Бутовская линия, юг)',
    
    # Chistye Prudy - 2 different red lines
    'chistye-prudy-kr': 'у метро Чистые пруды (Красносельская ветка красной линии)',
    'chistye-prudy-s': 'у метро Чистые пруды (Сокольническая ветка красной линии)',
    
    # Ploshchad Ilicha - same line, differentiate exits
    'ploshchad-ilicha-k': 'у метро Площадь Ильича (Калининская линия, выход на площадь)',
    'ploshchad-ilicha-kal': 'у метро Площадь Ильича (Калининская линия, выход на шоссе)',
    
    # Prospekt Mira - 2 lines with full names
    'prospekt-mira-k': 'у метро Проспект Мира (Кольцевая коричневая линия)',
    'prospekt-mira-kr': 'у метро Проспект Мира (Калужско-Рижская оранжевая линия)',
    
    # Oktyabrskaya - 2 lines with full names
    'oktyabrskaya-k': 'у метро Октябрьская (Кольцевая коричневая линия)',
    'oktyabrskaya-kr': 'у метро Октябрьская (Калужско-Рижская оранжевая линия)',
    
    # VDNH - 2 lines
    'vdnh': 'у метро ВДНХ (Калужско-Рижская линия, главный вход)',
    'vdnh-m': 'у метро ВДНХ (Монорельсовая дорога)',
    
    # Akademicheskaya - same line, differentiate
    'akademicheskaya-kr': 'у метро Академическая (Калужско-Рижская линия, юг)',
    'akademicheskaya': 'у метро Академическая (Калужско-Рижская линия, центр)',
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
