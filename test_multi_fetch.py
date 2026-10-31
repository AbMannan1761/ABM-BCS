import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
from bs4 import BeautifulSoup

def test_fetch(route):
    url = f"https://uttoron.academy/QuestionBank/QuestionPreview/{route}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        q_divs = soup.find_all('div', class_='single-question')
        print(f"[{route}] -> HTML size: {len(html)}, Questions count: {len(q_divs)}")
        if q_divs:
            q1 = q_divs[0]
            subj = q1.get('data-subject')
            ans = q1.get('data-answer')
            desc = q1.find('p', class_='description')
            q_text = desc.get_text(strip=True) if desc else ""
            print(f"   Q1: {q_text[:60]}... (Subject: {subj}, Ans: {ans})")
        return len(q_divs)
    except Exception as e:
        print(f"[{route}] Error: {e}")
        return 0

for r in ['47th-BCS', '46th-BCS', '45th-BCS', '44th-bcs', '43rd-bcs', '41st-bcs', '40th-bcs', '49th-BCS', '48th-BCS']:
    test_fetch(r)
