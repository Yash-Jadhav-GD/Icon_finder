import os
import re
import json
import uuid

def generate_tags(label_text):
    words = re.findall(r'[a-zA-Z0-9]+', label_text)
    tags = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if (len(w_lower) > 2 or w_lower in ['ai', 'ui', 'ux', '3d', 'vr', 'ar', 'os', 'it', 'bot']) and w_lower not in seen:
            tags.append(w_lower)
            seen.add(w_lower)
    return tags[:8]

def clean_label(raw_id):
    # Remove standard suffix if present
    lbl = raw_id.replace('--Streamline-Ultimate', '').replace('.svg', '')
    # Replace hyphens with spaces
    lbl = lbl.replace('-', ' ')
    # Remove trailing numbers like " 1", " 6"
    lbl = re.sub(r' \d+$', '', lbl)
    # Remove multiple spaces
    lbl = re.sub(r'\s+', ' ', lbl).strip()
    return lbl

def main():
    icons_dir = 'icon-finder-app/icons'
    json_path = 'icon-finder-app/icons.json'
    
    new_data = []
    
    # Process all svgs
    for filename in os.listdir(icons_dir):
        if not filename.endswith('.svg'):
            continue
            
        filepath = os.path.join(icons_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        m = re.search(r'id="([^"]+)"', content)
        if m:
            raw_id = m.group(1)
        else:
            raw_id = filename.replace('.svg', '')
            
        label = clean_label(raw_id)
        
        # Generate new filename
        new_filename_base = label.lower().replace(' ', '-')
        # Add a short unique id to prevent overwriting
        short_id = str(uuid.uuid4())[:6]
        new_filename = f"{new_filename_base}-{short_id}.svg"
        
        new_filepath = os.path.join(icons_dir, new_filename)
        
        # Rename file
        os.rename(filepath, new_filepath)
        
        # Generate tags
        tags = generate_tags(label)
        
        new_data.append({
            "id": short_id,
            "file": new_filename,
            "label": label,
            "tags": tags
        })
        
    # Write new json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2)
        
    print(f"Successfully rebuilt library for {len(new_data)} icons.")

if __name__ == '__main__':
    main()
