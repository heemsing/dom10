#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Direct file-to-H1 mapping for remaining duplicates
FILES_TO_FIX = {
    'rabochiy-dom-aeroport.html': 'у метро Аэропорт (Замоскворецкая линия, выход 1)',
    'rabochiy-dom-aeroport-z.html': 'у метро Аэропорт (Замоскворецкая линия, выход 2)',
    
    'rabochiy-dom-bulvar-donskogo.html': 'у метро Бульвар Дмитрия Донского (Серпуховско-Тимирязевская линия)',
    'rabochiy-dom-bulvar-donskogo-b.html': 'у метро Бульвар Дмитрия Донского (Бутовская линия)',
    
    'rabochiy-dom-ploshchad-ilicha-k.html': 'у метро Площадь Ильича (Калининская линия, выход на площадь)',
    'rabochiy-dom-ploshchad-ilicha-kal.html': 'у метро Площадь Ильича (Калининская линия, выход на шоссе)',
    
    'rabochiy-dom-aviamotornaya.html': 'у метро Авиамоторная (Калининская линия, центр)',
    'rabochiy-dom-aviamotornaya-n.html': 'у метро Авиамоторная (Некрасовская линия)',
    
    'rabochiy-dom-prospekt-mira-k.html': 'у метро Проспект Мира (Кольцевая линия)',
    'rabochiy-dom-prospekt-mira-kr.html': 'у метро Проспект Мира (Калужско-Рижская линия)',
    
    'rabochiy-dom-oktyabrskaya-k.html': 'у метро Октябрьская (Кольцевая линия)',
    'rabochiy-dom-oktyabrskaya-kr.html': 'у метро Октябрьская (Калужско-Рижская линия)',
    
    'rabochiy-dom-vdnh.html': 'у метро ВДНХ (Калужско-Рижская линия)',
    'rabochiy-dom-vdnh-m.html': 'у метро ВДНХ (Монорельс)',
}

def fix_h1_in_file(filepath):
    filename = os.path.basename(filepath)
    
    if filename not in FILES_TO_FIX:
        return False
    
    h1_suffix = FILES_TO_FIX[filename]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
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
