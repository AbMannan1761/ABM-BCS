import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

with open('qb_full.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

print("--- Top Nav ---")
top = soup.find('section', class_='topNav-section')
if top:
    print(top.prettify())

print("\n--- Header Navbar ---")
header = soup.find('header')
if header:
    print(header.prettify()[:1000])

print("\n--- Question Bank Title & Accordion ---")
head_qb = soup.find('div', class_='head')
if head_qb:
    print(head_qb.prettify())

acc = soup.find('div', class_='accordion')
if acc:
    print(acc.prettify()[:1500])
