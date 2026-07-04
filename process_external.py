import os
import shutil
import json
import re

EXTERNAL_DIR = 'external_icons'
TARGET_DIR = 'icon-finder-app/icons'
JSON_FILE = 'icon-finder-app/icons.json'

def generate_tags(label_text, category):
    words = re.findall(r'[a-zA-Z0-9]+', label_text)
    words.append(category)
    tags = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if (len(w_lower) > 2 or w_lower in ['ai', 'ui', 'ux', 'db', 'it', '5g', 'vr', 'ar']) and w_lower not in seen:
            tags.append(w_lower)
            seen.add(w_lower)
    return tags

def main():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        icons_data = json.load(f)

    # Clean existing external icons from json if running multiple times
    icons_data = [i for i in icons_data if i.get('source') != 'external']

    count = 0
    for root, dirs, files in os.walk(EXTERNAL_DIR):
        category = os.path.basename(root)
        if category == EXTERNAL_DIR:
            continue # skip root

        for file in files:
            if file.endswith('.svg'):
                source_path = os.path.join(root, file)
                
                # generate new filename to prevent collisions
                clean_name = re.sub(r'[^a-zA-Z0-9]', '-', file[:-4]).strip('-').lower()
                clean_name = re.sub(r'-+', '-', clean_name)
                cat_clean = re.sub(r'[^a-zA-Z0-9]', '-', category).lower()
                new_filename = f"ext-{cat_clean}-{clean_name}.svg"
                target_path = os.path.join(TARGET_DIR, new_filename)
                
                shutil.copy2(source_path, target_path)

                # Generate label
                label = clean_name.replace('-', ' ').title()
                
                # Generate tags
                tags = generate_tags(label, category)

                icons_data.append({
                    "label": label,
                    "tags": tags,
                    "file": new_filename,
                    "source": "external"
                })
                count += 1

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(icons_data, f, indent=4)

    print(f"Processed {count} external icons and updated icons.json")

if __name__ == '__main__':
    main()
