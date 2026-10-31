import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json

bundle = {}
for fname in os.listdir('bcs_data'):
    if fname.endswith('.json'):
        route_id = fname[:-5]
        with open(os.path.join('bcs_data', fname), encoding='utf-8') as f:
            data = json.load(f)
            bundle[route_id] = data

print(f"Compiled {len(bundle)} exams into bundle.")
total_qs = sum(len(d['questions']) for d in bundle.values())
print(f"Total questions across all compiled exams: {total_qs}")

# Output as JS
js_content = "window.ALL_BCS_EXAMS = " + json.dumps(bundle, ensure_ascii=False) + ";\n"
with open('bcs_exams_bundle.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Saved bcs_exams_bundle.js successfully!")
