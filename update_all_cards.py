import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json

def suffix(n):
    if 11 <= (n % 100) <= 13: return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')

# 1. Load accordions
with open('qb_accordions.json', 'r', encoding='utf-8') as f:
    accs = json.load(f)

preli_acc = next(a for a in accs if 'Preli Question' in a['header'])

# Map existing bundle files
files = {f[:-5].lower(): f[:-5] for f in os.listdir('bcs_data') if f.endswith('.json')}

new_cards = []
for i in range(49, 0, -1):
    route_candidate = f"{i}{suffix(i)}-bcs"
    matched_route = files.get(route_candidate.lower())
    
    if matched_route:
        with open(f"bcs_data/{matched_route}.json", 'r', encoding='utf-8') as f:
            d = json.load(f)
            meta = d.get('meta', {})
            q_count = len(d.get('questions', []))
            new_cards.append({
                'title': f"{i}{suffix(i)} BCS",
                'sub1': f"{meta.get('sub', 'General')} ({q_count}টি প্রশ্ন)",
                'sub2': meta.get('date', f"BCS Exam {i}"),
                'route': matched_route
            })
    else:
        if i in [11, 12, 13]:
            note = "বিশেষ ব্যাচ / সরাসরি লিখিত"
        else:
            note = "ঐতিহাসিক লিখিত পরীক্ষা"
        new_cards.append({
            'title': f"{i}{suffix(i)} BCS",
            'sub1': note,
            'sub2': "MCQ প্রিলি চালু হয় ১০ম বিসিএস থেকে",
            'route': f"{i}{suffix(i)}-bcs"
        })

preli_acc['cards'] = new_cards
print(f"Total cards generated in Preli Accordion: {len(new_cards)}")

with open('qb_accordions.json', 'w', encoding='utf-8') as f:
    json.dump(accs, f, ensure_ascii=False, indent=2)

# Also update homepage_data.js
with open('homepage_data.js', 'r', encoding='utf-8') as f:
    hp_content = f.read()

# Replace window.QB_ACCORDIONS in homepage_data.js
acc_json_str = json.dumps(accs, ensure_ascii=False, indent=2)
if 'window.QB_ACCORDIONS =' in hp_content:
    prefix = hp_content.split('window.QB_ACCORDIONS =')[0]
    rest = hp_content.split('window.QB_ACCORDIONS =')[1]
    # find ending of array
    idx_semicolon = rest.find(';\n')
    if idx_semicolon != -1:
        hp_content = prefix + "window.QB_ACCORDIONS = " + acc_json_str + rest[idx_semicolon:]
    else:
        hp_content = prefix + "window.QB_ACCORDIONS = " + acc_json_str + ";\n"

with open('homepage_data.js', 'w', encoding='utf-8') as f:
    f.write(hp_content)

print("Successfully updated qb_accordions.json and homepage_data.js!")
