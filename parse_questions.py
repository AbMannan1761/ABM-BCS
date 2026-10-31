import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
from bs4 import BeautifulSoup

with open('raw_page.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

q_divs = soup.find_all('div', class_='single-question')
print(f"Total single-question divs: {len(q_divs)}")

subject_names = {
    'BANGLA': {'bn': 'বাংলা ভাষা ও সাহিত্য', 'en': 'Bengali Language & Literature', 'icon': '📚'},
    'ENGLISH': {'bn': 'ইংরেজি ভাষা ও সাহিত্য', 'en': 'English Language & Literature', 'icon': '📖'},
    'BANGLADESH-AFFAIRS': {'bn': 'বাংলাদেশ বিষয়াবলী', 'en': 'Bangladesh Affairs', 'icon': '🇧🇩'},
    'INTERNATIONAL-AFFAIRS': {'bn': 'আন্তর্জাতিক বিষয়াবলী', 'en': 'International Affairs', 'icon': '🌐'},
    'GEOGRAPHY': {'bn': 'ভূগোল, পরিবেশ ও দুর্যোগ ব্যবস্থাপনা', 'en': 'Geography & Disaster Management', 'icon': '🗺️'},
    'GENERAL-SCIENCE': {'bn': 'সাধারণ বিজ্ঞান', 'en': 'General Science', 'icon': '🔬'},
    'COMPUTER-AND-IT': {'bn': 'কম্পিউটার ও তথ্যপ্রযুক্তি', 'en': 'Computer & Information Technology', 'icon': '💻'},
    'MATHEMATICAL-REASONING': {'bn': 'গাণিতিক যুক্তি', 'en': 'Mathematical Reasoning', 'icon': '📐'},
    'MENTAL-ABILITY': {'bn': 'মানসিক দক্ষতা', 'en': 'Mental Ability', 'icon': '🧠'},
    'ETHICS': {'bn': 'নৈতিকতা, মূল্যবোধ ও সুশাসন', 'en': 'Ethics, Values & Good Governance', 'icon': '⚖️'}
}

questions_data = []

for idx, q_div in enumerate(q_divs):
    q_num = idx + 1
    raw_subj = q_div.get('data-subject', 'GENERAL').strip().upper()
    correct_ans = q_div.get('data-answer', '').strip().upper()
    
    # Title / Number
    h4 = q_div.find('h4')
    title = h4.get_text(strip=True) if h4 else f"Question {q_num}"
    
    # Description / Question Text
    desc_div = q_div.find('p', class_='description')
    q_html = ""
    q_text = ""
    if desc_div:
        # get inner content
        inner_div = desc_div.find('div')
        if inner_div:
            q_html = str(inner_div).strip()
            q_text = inner_div.get_text(strip=True)
        else:
            q_html = "".join([str(c) for c in desc_div.children]).strip()
            q_text = desc_div.get_text(strip=True)
            
    # Options
    options = {}
    options_html = {}
    ul = q_div.find('ul', class_='list-unstyled')
    if ul:
        lis = ul.find_all('li')
        for li in lis:
            lbl = li.find('span', class_='options_label')
            lbl_text = lbl.get_text(strip=True) if lbl else ""
            opt_key = lbl_text.upper() if lbl_text else ""
            
            # Find the option text span
            # usually span after input
            inp = li.find('input')
            if inp and not opt_key:
                opt_key = inp.get('value', '').strip().upper()
                
            # Content span is the last span
            spans = li.find_all('span')
            if len(spans) >= 2:
                content_span = spans[-1]
                options[opt_key] = content_span.get_text(strip=True)
                options_html[opt_key] = "".join([str(c) for c in content_span.children]).strip()
            elif len(spans) == 1:
                options[opt_key] = spans[0].get_text(strip=True)
                options_html[opt_key] = str(spans[0]).strip()
                
    # Solve note / explanation
    solve_div = q_div.find('div', class_='solve-note')
    explanation_html = ""
    explanation_text = ""
    if solve_div:
        # inner div
        inner = solve_div.find('div')
        if inner:
            explanation_html = "".join([str(c) for c in inner.children]).strip()
            explanation_text = inner.get_text(strip=True)
        else:
            explanation_html = "".join([str(c) for c in solve_div.children]).strip()
            explanation_text = solve_div.get_text(strip=True)
            
    questions_data.append({
        'id': q_num,
        'title': title,
        'subject_code': raw_subj,
        'subject_meta': subject_names.get(raw_subj, {'bn': raw_subj, 'en': raw_subj, 'icon': '📌'}),
        'question_text': q_text,
        'question_html': q_html,
        'options': options,
        'options_html': options_html,
        'correct_answer': correct_ans,
        'explanation_text': explanation_text,
        'explanation_html': explanation_html
    })

print(f"Parsed {len(questions_data)} questions.")
print("\nSample Question 1:")
print(json.dumps(questions_data[0], ensure_ascii=False, indent=2)[:500])

print("\nSample Question 24 (Math fraction):")
print(json.dumps(questions_data[23], ensure_ascii=False, indent=2)[:500])

# Check for any missing options or answers
missing_ans = [q['id'] for q in questions_data if not q['correct_answer']]
missing_opts = [q['id'] for q in questions_data if len(q['options']) < 2]
print(f"Missing answers: {missing_ans}")
print(f"Missing options: {missing_opts}")

# Write to questions.json
with open('questions.json', 'w', encoding='utf-8') as out_f:
    json.dump(questions_data, out_f, ensure_ascii=False, indent=2)

print("Saved questions.json successfully!")
