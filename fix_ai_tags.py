import json
import re

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

def update_json():
    json_path = 'icon-finder-app/icons.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        item['tags'] = generate_tags(item.get('label', ''))
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Successfully updated tags in {json_path}")
    
if __name__ == '__main__':
    update_json()
