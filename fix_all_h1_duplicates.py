#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Complete mapping of all metro stations with duplicates
# Format: filename pattern -> (line_name, color_adj, district)
LINE_INFO = {
    # Already fixed - 30 stations
    'shipilovskaya-l': ('Люблинско-Дмитровская', 'салатовая'),
    'shipilovskaya-z': ('Замоскворецкая', 'зелёная'),
    'smolenskaya-f': ('Филёвская', 'голубая'),
    'smolenskaya-a': ('Арбатско-Покровская', 'синяя'),
    'dmitrovskaya-s': ('Серпуховско-Тимирязевская', 'серая'),
    'dmitrovskaya-m': ('МЦК', 'красная'),
    'vdnh': ('Калужско-Рижская', 'оранжевая'),
    'vdnh-m': ('Монорельс', 'серая'),
    'kurskaya-a': ('Арбатско-Покровская', 'синяя'),
    'kurskaya-k': ('Кольцевая', 'коричневая'),
    'dobryninskaya-k': ('Кольцевая', 'коричневая'),
    'dobryninskaya-z': ('Замоскворецкая', 'зелёная'),
    'akademicheskaya-kr': ('Калужско-Рижская', 'оранжевая'),
    'akademicheskaya': ('Калужско-Рижская', 'оранжевая'),
    'arbatskaya-f': ('Филёвская', 'голубая'),
    'arbatskaya-a': ('Арбатско-Покровская', 'синяя'),
    'fonvizinskaya-m': ('Монорельс', 'серая'),
    'fonvizinskaya-l': ('Люблинско-Дмитровская', 'салатовая'),
    'fonvizinskaya-s': ('Серпуховско-Тимирязевская', 'серая'),
    'zyablikovo-l': ('Люблинско-Дмитровская', 'салатовая'),
    'zyablikovo-z': ('Замоскворецкая', 'зелёная'),
    'alekseevskaya-k': ('Калужско-Рижская', 'оранжевая'),
    'alekseevskaya': ('Калужско-Рижская', 'оранжевая'),
    'lubyanka-s': ('Сокольническая', 'красная'),
    'lubyanka-kr': ('Калужско-Рижская', 'оранжевая'),
    'alma-atinskaya': ('Замоскворецкая', 'зелёная'),
    'almatinskaya': ('Замоскворецкая', 'зелёная'),
    'avtozavodskaya-z': ('Замоскворецкая', 'зелёная'),
    'avtozavodskaya': ('Замоскворецкая', 'зелёная'),
    'paveletskaya-z': ('Замоскворецкая', 'зелёная'),
    'paveletskaya-k': ('Кольцевая', 'коричневая'),
    
    # Kievskaya - 3 lines
    'kievskaya-k': ('Кольцевая', 'коричневая'),
    'kievskaya-a': ('Арбатско-Покровская', 'синяя'),
    'kievskaya-f': ('Филёвская', 'голубая'),
    
    # Elektrozavodskaya - 2 lines
    'elektrozavodskaya-a': ('Арбатско-Покровская', 'синяя'),
    'elektrozavodskaya-n': ('Некрасовская', 'розовая'),
    
    # Aviamotornaya - 3 lines
    'aviamotornaya-kal': ('Калининская', 'жёлтая'),
    'aviamotornaya': ('Калининская', 'жёлтая'),
    'aviamotornaya-n': ('Некрасовская', 'розовая'),
    
    # Tretyakovskaya - 3 lines
    'tretyakovskaya-z': ('Замоскворецкая', 'зелёная'),
    'tretyakovskaya-kal': ('Калининская', 'жёлтая'),
    'tretyakovskaya-kr': ('Калужско-Рижская', 'оранжевая'),
    
    # Aeroport
    'aeroport': ('Замоскворецкая', 'зелёная'),
    'aeroport-z': ('Замоскворецкая', 'зелёная'),
    
    # Bulvar Dmitriya Donskogo
    'bulvar-donskogo': ('Серпуховско-Тимирязевская', 'серая'),
    'bulvar-donskogo-b': ('Бутовская', 'светло-серая'),
    
    # Marksistskaya
    'marksistskaya-kal': ('Калининская', 'жёлтая'),
    'marksistskaya-k': ('Кольцевая', 'коричневая'),
    
    # Sukharevskaya
    'sukharevskaya-kr': ('Калужско-Рижская', 'оранжевая'),
    'sukharevskaya-k': ('Кольцевая', 'коричневая'),
    
    # Kashirskaya
    'kashirskaya-kh': ('Каховская', 'бирюзовая'),
    'kashirskaya-z': ('Замоскворецкая', 'зелёная'),
    
    # Chistye Prudy
    'chistye-prudy-kr': ('Красносельская', 'красная'),
    'chistye-prudy-s': ('Сокольническая', 'красная'),
    
    # Ploshchad Ilicha
    'ploshchad-ilicha-k': ('Калининская', 'жёлтая'),
    'ploshchad-ilicha-kal': ('Калининская', 'жёлтая'),
    
    # Serpukhovskaya
    'serpukhovskaya-s': ('Серпуховско-Тимирязевская', 'серая'),
    'serpukhovskaya-z': ('Замоскворецкая', 'зелёная'),
    
    # Timiryazevskaya
    'timiryazevskaya-s': ('Серпуховско-Тимирязевская', 'серая'),
    'timiryazevskaya-m': ('МЦК', 'красная'),
    
    # Belorusskaya
    'belorusskaya-k': ('Кольцевая', 'коричневая'),
    'belorusskaya-z': ('Замоскворецкая', 'зелёная'),
    
    # Prospekt Mira
    'prospekt-mira-k': ('Кольцевая', 'коричневая'),
    'prospekt-mira-kr': ('Калужско-Рижская', 'оранжевая'),
    
    # Oktyabrskaya
    'oktyabrskaya-k': ('Кольцевая', 'коричневая'),
    'oktyabrskaya-kr': ('Калужско-Рижская', 'оранжевая'),
    
    # Krasnye Vorota
    'krasnye-vorota-s': ('Сокольническая', 'красная'),
    'krasnye-vorota-k': ('Кольцевая', 'коричневая'),
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
        
        # Create new H1 with line info
        new_h1 = f'<h1 itemprop="name">Рабочий дом <span>у метро {metro_name} ({color} линия)</span></h1>'
        
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
