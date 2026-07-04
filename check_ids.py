import os, re

c = 0
tot = 0
ids = []
for f in os.listdir('icon-finder-app/icons'):
    if not f.endswith('.svg'): continue
    tot += 1
    content = open(f'icon-finder-app/icons/{f}', 'r', encoding='utf-8').read()
    m = re.search(r'id="([^"]+)"', content)
    if m:
        c += 1
        ids.append(m.group(1))

print(f'Total SVGs: {tot}, With ID: {c}')
print('Sample IDs:')
print('\n'.join(ids[:10]))
