import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from bs4 import BeautifulSoup

with open('qb_full.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

accordions = []
for acc in soup.find_all('div', class_='accordion-item'):
    header = acc.find('h2', class_='accordion-header')
    header_text = header.get_text(strip=True) if header else ""
    body = acc.find('div', class_='accordion-body')
    cards = []
    if body:
        for card in body.find_all('div', class_='card'):
            h2 = card.find('h2')
            title = h2.get_text(strip=True) if h2 else ""
            spans = [s.get_text(strip=True) for s in card.find_all('span')]
            a = card.find('a', href=True)
            href = a['href'] if a else card.find('a').get('data-route-id', '') if card.find('a') else ""
            cards.append({
                'title': title,
                'sub1': spans[0] if len(spans) > 0 else '',
                'sub2': spans[1] if len(spans) > 1 else '',
                'route': href
            })
    accordions.append({
        'header': header_text,
        'cards': cards
    })

print(f"Total accordions found: {len(accordions)}")
for a in accordions:
    print(f"Accordion: '{a['header']}' ({len(a['cards'])} cards)")
    for c in a['cards'][:6]:
        print(f"   {c['title']} | {c['sub1']} | {c['sub2']} -> {c['route']}")

with open('qb_accordions.json', 'w', encoding='utf-8') as f:
    json.dump(accordions, f, ensure_ascii=False, indent=2)
print("Saved qb_accordions.json")
