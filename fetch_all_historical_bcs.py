import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
import json
import urllib.request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

os.makedirs('bcs_data', exist_ok=True)

HISTORICAL_EXAMS = [
    {'id': '10th-bcs', 'name': '10th BCS', 'sub': 'General', 'date': '1989-12-22'},
    {'id': '14th-bcs', 'name': '14th BCS', 'sub': 'General', 'date': '1992-05-15'},
    {'id': '15th-bcs', 'name': '15th BCS', 'sub': 'General', 'date': '1993-06-11'},
    {'id': '16th-bcs', 'name': '16th BCS', 'sub': 'General', 'date': '1994-04-08'},
    {'id': '17th-bcs', 'name': '17th BCS', 'sub': 'General', 'date': '1995-05-19'},
    {'id': '18th-bcs', 'name': '18th BCS', 'sub': 'General', 'date': '1996-06-28'},
    {'id': '19th-bcs', 'name': '19th BCS', 'sub': 'Special', 'date': '1997-07-11'},
    {'id': '20th-bcs', 'name': '20th BCS', 'sub': 'General', 'date': '1998-05-29'},
    {'id': '21st-bcs', 'name': '21st BCS', 'sub': 'General', 'date': '2000-03-31'},
    {'id': '22nd-bcs', 'name': '22nd BCS', 'sub': 'Special', 'date': '2000-11-24'},
    {'id': '23rd-bcs', 'name': '23rd BCS', 'sub': 'General', 'date': '2001-05-25'},
    {'id': '24th-bcs', 'name': '24th BCS', 'sub': 'General', 'date': '2002-06-21'},
    {'id': '25th-bcs', 'name': '25th BCS', 'sub': 'General', 'date': '2003-09-12'},
    {'id': '26th-bcs', 'name': '26th BCS', 'sub': 'General', 'date': '2004-10-15'},
    {'id': '27th-bcs', 'name': '27th BCS', 'sub': 'General', 'date': '2007-01-19'},
    {'id': '28th-bcs', 'name': '28th BCS', 'sub': 'General', 'date': '2008-11-28'},
    {'id': '29th-bcs', 'name': '29th BCS', 'sub': 'General', 'date': '2009-08-07'},
    {'id': '30th-bcs', 'name': '30th BCS', 'sub': 'General', 'date': '2010-06-18'},
    {'id': '31st-bcs', 'name': '31st BCS', 'sub': 'General', 'date': '2011-05-27'},
    {'id': '32nd-bcs', 'name': '32nd BCS', 'sub': 'Special', 'date': '2011-12-09'},
    {'id': '33rd-bcs', 'name': '33rd BCS', 'sub': 'General', 'date': '2012-06-01'},
    {'id': '34th-bcs', 'name': '34th BCS', 'sub': 'General', 'date': '2013-05-24'}
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

def parse_historical_exam(exam_meta):
    route_id = exam_meta['id']
    target_file = f"bcs_data/{route_id}.json"
    
    url = f"https://uttoron.academy/QuestionBank/QuestionPreview/{route_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to fetch {route_id}: {e}")
        return None

    soup = BeautifulSoup(html, 'html.parser')
    q_divs = soup.find_all(attrs={'data-answer': True})
    if not q_divs:
        q_divs = soup.find_all('div', class_='single-question')

    parsed_questions = []
    q_counter = 1
    
    for q_div in q_divs:
        raw_subj = q_div.get('data-subject', '')
        canon_subj = get_canonical_subject(raw_subj)
        subj_info = SUBJECT_MAP.get(canon_subj, SUBJECT_MAP['BANGLADESH-AFFAIRS'])

        correct_ans = (q_div.get('data-answer') or '').strip().upper()

        # Question title / text
        title_div = q_div.find('div', class_='p-2') or q_div.find(class_='question-title') or q_div.find(class_='title')
        q_text = ''
        q_html = ''
        if title_div:
            q_html = str(title_div)
            q_text = title_div.get_text(separator=' ', strip=True)
            # Remove leading "Question X" or "X."
            q_text = re.sub(r'^(Question\s*\d+\s*[:.-]?|\d+\s*[:.-]?)\s*', '', q_text, flags=re.I).strip()
        else:
            q_text = f"প্রশ্ন {q_counter}"
            q_html = f"<div>{q_text}</div>"

        # Options
        options = {'A': '', 'B': '', 'C': '', 'D': ''}
        options_html = {'A': '', 'B': '', 'C': '', 'D': ''}

        opt_items = q_div.find_all('li') or q_div.find_all(class_='option')
        for i, opt in enumerate(opt_items[:4]):
            key = ['A', 'B', 'C', 'D'][i]
            opt_text = opt.get_text(separator=' ', strip=True)
            # Remove leading A, B, C, D or (a), (b)
            clean_text = re.sub(r'^[A-Da-dক-ঘ][.\):\-]?\s*', '', opt_text).strip()
            options[key] = clean_text or opt_text
            options_html[key] = str(opt)

        # Explanation
        exp_div = q_div.find('div', class_='solve-note') or q_div.find(class_='explanation') or q_div.find(class_='ans-explanation')
        exp_text = ''
        exp_html = ''
        if exp_div:
            exp_html = str(exp_div)
            exp_text = exp_div.get_text(separator=' ', strip=True)

        parsed_questions.append({
            'id': q_counter,
            'canonical_subject': canon_subj,
            'subject_info': subj_info,
            'question_text': q_text,
            'question_html': q_html,
            'options': options,
            'options_html': options_html,
            'correct_answer': correct_ans,
            'explanation_text': exp_text,
            'explanation_html': exp_html
        })
        q_counter += 1

    result_data = {
        'meta': exam_meta,
        'questions': parsed_questions
    }

    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully processed {route_id}: {len(parsed_questions)} questions saved.")
    return route_id, len(parsed_questions)

print(f"Fetching and parsing {len(HISTORICAL_EXAMS)} historical BCS exams concurrently...")
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(parse_historical_exam, HISTORICAL_EXAMS))

print("Historical exams fetch complete!")
