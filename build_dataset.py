import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('questions.json', encoding='utf-8') as f:
    questions = json.load(f)

# Specific manual mapping for the 18 questions that had missing subject
manual_blanks = {
    17: ('ENGLISH', 'English Literature'),
    53: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    62: ('COMPUTER-AND-IT', 'কম্পিউটার ও তথ্যপ্রযুক্তি'),
    64: ('ETHICS', 'নৈতিকতা, মূল্যবোধ ও সুশাসন'),
    110: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    118: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    124: ('BANGLA', 'বাংলা ভাষা ও ব্যাকরণ'),
    125: ('COMPUTER-AND-IT', 'কম্পিউটার ও তথ্যপ্রযুক্তি'),
    126: ('BANGLA', 'বাংলা সাহিত্য'),
    130: ('INTERNATIONAL-AFFAIRS', 'আন্তর্জাতিক বিষয়াবলী'),
    133: ('BANGLADESH-AFFAIRS', 'বাংলাদেশ বিষয়াবলী'),
    134: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    146: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    153: ('ETHICS', 'নৈতিকতা, মূল্যবোধ ও সুশাসন'),
    155: ('INTERNATIONAL-AFFAIRS', 'আন্তর্জাতিক বিষয়াবলী'),
    169: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    176: ('MATHEMATICAL-REASONING', 'গাণিতিক যুক্তি'),
    181: ('INTERNATIONAL-AFFAIRS', 'আন্তর্জাতিক বিষয়াবলী')
}

# Standard 10 BCS Subject definitions
CANONICAL_SUBJECTS = {
    'BANGLA': {
        'id': 'BANGLA',
        'name_bn': 'বাংলা ভাষা ও সাহিত্য',
        'name_en': 'Bengali Language & Literature',
        'icon': '📚',
        'color': '#2563eb',
        'bg_light': '#eff6ff',
        'bpsc_marks': 35
    },
    'ENGLISH': {
        'id': 'ENGLISH',
        'name_bn': 'ইংরেজি ভাষা ও সাহিত্য',
        'name_en': 'English Language & Literature',
        'icon': '📖',
        'color': '#7c3aed',
        'bg_light': '#f5f3ff',
        'bpsc_marks': 35
    },
    'BANGLADESH-AFFAIRS': {
        'id': 'BANGLADESH-AFFAIRS',
        'name_bn': 'বাংলাদেশ বিষয়াবলী',
        'name_en': 'Bangladesh Affairs',
        'icon': '🇧🇩',
        'color': '#059669',
        'bg_light': '#ecfdf5',
        'bpsc_marks': 30
    },
    'INTERNATIONAL-AFFAIRS': {
        'id': 'INTERNATIONAL-AFFAIRS',
        'name_bn': 'আন্তর্জাতিক বিষয়াবলী',
        'name_en': 'International Affairs',
        'icon': '🌐',
        'color': '#0284c7',
        'bg_light': '#f0f9ff',
        'bpsc_marks': 20
    },
    'GEOGRAPHY': {
        'id': 'GEOGRAPHY',
        'name_bn': 'ভূগোল, পরিবেশ ও দুর্যোগ ব্যবস্থাপনা',
        'name_en': 'Geography & Disaster Management',
        'icon': '🗺️',
        'color': '#0d9488',
        'bg_light': '#f0fdfa',
        'bpsc_marks': 10
    },
    'GENERAL-SCIENCE': {
        'id': 'GENERAL-SCIENCE',
        'name_bn': 'সাধারণ বিজ্ঞান',
        'name_en': 'General Science',
        'icon': '🔬',
        'color': '#d97706',
        'bg_light': '#fffbeb',
        'bpsc_marks': 15
    },
    'COMPUTER-AND-IT': {
        'id': 'COMPUTER-AND-IT',
        'name_bn': 'কম্পিউটার ও তথ্যপ্রযুক্তি',
        'name_en': 'Computer & Information Technology',
        'icon': '💻',
        'color': '#4f46e5',
        'bg_light': '#eef2ff',
        'bpsc_marks': 15
    },
    'MATHEMATICAL-REASONING': {
        'id': 'MATHEMATICAL-REASONING',
        'name_bn': 'গাণিতিক যুক্তি',
        'name_en': 'Mathematical Reasoning',
        'icon': '📐',
        'color': '#e11d48',
        'bg_light': '#fff1f2',
        'bpsc_marks': 15
    },
    'MENTAL-ABILITY': {
        'id': 'MENTAL-ABILITY',
        'name_bn': 'মানসিক দক্ষতা',
        'name_en': 'Mental Ability',
        'icon': '🧠',
        'color': '#9333ea',
        'bg_light': '#faf5ff',
        'bpsc_marks': 15
    },
    'ETHICS': {
        'id': 'ETHICS',
        'name_bn': 'নৈতিকতা, মূল্যবোধ ও সুশাসন',
        'name_en': 'Ethics, Values & Good Governance',
        'icon': '⚖️',
        'color': '#ca8a04',
        'bg_light': '#fefce8',
        'bpsc_marks': 10
    }
}

for q in questions:
    qid = q['id']
    raw_subj = q.get('subject_code', '').strip().upper()
    sub_category = ''
    canon_id = ''

    if qid in manual_blanks:
        canon_id, sub_category = manual_blanks[qid]
    elif raw_subj == 'BANGLADESH-AFFAIRS':
        canon_id = 'BANGLADESH-AFFAIRS'
        sub_category = 'বাংলাদেশ বিষয়াবলী'
    elif raw_subj == 'MENTAL-ABILITY':
        canon_id = 'MENTAL-ABILITY'
        sub_category = 'মানসিক দক্ষতা'
    elif raw_subj in ('BANGLA-LANGUAGE', 'BANGLA-LITERATURE'):
        canon_id = 'BANGLA'
        sub_category = 'বাংলা সাহিত্য' if raw_subj == 'BANGLA-LITERATURE' else 'বাংলা ভাষা ও ব্যাকরণ'
    elif raw_subj in ('ENGLISH-LANGUAGE', 'ENGLISH-LITERATURE'):
        canon_id = 'ENGLISH'
        sub_category = 'English Literature' if raw_subj == 'ENGLISH-LITERATURE' else 'English Language & Grammar'
    elif raw_subj == 'INTERNATIONAL-AFFAIRS':
        canon_id = 'INTERNATIONAL-AFFAIRS'
        sub_category = 'আন্তর্জাতিক বিষয়াবলী'
    elif raw_subj == 'GEOGRAPHY-ENVIRONMENT-AND-DIGESTER-MANAGEMENT':
        canon_id = 'GEOGRAPHY'
        sub_category = 'ভূগোল, পরিবেশ ও দুর্যোগ ব্যবস্থাপনা'
    elif raw_subj == 'GENERAL-SCIENCE':
        canon_id = 'GENERAL-SCIENCE'
        sub_category = 'সাধারণ বিজ্ঞান'
    elif raw_subj == 'COMPUTER-AND-INFORMATION-TECHNOLOGY':
        canon_id = 'COMPUTER-AND-IT'
        sub_category = 'কম্পিউটার ও তথ্যপ্রযুক্তি'
    elif raw_subj == 'MATHEMATICAL-REASONING':
        canon_id = 'MATHEMATICAL-REASONING'
        sub_category = 'গাণিতিক যুক্তি'
    elif raw_subj == 'ETHICS-VALUES-GOOD-GOVERNANCE':
        canon_id = 'ETHICS'
        sub_category = 'নৈতিকতা, মূল্যবোধ ও সুশাসন'
    else:
        canon_id = 'BANGLADESH-AFFAIRS'
        sub_category = 'বাংলাদেশ বিষয়াবলী'

    # Special case Q119
    if qid == 119:
        q['correct_answer'] = 'C'
        q['correct_answer_alt'] = ['C', 'D']
        q['is_multi_correct'] = True

    # Special case Q191
    if qid == 191:
        if 'বিশ্বব্যাংক গ্রুপের ৫টি প্রধান অঙ্গসংগঠন' not in q['explanation_html']:
            q['explanation_html'] += """
<div style="margin-top:10px; padding:10px; background:#f0fdf4; border-radius:6px; border:1px solid #bbf7d0; font-size:14px;">
<strong>বিশ্বব্যাংক গ্রুপের ৫টি প্রধান অঙ্গসংগঠন:</strong>
<ul style="margin:6px 0 0 20px; list-style-type:disc;">
  <li><strong>IBRD:</strong> International Bank for Reconstruction and Development (প্রতিষ্ঠিত: ১৯৪৪)</li>
  <li><strong>IDA:</strong> International Development Association (প্রতিষ্ঠিত: ১৯৬০) - স্বল্পোন্নত দেশগুলোকে সহজ শর্তে দীর্ঘমেয়াদি ঋণ দেয়</li>
  <li><strong>IFC:</strong> International Finance Corporation (প্রতিষ্ঠিত: ১৯৫৬) - বেসরকারি খাতে বিনিয়োগ ও অর্থায়ন করে</li>
  <li><strong>MIGA:</strong> Multilateral Investment Guarantee Agency (প্রতিষ্ঠিত: ১৯৮৮) - বিদেশি বিনিয়োগকারীদের রাজনৈতিক ঝুঁকি ও যুদ্ধকালীন বীমা দেয়</li>
  <li><strong>ICSID:</strong> International Centre for Settlement of Investment Disputes (প্রতিষ্ঠিত: ১৯৬৬) - সরকার ও বিদেশি বিনিয়োগকারীদের বিরোধ নিষ্পত্তি করে</li>
</ul>
</div>
"""

    q['canonical_subject'] = canon_id
    q['sub_category'] = sub_category
    q['subject_info'] = CANONICAL_SUBJECTS[canon_id]

# Calculate final stats per canonical subject
final_stats = {k: {**v, 'count': 0} for k, v in CANONICAL_SUBJECTS.items()}
for q in questions:
    subj = q['canonical_subject']
    final_stats[subj]['count'] += 1

print("\nFinal Subject Distribution (Total: 200 questions):")
for k, v in final_stats.items():
    print(f"  {v['icon']} {v['name_bn']} ({k}): {v['count']} questions")

# Save updated questions.json
with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

# Save questions_data.js for instant browser usage
js_payload = f"""/**
 * ABM BCS Question Bank - 50th BCS Preliminary Model Test
 * Total Questions: 200
 * Generated & Structured for ABM BCS
 */
window.BCS_METADATA = {{
  title: "ABM BCS - ৫০তম বিসিএস প্রিলিমিনারি পূর্ণাঙ্গ প্রশ্নব্যাংক ও মডেল টেস্ট",
  shortTitle: "ABM BCS",
  totalQuestions: 200,
  totalMarks: 200,
  durationMinutes: 120,
  negativeMarking: 0.50,
  sourceExam: "৫০তম বিসিএস (50th BCS)",
  createdYear: 2026
}};

window.BCS_SUBJECTS = {json.dumps(final_stats, ensure_ascii=False, indent=2)};

window.BCS_QUESTIONS = {json.dumps(questions, ensure_ascii=False, indent=2)};
"""

with open('questions_data.js', 'w', encoding='utf-8') as f:
    f.write(js_payload)

print("\nSuccessfully updated questions.json and generated questions_data.js!")
