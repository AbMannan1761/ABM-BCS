import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

ids = re.findall(r'document\.getElementById\([\'"](.*?)[\'"]\)', code)
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_ids = set(re.findall(r'id=[\'"](.*?)[\'"]', html))

missing = [i for i in sorted(set(ids)) if i not in html_ids and not i.startswith('qcard_') and not i.startswith('exp_') and not i.startswith('omr_')]

print("MISSING IDs in index.html:")
for m in missing:
    print(" -", m)
