#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Mapping for remaining duplicates - need to add line NAME not just color
# Format: filename pattern -> (line_name, color_adj)
LINE_INFO = {
    # Aviamotornaya - 3 lines - use full line name
    'aviamotornaya-kal': ('Калининская', 'жёлтая'),
    'aviamotornaya': ('Калининская', 'жёлтая'),
    'aviamotornaya-n': ('Некрасовская', 'розовая'),
    
    # Fonvizinskaya - 2 lines
    'fonvizinskaya-m': ('Монорельс', 'серая'),
    'fonvizinskaya-s': ('Серпуховско-Тимирязевская', 'серая'),
    
    # Aeroport - same line, different districts
    'aeroport': ('Замоскворецкая', 'зелёная'),
    'aeroport-z': ('Замоскворецкая', 'зелёная'),
    
    # Alekseevskaya - same line
    'alekseevskaya-k': ('Калужско-Рижская', 'оранжевая'),
    'alekseevskaya': ('Калужско-Рижская', 'оранжевая'),
    
    # Avtozavodskaya - same line
    'avtozavodskaya-z': ('Замоскворецкая', 'зелёная'),
    'avtozavodskaya': ('Замоскворецкая', 'зелёная'),
    
    # Bulvar Dmitriya Donskogo - 2 lines
    'bulvar-donskogo': ('Серпуховско-Тимирязевская', 'серая'),
    'bulvar-donskogo-b': ('Бутовская', 'светло-серая'),
    
    # Chistye Prudy - 2 lines both red - use line name
    'chistye-prudy-kr': ('Красносельская', 'красная'),
    'chistye-prudy-s': ('Сокольническая', 'красная'),
    
    # Ploshchad Ilicha - same line
    'ploshchad-ilicha-k': ('Калининская', 'жёлтая'),
    'ploshchad-ilicha-kal': ('Калининская', 'жёлтая'),
    
    # Prospekt Mira - 2 lines
    'prospekt-mira-k': ('Кольцевая', 'коричневая'),
    'prospekt-mira-kr': ('Калужско-Рижская', 'оранжевая'),
    
    # Oktyabrskaya - 2 lines
    'oktyabrskaya-k': ('Кольцевая', 'коричневая'),
    'oktyabrskaya-kr': ('Калужско-Рижская', 'оранжевая'),
    
    # VDNH - 2 lines
    'vdnh': ('Калужско-Рижская', 'оранжевая'),
    'vdnh-m': ('Монорельс', 'серая'),
    
    # Akademicheskaya - same line
    'akademicheskaya-kr': ('Калужско-Рижская', 'оранжевая'),
    'akademicheskaya': ('Калужско-Рижская', 'оранжевая'),
}

def get_line_info(filename):
    """Extract line info from filename"""
    for pattern, info in LINE_INFO.items():
        if pattern in filename:
            return info
    return None

def fix_h1_in_file(filepath):
    """Fix H1 tag in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    line_info = get_line_info(filename)
    
    if not line_info:
        return False
    
    line_name, color = line_info
    
    # Find current H1
    h1_pattern = r'<h1 itemprop="name">Рабочий дом <span>у метро ([^<]+)</span></h1>'
    match = re.search(h1_pattern, content)
    
    if match:
        current_text = match.group(1)
        # Extract just the metro name (remove any existing line info in parentheses)
        metro_name_match = re.match(r'([^(]+)', current_text)
        if metro_name_match:
            metro_name = metro_name_match.group(1).strip()
        else:
            metro_name = current_text
        
        # For stations with same line, add district or other distinguishing info
        # For now use full line name + color
        new_h1 = f'<h1 itemprop="name">Рабочий дом <span>у метро {metro_name} ({line_name} {color}я линия)</span></h1>'
        
        content = re.sub(h1_pattern, new_h1, content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

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
