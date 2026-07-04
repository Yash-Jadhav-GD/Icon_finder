import json
import re

def generate_tags(label_text):
    # Split by non-alphanumeric to get words
    words = re.findall(r'[a-zA-Z0-9]+', label_text)
    
    tags = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        # Filter out very short words or common stop words if necessary
        # but in this context, most words in the label are keywords.
        if (len(w_lower) > 2 or w_lower in ['ai', 'ui', 'ux', '3d', 'vr', 'ar', 'os', 'it', 'bot']) and w_lower not in seen:
            tags.append(w_lower)
            seen.add(w_lower)
            
    # Return 5 to 8 tags, or however many we have if less
    return tags[:8]

def update_json():
    with open('output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        item['tags'] = generate_tags(item.get('label', ''))
        
    with open('output_tagged.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Successfully processed {len(data)} items and added tags.")
    
if __name__ == '__main__':
    update_json()
