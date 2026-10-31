import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
from bs4 import BeautifulSoup

recent_bcs = [
    ('50th BCS', '50th-bcs'),
    ('49th BCS', '49th-BCS'),
    ('48th BCS', '48th-BCS'),
    ('47th BCS', '47th-BCS'),
    ('46th BCS', '46th-BCS'),
    ('45th BCS', '45th-BCS'),
    ('44th BCS', '44th-bcs'),
    ('43rd BCS', '43rd-bcs'),
    ('42nd BCS', '42nd-bcs'),
    ('41st BCS', '41st-bcs'),
    ('40th BCS', '40th-bcs'),
    ('39th BCS', '39th-bcs'),
    ('38th BCS', '38th-bcs'),
    ('37th BCS', '37th-bcs'),
    ('36th BCS', '36th-bcs'),
    ('35th BCS', '35th-bcs')
]

for name, route in recent_bcs:
    url = f"https://uttoron.academy/QuestionBank/QuestionPreview/{route}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        qs = soup.find_all('div', class_='single-question')
        print(f"{name} ({route}) -> {len(qs)} questions")
    except Exception as e:
        print(f"{name} ({route}) -> Error: {e}")
