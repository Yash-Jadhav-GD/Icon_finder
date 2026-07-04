import json
import zipfile
import os
import shutil
import re

def create_slug(text, max_len=50):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    if len(slug) > max_len:
        # truncate at last hyphen if possible
        truncated = slug[:max_len]
        last_hyphen = truncated.rfind('-')
        if last_hyphen > 0:
            slug = truncated[:last_hyphen]
        else:
            slug = truncated
    return slug

def export():
    pptx_file = 'Minimal_Icons 3.pptx'
    json_file = 'output.json'
    export_dir = 'icons_export'
    icons_dir = os.path.join(export_dir, 'icons')
    
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)
    os.makedirs(icons_dir)
    
    # 1. Extract ppt/media/
    print("Extracting media files from PPTX...")
    media_tmp = 'media_tmp'
    if os.path.exists(media_tmp):
        shutil.rmtree(media_tmp)
    os.makedirs(media_tmp)
    
    with zipfile.ZipFile(pptx_file, 'r') as z:
        media_files = [f for f in z.namelist() if f.startswith('ppt/media/')]
        for mf in media_files:
            z.extract(mf, media_tmp)
            
    # 2. Process JSON and rename files
    print("Processing JSON and renaming files...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        original_file = item.get('file')
        if not original_file or original_file == 'unknown':
            continue
            
        ext = os.path.splitext(original_file)[1]
        
        # generate slug from label
        slug = create_slug(item.get('label', 'icon'))
        
        # ensure unique filename
        new_filename = f"{slug}-{item['id']}{ext}"
        
        src_path = os.path.join(media_tmp, 'ppt', 'media', original_file)
        dst_path = os.path.join(icons_dir, new_filename)
        
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
            # Update json
            item['file'] = new_filename
        else:
            print(f"Warning: {src_path} not found in zip.")
            
    # 3. Save updated JSON
    out_json = os.path.join(export_dir, 'icons.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved JSON to {out_json}")
    
    # 4. Zip the export directory
    print("Zipping the final export...")
    zip_name = 'icons_export.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, export_dir)
                zf.write(filepath, arcname)
                
    # cleanup
    shutil.rmtree(media_tmp)
    
    print(f"Done! Created {zip_name}")

if __name__ == '__main__':
    export()
