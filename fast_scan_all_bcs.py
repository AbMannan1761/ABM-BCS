import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def suffix(n):
    if 11 <= (n % 100) <= 13: return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')

def check_bcs(i):
    candidates = [f'{i}{suffix(i)}-bcs', f'{i}{suffix(i)}-BCS', f'{i}-bcs', f'{i}-BCS']
    for r in candidates:
        url = f'https://uttoron.academy/QuestionBank/QuestionPreview/{r}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                qs = soup.find_all(attrs={'data-answer': True})
                if not qs:
                    qs = soup.find_all('div', class_='single-question')
                if len(qs) > 0:
                    return i, r, len(qs)
        except Exception:
            pass
    return i, None, 0

print("Scanning BCS 1 to 50 in parallel...")
results = {}
with ThreadPoolExecutor(max_workers=20) as executor:
    for i, route, count in executor.map(check_bcs, range(1, 51)):
        if count > 0:
            results[i] = (route, count)
            print(f"[{i}th BCS] FOUND: {route} with {count} questions", flush=True)
        else:
            print(f"[{i}th BCS] No question data on uttoron", flush=True)

print("\n--- SUMMARY ---")
print(f"Total exams with question data: {len(results)}")
for i in sorted(results.keys()):
    print(f"{i}th BCS: {results[i][0]} ({results[i][1]} Qs)")
