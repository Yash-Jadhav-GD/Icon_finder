import os
import re

TARGET_DIR = 'icon-finder-app/icons'

def main():
    count = 0
    for file in os.listdir(TARGET_DIR):
        if file.startswith('ext-') and file.endswith('.svg'):
            filepath = os.path.join(TARGET_DIR, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace any stroke color that is not "none" with "#66737C"
            new_content = re.sub(r'stroke="(?!none")[^"]+"', 'stroke="#66737C"', content)
            
            # Replace any fill color that is not "none" with "#66737C"
            new_content = re.sub(r'fill="(?!none")[^"]+"', 'fill="#66737C"', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1

    print(f"Recolored {count} external SVGs to #66737C")

if __name__ == '__main__':
    main()
