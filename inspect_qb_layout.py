import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
from bs4 import BeautifulSoup

req = urllib.request.Request('https://uttoron.academy/QuestionBank', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

with open('qb_full.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved qb_full.html, size:", len(html))

# Print all accordion headers
for header in soup.find_all(class_=lambda c: c and 'accordion' in str(c).lower()):
    print("Accordion item:", header.get_text(strip=True)[:100])

# Find the main container
main = soup.find('main') or soup.find('body')
for h in main.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'button', 'a']):
    t = h.get_text(strip=True)
    if any(k in t for k in ['Preli', 'Written', 'Question', 'বিসিএস', 'আরও দেখুন']):
        print(f"[{h.name}] {t} -> href={h.get('href')}")
