#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Mapping of metro station suffixes to line info with proper adjective endings
# Format: filename pattern -> (line_name, color_adj_correct, district)
LINE_INFO = {
    # Шипиловская
    'shipilovskaya-l': ('Люблинско-Дмитровская', 'салатовая', 'Орехово-Борисово'),
    'shipilovskaya-z': ('Замоскворецкая', 'зелёная', 'Зябликово'),
    
    # Смоленская
    'smolenskaya-f': ('Филёвская', 'голубая', 'Арбат'),
    'smolenskaya-a': ('Арбатско-Покровская', 'синяя', 'Арбат'),
    
    # Дмитровская
    'dmitrovskaya-s': ('Серпуховско-Тимирязевская', 'серая', 'Савёловский'),
    'dmitrovskaya-m': ('Московское центральное кольцо', 'красная', 'Коптево'),
    
    # ВДНХ
    'vdnh': ('Калужско-Рижская', 'оранжевая', 'Останкинский'),
    'vdnh-m': ('Монорельс', 'серая', 'Останкинский'),
    
    # Курская
    'kurskaya-a': ('Арбатско-Покровская', 'синяя', 'Басманный'),
    'kurskaya-k': ('Кольцевая', 'коричневая', 'Басманный'),
    
    # Добрынинская
    'dobryninskaya-k': ('Кольцевая', 'коричневая', 'Даниловский'),
    'dobryninskaya-z': ('Замоскворецкая', 'зелёная', 'Даниловский'),
    
    # Академическая
    'akademicheskaya-kr': ('Калужско-Рижская', 'оранжевая', 'Академический'),
    'akademicheskaya': ('Калужско-Рижская', 'оранжевая', 'Академический'),
    
    # Арбатская
    'arbatskaya-f': ('Филёвская', 'голубая', 'Арбат'),
    'arbatskaya-a': ('Арбатско-Покровская', 'синяя', 'Арбат'),
    
    # Фонвизинская
    'fonvizinskaya-m': ('Монорельс', 'серая', 'Останкинский'),
    'fonvizinskaya-l': ('Люблинско-Дмитровская', 'салатовая', 'Марьина Роща'),
    'fonvizinskaya-s': ('Серпуховско-Тимирязевская', 'серая', 'Марьина Роща'),
    
    # Зябликово
    'zyablikovo-l': ('Люблинско-Дмитровская', 'салатовая', 'Зябликово'),
    'zyablikovo-z': ('Замоскворецкая', 'зелёная', 'Зябликово'),
    
    # Алексеевская
    'alekseevskaya-k': ('Калужско-Рижская', 'оранжевая', 'Алексеевский'),
    'alekseevskaya': ('Калужско-Рижская', 'оранжевая', 'Алексеевский'),
    
    # Лубянка
    'lubyanka-s': ('Сокольническая', 'красная', 'Мещанский'),
    'lubyanka-kr': ('Красносельская', 'красная', 'Мещанский'),
    
    # Алма-Атинская
    'alma-atinskaya': ('Замоскворецкая', 'зелёная', 'Братеево'),
    'almatinskaya': ('Замоскворецкая', 'зелёная', 'Братеево'),
    
    # Автозаводская
    'avtozavodskaya-z': ('Замоскворецкая', 'зелёная', 'Даниловский'),
    'avtozavodskaya': ('Замоскворецкая', 'зелёная', 'Даниловский'),
    
    # Павелецкая
    'paveletskaya-z': ('Замоскворецкая', 'зелёная', 'Замоскворечье'),
    'paveletskaya-k': ('Кольцевая', 'коричневая', 'Замоскворечье'),
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
    
    line_name, color, district = line_info
    
    # Find current H1 (may already have been modified)
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
        
        # Create new H1 with line info - format: "у метро Название (цвет линия)"
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
