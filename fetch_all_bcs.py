import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import urllib.request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

os.makedirs('bcs_data', exist_ok=True)

# List of BCS Preli exams
EXAMS_TO_FETCH = [
    {'id': '50th-bcs', 'name': '50th BCS', 'sub': 'General', 'date': '2026-01-30'},
    {'id': '49th-BCS', 'name': '49th BCS', 'sub': 'Special (Education)', 'date': '2025-10-10'},
    {'id': '47th-BCS', 'name': '47th BCS', 'sub': 'General', 'date': '2025-09-19'},
    {'id': '48th-BCS', 'name': '48th BCS', 'sub': 'Special (Health)', 'date': '2025-07-18'},
    {'id': '46th-BCS', 'name': '46th BCS', 'sub': 'General', 'date': '2024-04-26'},
    {'id': '45th-BCS', 'name': '45th BCS', 'sub': 'General', 'date': '2023-05-19'},
    {'id': '44th-bcs', 'name': '44th BCS', 'sub': 'General', 'date': '2022-05-27'},
    {'id': '43rd-bcs', 'name': '43rd BCS', 'sub': 'General', 'date': '2021-10-29'},
    {'id': '42nd-bcs', 'name': '42nd BCS', 'sub': 'Special (Health)', 'date': '2021-02-26'},
    {'id': '41st-bcs', 'name': '41st BCS', 'sub': 'General', 'date': '2021-03-19'},
    {'id': '40th-bcs', 'name': '40th BCS', 'sub': 'General', 'date': '2019-05-03'},
    {'id': '39th-bcs', 'name': '39th BCS', 'sub': 'Special (Health)', 'date': '2018-08-03'},
    {'id': '38th-bcs', 'name': '38th BCS', 'sub': 'General', 'date': '2017-12-29'},
    {'id': '37th-bcs', 'name': '37th BCS', 'sub': 'General', 'date': '2016-09-30'},
    {'id': '36th-bcs', 'name': '36th BCS', 'sub': 'General', 'date': '2016-01-08'},
    {'id': '35th-bcs', 'name': '35th BCS', 'sub': 'General', 'date': '2015-03-06'}
]

SUBJECT_MAP = {
    'BANGLA': {'bn': 'বাংলা ভাষা ও সাহিত্য', 'icon': '📚', 'color': '#2563eb'},
    'ENGLISH': {'bn': 'ইংরেজি ভাষা ও সাহিত্য', 'icon': '📖', 'color': '#7c3aed'},
    'BANGLADESH-AFFAIRS': {'bn': 'বাংলাদেশ বিষয়াবলী', 'icon': '🇧🇩', 'color': '#059669'},
    'INTERNATIONAL-AFFAIRS': {'bn': 'আন্তর্জাতিক বিষয়াবলী', 'icon': '🌐', 'color': '#0284c7'},
    'GEOGRAPHY': {'bn': 'ভূগোল ও দুর্যোগ ব্যবস্থাপনা', 'icon': '🗺️', 'color': '#0d9488'},
    'GENERAL-SCIENCE': {'bn': 'সাধারণ বিজ্ঞান', 'icon': '🔬', 'color': '#d97706'},
    'COMPUTER-AND-IT': {'bn': 'কম্পিউটার ও তথ্যপ্রযুক্তি', 'icon': '💻', 'color': '#4f46e5'},
    'MATHEMATICAL-REASONING': {'bn': 'গাণিতিক যুক্তি', 'icon': '📐', 'color': '#e11d48'},
    'MENTAL-ABILITY': {'bn': 'মানসিক দক্ষতা', 'icon': '🧠', 'color': '#9333ea'},
    'ETHICS': {'bn': 'নৈতিকতা ও সুশাসন', 'icon': '⚖️', 'color': '#ca8a04'}
}

def get_canonical_subject(raw_subj):
    s = (raw_subj or '').strip().upper()
    if 'BANGLADESH' in s: return 'BANGLADESH-AFFAIRS'
    if 'BANGLA' in s: return 'BANGLA'
    if 'ENGLISH' in s: return 'ENGLISH'
    if 'INTERNATIONAL' in s: return 'INTERNATIONAL-AFFAIRS'
    if 'GEOGRAPHY' in s or 'DIGESTER' in s: return 'GEOGRAPHY'
    if 'SCIENCE' in s: return 'GENERAL-SCIENCE'
    if 'COMPUTER' in s or 'IT' in s or 'INFORMATION' in s: return 'COMPUTER-AND-IT'
    if 'MATH' in s: return 'MATHEMATICAL-REASONING'
    if 'MENTAL' in s: return 'MENTAL-ABILITY'
    if 'ETHIC' in s or 'GOVERN' in s: return 'ETHICS'
    return 'BANGLADESH-AFFAIRS'

def parse_exam(exam_meta):
    route_id = exam_meta['id']
    target_file = f"bcs_data/{route_id}.json"
    
    # If 50th BCS already parsed locally
    if route_id == '50th-bcs' and os.path.exists('questions.json'):
        with open('questions.json', encoding='utf-8') as f:
            qs = json.load(f)
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump({'meta': exam_meta, 'questions': qs}, f, ensure_ascii=False, indent=2)
        print(f"[{route_id}] Used existing 50th BCS questions ({len(qs)} questions)")
        return route_id, len(qs)

    url = f"https://uttoron.academy/QuestionBank/QuestionPreview/{route_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        q_divs = soup.find_all('div', class_='single-question')
        
        parsed_questions = []
        for idx, q_div in enumerate(q_divs):
            q_num = idx + 1
            raw_subj = q_div.get('data-subject', '').strip().upper()
            canon_subj = get_canonical_subject(raw_subj)
            correct_ans = q_div.get('data-answer', '').strip().upper()

            # Description
            desc_div = q_div.find('p', class_='description')
            q_html = ""
            q_text = ""
            if desc_div:
                inner = desc_div.find('div')
                q_html = str(inner).strip() if inner else "".join([str(c) for c in desc_div.children]).strip()
                q_text = desc_div.get_text(strip=True)

            # Options
            options = {}
            options_html = {}
            ul = q_div.find('ul', class_='list-unstyled')
            if ul:
                lis = ul.find_all('li')
                for li in lis:
                    lbl = li.find('span', class_='options_label')
                    opt_key = lbl.get_text(strip=True).upper() if lbl else ""
                    spans = li.find_all('span')
                    if len(spans) >= 2:
                        content_span = spans[-1]
                        options[opt_key] = content_span.get_text(strip=True)
                        options_html[opt_key] = "".join([str(c) for c in content_span.children]).strip()
                    elif len(spans) == 1:
                        options[opt_key] = spans[0].get_text(strip=True)
                        options_html[opt_key] = str(spans[0]).strip()

            # Solve Note
            solve_div = q_div.find('div', class_='solve-note')
            exp_html = ""
            exp_text = ""
            if solve_div:
                inner = solve_div.find('div')
                exp_html = "".join([str(c) for c in inner.children]).strip() if inner else "".join([str(c) for c in solve_div.children]).strip()
                exp_text = solve_div.get_text(strip=True)

            parsed_questions.append({
                'id': q_num,
                'canonical_subject': canon_subj,
                'subject_info': SUBJECT_MAP.get(canon_subj, {'bn': canon_subj, 'icon': '📌', 'color': '#059669'}),
                'question_text': q_text,
                'question_html': q_html,
                'options': options,
                'options_html': options_html,
                'correct_answer': correct_ans,
                'explanation_text': exp_text,
                'explanation_html': exp_html
            })

        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump({'meta': exam_meta, 'questions': parsed_questions}, f, ensure_ascii=False, indent=2)

        print(f"[{route_id}] Successfully parsed and saved {len(parsed_questions)} questions!")
        return route_id, len(parsed_questions)
    except Exception as e:
        print(f"[{route_id}] Error: {e}")
        return route_id, 0

print("Starting parallel fetch of all BCS exams...")
with ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(parse_exam, EXAMS_TO_FETCH))

print("\n--- Summary of Parsed Exams ---")
for r_id, count in results:
    print(f"  {r_id}: {count} questions")
