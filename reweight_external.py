import os
import re

TARGET_DIR = 'icon-finder-app/icons'

# GEP icons use 3.33333 stroke on a 60x60 grid
TARGET_PROPORTION = 3.33333 / 60

def main():
    count = 0
    for file in os.listdir(TARGET_DIR):
        if file.startswith('ext-') and file.endswith('.svg'):
            filepath = os.path.join(TARGET_DIR, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find viewBox width
            match = re.search(r'viewBox="[\d\.\-]+\s+[\d\.\-]+\s+([\d\.]+)\s+[\d\.]+"', content)
            if match:
                vb_width = float(match.group(1))
            else:
                # default to 24 if no viewBox
                vb_width = 24.0
            
            target_stroke_width = round(vb_width * TARGET_PROPORTION, 4)

            # Replace any stroke-width
            new_content = re.sub(r'stroke-width="[^"]+"', f'stroke-width="{target_stroke_width}"', content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1

    print(f"Reweighted {count} external SVGs to match GEP proportion.")

if __name__ == '__main__':
    main()
