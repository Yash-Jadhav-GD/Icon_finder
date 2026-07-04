import os
import urllib.request
import zipfile
import shutil
import json
import re

ZIP_URL = "https://github.com/tabler/tabler-icons/archive/refs/heads/main.zip"
ZIP_FILE = "tabler-icons-main.zip"
TEMP_DIR = "tabler-icons-temp"
TARGET_DIR = "icon-finder-app/icons"
JSON_FILE = "icon-finder-app/icons.json"

TARGET_PROPORTION = 3.33333 / 60

def generate_tags(filename):
    # e.g. "brand-github" -> ["brand", "github"]
    words = re.findall(r'[a-zA-Z0-9]+', filename)
    tags = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if (len(w_lower) > 2 or w_lower in ['ai', 'ui', 'ux', 'db', 'it', '5g', 'vr', 'ar']) and w_lower not in seen:
            tags.append(w_lower)
            seen.add(w_lower)
    return tags

def main():
    print("Downloading Tabler Icons zip...")
    urllib.request.urlretrieve(ZIP_URL, ZIP_FILE)
    
    print("Extracting zip...")
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)
    
    outline_dir = os.path.join(TEMP_DIR, "tabler-icons-main", "icons", "outline")
    if not os.path.exists(outline_dir):
        print("Could not find outline directory!")
        return

    print("Processing outline SVGs...")
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        icons_data = json.load(f)

    # Clean existing tabler icons if running multiple times
    icons_data = [i for i in icons_data if not i.get('file', '').startswith('tabler-')]

    count = 0
    for file in os.listdir(outline_dir):
        if file.endswith('.svg'):
            source_path = os.path.join(outline_dir, file)
            
            clean_name = file[:-4]
            new_filename = f"tabler-{clean_name}.svg"
            target_path = os.path.join(TARGET_DIR, new_filename)
            
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find viewBox width
            match = re.search(r'viewBox="[\d\.\-]+\s+[\d\.\-]+\s+([\d\.]+)\s+[\d\.]+"', content)
            vb_width = float(match.group(1)) if match else 24.0
            target_stroke_width = round(vb_width * TARGET_PROPORTION, 4)

            # Recolor stroke and fill
            content = re.sub(r'stroke="(?!none")[^"]+"', 'stroke="#66737C"', content)
            content = re.sub(r'fill="(?!none")[^"]+"', 'fill="#66737C"', content)
            
            # Change stroke-width
            content = re.sub(r'stroke-width="[^"]+"', f'stroke-width="{target_stroke_width}"', content)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

            label = clean_name.replace('-', ' ').title()
            tags = generate_tags(clean_name)
            tags.append('tabler') # Add tabler tag for easy finding

            icons_data.append({
                "label": label,
                "tags": tags,
                "file": new_filename,
                "source": "external"
            })
            count += 1

    print(f"Writing {len(icons_data)} records to JSON...")
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(icons_data, f, indent=4)

    print("Cleaning up temporary files...")
    os.remove(ZIP_FILE)
    shutil.rmtree(TEMP_DIR)

    print(f"Success! Processed {count} Tabler Outline icons.")

if __name__ == '__main__':
    main()
