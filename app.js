/**
 * ABM BCS - Complete Question Bank & Exam Application
 * Perfectly reproduces the uttoron.academy Question Bank view
 */

(function () {
  'use strict';

  // --- State ---
  const state = {
    accordions: window.QB_ACCORDIONS || [],
    portalData: window.PORTAL_DATA || {},
    allExams: window.ALL_BCS_EXAMS || {},
    currentExamId: '50th-bcs',
    currentExamMeta: { name: '50th BCS', sub: 'General', date: '2026-01-30' },
    allQuestions: window.BCS_QUESTIONS || [],
    subjects: window.BCS_SUBJECTS || {},
    
    // Exam / Practice
    examMode: 'study', // 'study' | 'exam'
    activeSubject: 'ALL',
    searchQuery: '',
    currentPage: 1,
    pageSize: 10,
    userAnswers: {},
    bookmarks: new Set(JSON.parse(localStorage.getItem('abm_bcs_bookmarks') || '[]')),
    soundEnabled: localStorage.getItem('abm_bcs_sound') !== 'false',
    theme: localStorage.getItem('abm_bcs_theme') || 'light',
    
    // Exam Timer
    exam: {
      totalSeconds: 120 * 60,
      remainingSeconds: 120 * 60,
      timerId: null,
      isPaused: false,
      isSubmitted: false,
      startTime: null,
      endTime: null
    }
  };

  // --- Web Audio Synthesizer ---
  let audioCtx = null;
  function getAudioContext() {
    if (!audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) audioCtx = new AudioCtxClass();
    }
    return audioCtx;
  }

  function playSound(type) {
    if (!state.soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      if (ctx.state === 'suspended') ctx.resume();

      const now = ctx.currentTime;
      if (type === 'correct') {
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();

        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(587.33, now);
        osc1.frequency.exponentialRampToValueAtTime(880, now + 0.15);

        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(880, now + 0.1);
        osc2.frequency.exponentialRampToValueAtTime(1174.66, now + 0.25);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);

        osc1.start(now);
        osc2.start(now + 0.1);
        osc1.stop(now + 0.35);
        osc2.stop(now + 0.35);

      } else if (type === 'wrong') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(180, now);
        osc.frequency.exponentialRampToValueAtTime(110, now + 0.2);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.25);

      } else if (type === 'click') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(600, now);
        gain.gain.setValueAtTime(0.04, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.05);
      }
    } catch (e) {
      console.warn('Audio play error:', e);
    }
  }

  // --- KaTeX Math Renderer ---
  function renderKaTeX() {
    if (window.renderMathInElement) {
      try {
        const container = document.getElementById('questionsContainer');
        if (container) {
          window.renderMathInElement(container, {
            delimiters: [
              { left: '$$', right: '$$', display: true },
              { left: '\\[', right: '\\]', display: true },
              { left: '\\(', right: '\\)', display: false },
              { left: '$', right: '$', display: false }
            ],
            throwOnError: false
          });
        }
      } catch (err) {
        console.warn('KaTeX render error:', err);
      }
    }
  }

  // --- Dynamic Exam Loader & Switcher ---
  function loadAndOpenExam(routeId, mode = 'study') {
    const bundle = window.ALL_BCS_EXAMS || {};
    let examData = bundle[routeId] || bundle[routeId.toLowerCase()] || Object.entries(bundle).find(([k]) => k.toLowerCase() === (routeId || '').toLowerCase())?.[1];

    // Fallback for 50th BCS if not in bundle directly
    if (!examData && (routeId === '50th-bcs' || routeId === '50th BCS')) {
      examData = {
        meta: { name: '50th BCS', sub: 'General', date: '2026-01-30' },
        questions: window.BCS_QUESTIONS || []
      };
    }

    if (!examData || !examData.questions || examData.questions.length === 0) {
      alert(`দুঃখিত, ${routeId} পরীক্ষার প্রশ্নমালা বর্তমানে প্রস্তুত হচ্ছে।`);
      return;
    }

    state.currentExamId = routeId;
    state.currentExamMeta = examData.meta || { name: routeId, sub: 'General' };
    state.allQuestions = examData.questions;
    state.userAnswers = {}; // reset answers for fresh exam
    state.exam.remainingSeconds = examData.questions.length <= 100 ? 60 * 60 : 120 * 60; // 1 hour for 100 Qs, 2 hours for 200 Qs
    state.exam.totalSeconds = state.exam.remainingSeconds;
    state.exam.isSubmitted = false;
    state.exam.isPaused = false;
    if (state.exam.timerId) {
      clearInterval(state.exam.timerId);
      state.exam.timerId = null;
    }

    // Recompute subject distribution for this specific exam
    const newSubjects = {};
    state.allQuestions.forEach(q => {
      const code = q.canonical_subject;
      if (!newSubjects[code]) {
        newSubjects[code] = {
          id: code,
          name_bn: q.subject_info.bn,
          icon: q.subject_info.icon,
          color: q.subject_info.color,
          count: 0
        };
      }
      newSubjects[code].count++;
    });
    state.subjects = newSubjects;

    // Update Modal Header Title & Subtitle
    const titleEl = document.getElementById('modalExamTitle');
    const subEl = document.getElementById('modalExamSub');
    if (titleEl) {
      titleEl.textContent = `${state.currentExamMeta.name} (${state.currentExamMeta.sub}) পূর্ণাঙ্গ পরীক্ষা ও অনুশীলন`;
    }
    if (subEl) {
      const durationMins = Math.floor(state.exam.totalSeconds / 60);
      subEl.textContent = `${state.allQuestions.length}টি প্রশ্ন | ${durationMins} মিনিট | নেগেটিভ মার্কিং -০.৫০`;
    }

    openExamModal(mode);
  }

  // --- Render Question Bank Accordions & Cards ---
  function initQuestionBankCards() {
    const preliAcc = state.accordions.find(a => a.header.includes('Preli Question'));
    if (!preliAcc) return;

    const cards = preliAcc.cards;
    const bundle = window.ALL_BCS_EXAMS || {};

    function findExamInBundle(route) {
      if (!route) return null;
      if (bundle[route]) return bundle[route];
      const lower = route.toLowerCase();
      if (bundle[lower]) return bundle[lower];
      for (const k in bundle) {
        if (k.toLowerCase() === lower) return bundle[k];
      }
      return null;
    }

    // Initial 4 cards: attach click handlers
    const initialGrid = document.getElementById('preliCardsInitialGrid');
    if (initialGrid) {
      initialGrid.innerHTML = '';
      for (let i = 0; i < Math.min(4, cards.length); i++) {
        const c = cards[i];
        const examItem = findExamInBundle(c.route);
        const isLoaded = !!examItem || c.route === '50th-bcs';
        const qCount = examItem ? examItem.questions.length : (window.BCS_QUESTIONS ? window.BCS_QUESTIONS.length : 200);
        const cardDiv = document.createElement('div');
        cardDiv.className = `qb-exam-card ${c.route === '50th-bcs' ? 'active-50th' : ''}`;
        cardDiv.innerHTML = `
          <div style="font-size:0.75rem; color:${isLoaded ? '#059669' : '#e31c25'}; font-weight:700; text-align:center; margin-bottom:2px;">
            <i class="fa-solid fa-circle-check"></i> ${isLoaded ? qCount + 'টি প্রশ্ন যুক্ত' : 'শীঘ্রই আসছে'}
          </div>
          <h4>${c.title}</h4>
          <div class="qb-exam-meta" style="flex-direction:column; align-items:flex-start; gap:2px;">
            <span>${c.sub1 || 'General'}</span>
            <span>${c.sub2}</span>
          </div>
        `;
        cardDiv.onclick = () => loadAndOpenExam(c.route, 'study');
        initialGrid.appendChild(cardDiv);
      }
    }

    // Extended cards (5 to end):
    const extGrid = document.getElementById('preliCardsExtendedGrid');
    if (extGrid && cards.length > 4) {
      extGrid.innerHTML = '';
      for (let i = 4; i < cards.length; i++) {
        const c = cards[i];
        const examItem = findExamInBundle(c.route);
        const isLoaded = !!examItem;
        const countText = isLoaded ? `${examItem.questions.length}টি প্রশ্ন যুক্ত` : 'বিসিএস প্রশ্ন';
        const cardDiv = document.createElement('div');
        cardDiv.className = 'qb-exam-card';
        cardDiv.innerHTML = `
          <div style="font-size:0.72rem; color:${isLoaded ? '#059669' : '#94a3b8'}; font-weight:700; text-align:center; margin-bottom:2px;">
            <i class="${isLoaded ? 'fa-solid fa-check-circle' : 'fa-regular fa-clock'}"></i> ${countText}
          </div>
          <h4>${c.title}</h4>
          <div class="qb-exam-meta" style="flex-direction:column; align-items:flex-start; gap:2px;">
            <span>${c.sub1 || 'General'}</span>
            <span>${c.sub2}</span>
          </div>
        `;
        cardDiv.onclick = () => {
          if (isLoaded) {
            loadAndOpenExam(c.route, 'study');
          } else {
            alert(`${c.title} (${c.sub1}) পরীক্ষার প্রশ্নমালা লোড হচ্ছে...`);
          }
        };
        extGrid.appendChild(cardDiv);
      }
    }

    // Written Question Cards
    const writtenAcc = state.accordions.find(a => a.header.includes('Written Question'));
    const writtenGrid = document.getElementById('writtenCardsGrid');
    if (writtenAcc && writtenGrid) {
      let wHtml = '';
      writtenAcc.cards.forEach(wc => {
        wHtml += `
          <div class="qb-exam-card" onclick="alert('${wc.title} লিখিত পরীক্ষার সকল বিষয়ের প্রশ্নপত্র সংরক্ষিত রয়েছে।')">
            <h4 style="margin-top:0.8rem;">${wc.title}</h4>
            <div class="qb-exam-meta">
              <span>Written Exam</span>
              <span style="color:#e31c25; font-weight:600;"><i class="fa-solid fa-file-pdf"></i> প্রশ্নপত্র</span>
            </div>
          </div>
        `;
      });
      writtenGrid.innerHTML = wHtml;
    }

    // Toggle "আরও দেখুন ∨" button
    const btnShowMore = document.getElementById('btnShowMorePreli');
    if (btnShowMore && extGrid) {
      btnShowMore.addEventListener('click', () => {
        const isHidden = extGrid.style.display === 'none';
        extGrid.style.display = isHidden ? 'grid' : 'none';
        document.getElementById('showMoreText').textContent = isHidden ? 'সংক্ষিপ্ত করুন' : 'আরও দেখুন';
        document.getElementById('showMoreIcon').className = isHidden ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down';
      });
    }

    // Preli Accordion Header Toggle
    const accHeaderPreli = document.getElementById('accHeaderPreli');
    const accItemPreli = document.getElementById('accItemPreli');
    if (accHeaderPreli && accItemPreli) {
      accHeaderPreli.addEventListener('click', () => {
        accItemPreli.classList.toggle('collapsed');
      });
    }
  }

  // --- Open / Close Exam Interactive Modal ---
  function openExamModal(mode = 'study') {
    state.examMode = mode;
    const modal = document.getElementById('examModal50th');
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
      setExamSubMode(mode);
      renderSubjectPills();
      renderQuestions();
    }
  }

  function closeExamModal() {
    const modal = document.getElementById('examModal50th');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = 'auto';
      if (state.exam.timerId) {
        clearInterval(state.exam.timerId);
        state.exam.timerId = null;
      }
    }
  }

  // --- 50th BCS Subject Pills & Filtering ---
  function renderSubjectPills() {
    const container = document.getElementById('subjectFilterContainer');
    if (!container) return;

    let html = `
      <button class="subject-pill ${state.activeSubject === 'ALL' ? 'active' : ''}" data-subject="ALL">
        <span>সকল বিষয়</span>
        <span class="count">${state.allQuestions.length}</span>
      </button>
    `;

    Object.values(state.subjects).forEach(subj => {
      const isAct = state.activeSubject === subj.id;
      html += `
        <button class="subject-pill ${isAct ? 'active' : ''}" data-subject="${subj.id}">
          <span>${subj.icon} ${subj.name_bn}</span>
          <span class="count">${subj.count}</span>
        </button>
      `;
    });

    container.innerHTML = html;

    container.querySelectorAll('.subject-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        state.activeSubject = btn.dataset.subject;
        state.currentPage = 1;
        renderSubjectPills();
        renderQuestions();
      });
    });
  }

  function getFilteredQuestions() {
    let list = state.allQuestions;

    if (state.activeSubject !== 'ALL') {
      list = list.filter(q => q.canonical_subject === state.activeSubject);
    }

    if (state.searchQuery.trim()) {
      const qLower = state.searchQuery.trim().toLowerCase();
      list = list.filter(q => {
        const textMatch = q.question_text.toLowerCase().includes(qLower);
        const expMatch = q.explanation_text.toLowerCase().includes(qLower);
        const optMatch = Object.values(q.options || {}).some(opt => opt.toLowerCase().includes(qLower));
        const subMatch = (q.subject_info.name_bn || '').toLowerCase().includes(qLower) || 
                         (q.subject_info.name_en || '').toLowerCase().includes(qLower);
        return textMatch || expMatch || optMatch || subMatch;
      });
    }

    return list;
  }

  function renderQuestions() {
    const container = document.getElementById('questionsContainer');
    if (!container) return;

    const filtered = getFilteredQuestions();
    const isExam = state.examMode === 'exam';
    const isSubmitted = state.exam.isSubmitted;

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-folder-open"></i>
          <h3>কোনো প্রশ্ন খুঁজে পাওয়া যায়নি!</h3>
          <p>আপনার অনুসন্ধান বা ফিল্টার মানদণ্ড পরিবর্তন করে আবার চেষ্টা করুন।</p>
        </div>
      `;
      document.getElementById('paginationBar').style.display = 'none';
      return;
    }

    let displayList = filtered;
    const paginationBar = document.getElementById('paginationBar');
    if (!isExam) {
      const totalPages = Math.ceil(filtered.length / state.pageSize);
      if (state.currentPage > totalPages) state.currentPage = totalPages;
      if (state.currentPage < 1) state.currentPage = 1;

      const startIndex = (state.currentPage - 1) * state.pageSize;
      displayList = filtered.slice(startIndex, startIndex + state.pageSize);

      if (paginationBar) {
        paginationBar.style.display = totalPages > 1 ? 'flex' : 'none';
        document.getElementById('pageInfo').textContent = `পৃষ্ঠা ${state.currentPage} / ${totalPages} (মোট ${filtered.length} টি)`;
        document.getElementById('prevPageBtn').disabled = state.currentPage <= 1;
        document.getElementById('nextPageBtn').disabled = state.currentPage >= totalPages;
      }
    } else {
      if (paginationBar) paginationBar.style.display = 'none';
    }

    let cardsHtml = '';
    displayList.forEach(q => {
      const qId = q.id;
      const isBookmarked = state.bookmarks.has(qId);
      const userSelected = state.userAnswers[qId];
      const correctAns = q.correct_answer;
      const isAnswered = !!userSelected;

      cardsHtml += `
        <article class="question-card" id="qcard_${qId}" data-id="${qId}">
          <div class="question-card-header">
            <div class="q-meta-left">
              <span class="q-number-badge"># ${qId}</span>
              <span class="q-subject-tag">${q.subject_info.icon} ${q.subject_info.name_bn}</span>
              ${q.sub_category ? `<span class="q-subject-tag" style="background:transparent; opacity:0.8;">${q.sub_category}</span>` : ''}
            </div>
            <div class="q-actions-right">
              <button class="card-tool-btn copy-q-btn" data-id="${qId}" title="প্রশ্ন ও অপশন কপি করুন">
                <i class="fa-regular fa-copy"></i>
              </button>
              <button class="card-tool-btn bookmark-btn ${isBookmarked ? 'bookmarked' : ''}" data-id="${qId}" title="${isBookmarked ? 'বুকমার্ক সরান' : 'সংরক্ষণ করুন'}">
                <i class="${isBookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
              </button>
            </div>
          </div>

          <div class="question-title">
            ${q.question_html || q.question_text}
          </div>

          <div class="options-list">
      `;

      ['A', 'B', 'C', 'D'].forEach(letter => {
        const optText = q.options[letter] || q.options_html[letter] || '';
        if (!optText) return;

        let optClass = 'option-item';
        if (isExam && !isSubmitted) {
          if (userSelected === letter) optClass += ' selected';
        } else {
          if (isAnswered || isSubmitted) {
            optClass += ' locked';
            if (letter === correctAns || (q.correct_answer_alt && q.correct_answer_alt.includes(letter))) {
              optClass += ' correct';
            } else if (userSelected === letter) {
              optClass += ' wrong';
            }
          }
        }

        cardsHtml += `
          <div class="${optClass}" data-qid="${qId}" data-letter="${letter}">
            <div class="option-letter">${letter}</div>
            <div class="option-text">${q.options_html[letter] || optText}</div>
          </div>
        `;
      });

      cardsHtml += `</div>`;

      if (!isExam || isSubmitted) {
        const hasExplanation = (q.explanation_html && q.explanation_html.trim()) || (q.explanation_text && q.explanation_text.trim());
        if (hasExplanation) {
          const autoExpand = isSubmitted && isAnswered;
          cardsHtml += `
            <div class="explanation-wrapper">
              <button class="explanation-toggle-btn" data-qid="${qId}">
                <i class="fa-solid fa-lightbulb"></i>
                <span>${autoExpand ? 'ব্যাখ্যা লুকান' : 'ব্যাখ্যা দেখুন'}</span>
              </button>
              <div class="explanation-box" id="exp_${qId}" style="${autoExpand ? '' : 'display:none;'}">
                ${q.explanation_html || q.explanation_text}
              </div>
            </div>
          `;
        }
      }

      cardsHtml += `</article>`;
    });

    container.innerHTML = cardsHtml;
    attachInteractions(container);
    renderKaTeX();

    if (isExam) updateExamSidebar();
  }

  function attachInteractions(parent) {
    if (!parent) return;

    parent.querySelectorAll('.option-item').forEach(optEl => {
      optEl.addEventListener('click', () => {
        const qId = parseInt(optEl.dataset.qid, 10);
        const letter = optEl.dataset.letter;
        handleOptionSelect(qId, letter);
      });
    });

    parent.querySelectorAll('.bookmark-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const qId = parseInt(btn.dataset.id, 10);
        toggleBookmark(qId, btn);
      });
    });

    parent.querySelectorAll('.copy-q-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const qId = parseInt(btn.dataset.id, 10);
        copyQuestion(qId, btn);
      });
    });

    parent.querySelectorAll('.explanation-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const qId = btn.dataset.qid;
        const box = document.getElementById(`exp_${qId}`);
        const span = btn.querySelector('span');
        if (box) {
          const isHidden = box.style.display === 'none';
          box.style.display = isHidden ? 'block' : 'none';
          span.textContent = isHidden ? 'ব্যাখ্যা লুকান' : 'ব্যাখ্যা দেখুন';
          if (isHidden) renderKaTeX();
        }
      });
    });
  }

  function handleOptionSelect(qId, letter) {
    const q = state.allQuestions.find(item => item.id === qId);
    if (!q) return;

    const isExam = state.examMode === 'exam';
    if (isExam && state.exam.isSubmitted) return;
    if (!isExam && state.userAnswers[qId]) return;

    state.userAnswers[qId] = letter;

    if (!isExam) {
      const isCorrect = letter === q.correct_answer || (q.correct_answer_alt && q.correct_answer_alt.includes(letter));
      playSound(isCorrect ? 'correct' : 'wrong');

      const card = document.getElementById(`qcard_${qId}`);
      if (card) {
        card.querySelectorAll('.option-item').forEach(el => {
          el.classList.add('locked');
          const optL = el.dataset.letter;
          if (optL === q.correct_answer || (q.correct_answer_alt && q.correct_answer_alt.includes(optL))) {
            el.classList.add('correct');
          } else if (optL === letter) {
            el.classList.add('wrong');
          }
        });

        if (!isCorrect) {
          const expBox = document.getElementById(`exp_${qId}`);
          const toggleBtn = card.querySelector('.explanation-toggle-btn span');
          if (expBox) {
            expBox.style.display = 'block';
            if (toggleBtn) toggleBtn.textContent = 'ব্যাখ্যা লুকান';
            renderKaTeX();
          }
        }
      }
    } else {
      playSound('click');
      const card = document.getElementById(`qcard_${qId}`);
      if (card) {
        card.querySelectorAll('.option-item').forEach(el => {
          if (el.dataset.letter === letter) {
            el.classList.add('selected');
          } else {
            el.classList.remove('selected');
          }
        });
      }
      updateExamSidebar();
    }
  }

  function toggleBookmark(qId, btn) {
    if (state.bookmarks.has(qId)) {
      state.bookmarks.delete(qId);
    } else {
      state.bookmarks.add(qId);
      playSound('click');
    }
    localStorage.setItem('abm_bcs_bookmarks', JSON.stringify(Array.from(state.bookmarks)));
    const isBm = state.bookmarks.has(qId);
    btn.classList.toggle('bookmarked', isBm);
    btn.querySelector('i').className = isBm ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
  }

  function copyQuestion(qId, btn) {
    const q = state.allQuestions.find(item => item.id === qId);
    if (!q) return;

    let text = `প্রশ্ন ${q.id}: ${q.question_text}\n\n`;
    ['A', 'B', 'C', 'D'].forEach(l => {
      if (q.options[l]) text += `${l}. ${q.options[l]}\n`;
    });
    text += `\nসঠিক উত্তর: ${q.correct_answer}\n`;
    if (q.explanation_text) text += `ব্যাখ্যা: ${q.explanation_text}\n`;
    text += `\n— ABM BCS / উত্তরণ প্রশ্নব্যাংক`;

    navigator.clipboard.writeText(text).then(() => {
      const orig = btn.innerHTML;
      btn.innerHTML = `<i class="fa-solid fa-check" style="color:#10b981"></i>`;
      setTimeout(() => { btn.innerHTML = orig; }, 1500);
    });
  }

  // --- Sub-Mode (Study vs Exam within 50th BCS) ---
  function setExamSubMode(mode) {
    state.examMode = mode;
    const subStudy = document.getElementById('modalSubTabStudy');
    const subExam = document.getElementById('modalSubTabExam');
    const layout = document.getElementById('contentLayout');
    const sidebar = document.getElementById('examSidebar');
    const controls = document.getElementById('controlsBar');

    if (subStudy) subStudy.classList.toggle('active', mode === 'study');
    if (subExam) subExam.classList.toggle('active', mode === 'exam');

    if (mode === 'exam') {
      layout.style.gridTemplateColumns = '1fr 300px';
      sidebar.style.display = 'flex';
      sidebar.style.flexDirection = 'column';
      sidebar.style.gap = '0.75rem';
      controls.style.display = 'none';
      startExamTimer();
      renderExamPalette();
      renderQuestions();
    } else {
      layout.style.gridTemplateColumns = '1fr';
      sidebar.style.display = 'none';
      controls.style.display = 'flex';
      state.currentPage = 1;
      renderQuestions();
    }
  }

  function startExamTimer() {
    if (state.exam.timerId) return;
    state.exam.startTime = state.exam.startTime || Date.now();

    state.exam.timerId = setInterval(() => {
      if (!state.exam.isPaused && !state.exam.isSubmitted) {
        state.exam.remainingSeconds--;
        updateTimerDisplay();

        if (state.exam.remainingSeconds <= 0) {
          clearInterval(state.exam.timerId);
          state.exam.timerId = null;
          alert('পরীক্ষার সময় শেষ হয়েছে!');
          submitExam();
        }
      }
    }, 1000);
    updateTimerDisplay();
  }

  function updateTimerDisplay() {
    const s = Math.max(0, state.exam.remainingSeconds);
    const hrs = String(Math.floor(s / 3600)).padStart(2, '0');
    const mins = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const secs = String(s % 60).padStart(2, '0');
    document.getElementById('examTimerVal').textContent = `${hrs}:${mins}:${secs}`;
  }

  function renderExamPalette() {
    const grid = document.getElementById('paletteGrid');
    if (!grid) return;

    let gridHtml = '';
    for (let i = 1; i <= state.allQuestions.length; i++) {
      const isAns = !!state.userAnswers[i];
      gridHtml += `
        <button class="palette-btn ${isAns ? 'answered' : ''}" data-qid="${i}" id="pbtn_${i}">
          ${i}
        </button>
      `;
    }
    grid.innerHTML = gridHtml;

    grid.querySelectorAll('.palette-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const qid = btn.dataset.qid;
        const target = document.getElementById(`qcard_${qid}`);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          target.style.outline = '2px solid #e31c25';
          setTimeout(() => { target.style.outline = 'none'; }, 1500);
        }
      });
    });
  }

  function updateExamSidebar() {
    let answered = 0;
    state.allQuestions.forEach(q => {
      const isAns = !!state.userAnswers[q.id];
      if (isAns) answered++;
      const pbtn = document.getElementById(`pbtn_${q.id}`);
      if (pbtn) pbtn.classList.toggle('answered', isAns);
    });

    document.getElementById('answeredCount').textContent = answered;
    document.getElementById('unansweredCount').textContent = state.allQuestions.length - answered;
  }

  function submitExam() {
    if (state.exam.isSubmitted) return;

    const answered = Object.keys(state.userAnswers).length;
    const unanswered = state.allQuestions.length - answered;
    if (unanswered > 0) {
      const confirmSubmit = confirm(`আপনি ${answered} টি প্রশ্নের উত্তর দিয়েছেন। এখনও ${unanswered} টি প্রশ্ন বাকি রয়েছে।\n\nআপনি কি নিশ্চিত যে পরীক্ষা জমা দিতে চান?`);
      if (!confirmSubmit) return;
    }

    clearInterval(state.exam.timerId);
    state.exam.timerId = null;
    state.exam.isSubmitted = true;
    state.exam.endTime = Date.now();

    let correctCount = 0;
    let wrongCount = 0;
    let skippedCount = 0;

    const subjectStats = {};
    Object.values(state.subjects).forEach(s => {
      subjectStats[s.id] = { ...s, total: 0, correct: 0, wrong: 0, score: 0 };
    });

    state.allQuestions.forEach(q => {
      const subjId = q.canonical_subject;
      if (!subjectStats[subjId]) {
        subjectStats[subjId] = { name_bn: q.subject_info.name_bn, icon: q.subject_info.icon, total: 0, correct: 0, wrong: 0, score: 0 };
      }
      subjectStats[subjId].total++;

      const userAns = state.userAnswers[q.id];
      if (!userAns) {
        skippedCount++;
      } else if (userAns === q.correct_answer || (q.correct_answer_alt && q.correct_answer_alt.includes(userAns))) {
        correctCount++;
        subjectStats[subjId].correct++;
      } else {
        wrongCount++;
        subjectStats[subjId].wrong++;
      }
    });

    const negativePenalty = wrongCount * 0.50;
    const rawScore = correctCount - negativePenalty;
    const finalScore = Math.max(0, rawScore).toFixed(2);
    const totalAttempted = correctCount + wrongCount;
    const accuracy = totalAttempted > 0 ? ((correctCount / totalAttempted) * 100).toFixed(1) : 0;

    const spentSecs = Math.max(0, state.exam.totalSeconds - state.exam.remainingSeconds);
    const spentMins = Math.floor(spentSecs / 60);
    const spentRemSecs = spentSecs % 60;
    const timeSpentStr = `${String(spentMins).padStart(2, '0')}:${String(spentRemSecs).padStart(2, '0')}`;

    document.getElementById('resTotalScore').textContent = finalScore;
    document.getElementById('resCorrectCount').textContent = correctCount;
    document.getElementById('resWrongCount').textContent = wrongCount;
    document.getElementById('resSkippedCount').textContent = skippedCount;
    document.getElementById('resNegativeMarks').textContent = `-${negativePenalty.toFixed(2)}`;
    document.getElementById('resAccuracy').textContent = `${accuracy}%`;
    document.getElementById('resTimeTaken').textContent = timeSpentStr;

    let tableHtml = '';
    Object.values(subjectStats).forEach(s => {
      const subScore = (s.correct - (s.wrong * 0.50)).toFixed(2);
      tableHtml += `
        <tr>
          <td><strong>${s.icon || ''} ${s.name_bn}</strong></td>
          <td>${s.total}</td>
          <td style="color:#10b981; font-weight:700;">${s.correct}</td>
          <td style="color:#ef4444; font-weight:700;">${s.wrong}</td>
          <td><strong>${subScore}</strong></td>
        </tr>
      `;
    });
    document.getElementById('subjectPerfBody').innerHTML = tableHtml;

    if (rawScore >= 120) {
      document.getElementById('resultEmoji').textContent = '🏆';
      if (window.confetti) window.confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
    } else if (rawScore >= 90) {
      document.getElementById('resultEmoji').textContent = '🌟';
    } else {
      document.getElementById('resultEmoji').textContent = '📚';
    }

    document.getElementById('resultModal').classList.add('open');
  }

  function retakeExam() {
    state.exam.remainingSeconds = state.exam.totalSeconds;
    state.exam.isPaused = false;
    state.exam.isSubmitted = false;
    state.exam.startTime = null;
    state.exam.endTime = null;
    state.userAnswers = {};
    document.getElementById('resultModal').classList.remove('open');
    startExamTimer();
    renderExamPalette();
    renderQuestions();
  }

  // --- Render Cadre Stories Modal ---
  function initCadresModal() {
    const grid = document.getElementById('cadresGrid');
    if (!grid || !state.portalData.cadres) return;

    let html = '';
    state.portalData.cadres.forEach(cadre => {
      html += `
        <div class="cadre-card" style="border:1px solid var(--border-subtle); padding:1rem; border-radius:8px; background:var(--bg-surface);">
          <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
            <img src="${cadre.img}" alt="${cadre.name}" style="width:52px; height:52px; border-radius:50%; object-fit:cover; border:2px solid #e31c25;">
            <div>
              <h5 style="margin:0; font-size:1.05rem; font-weight:700;">${cadre.name}</h5>
              <span style="font-size:0.75rem; color:#e31c25; font-weight:700;">${cadre.cadre}</span>
              <div style="font-size:0.8rem; color:var(--text-muted);">${cadre.bcs}</div>
            </div>
          </div>
          <div style="font-size:0.88rem; color:var(--text-secondary); line-height:1.5; font-style:italic; background:var(--bg-surface-secondary); padding:0.65rem 0.85rem; border-radius:6px; border-left:3px solid #e31c25;">
            "${cadre.quote}"
          </div>
        </div>
      `;
    });
    grid.innerHTML = html;
  }

  // --- Render Syllabus Modal ---
  function initSyllabusModal() {
    const area = document.getElementById('syllabusContentArea');
    if (!area || !state.portalData.aboutBcs) return;

    let sHtml = `
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:1rem; margin-bottom:1.5rem;">
        ${state.portalData.aboutBcs.stages.map(st => `
          <div style="border:1px solid var(--border-subtle); border-radius:8px; padding:1rem; background:var(--bg-surface);">
            <h5 style="color:#e31c25; font-weight:700; margin-bottom:0.3rem;">${st.name}</h5>
            <div style="font-size:0.82rem; font-weight:700; color:var(--text-muted); margin-bottom:0.5rem;">পূর্ণমান: ${st.marks} | সময়: ${st.time}</div>
            <p style="font-size:0.88rem; color:var(--text-secondary); margin:0;">${st.desc}</p>
          </div>
        `).join('')}
      </div>
      <h4 style="font-size:1.1rem; margin-bottom:0.5rem;">প্রিলিমিনারি ২০০ নম্বরের বণ্টন:</h4>
      <div style="overflow-x:auto;">
        <table class="syllabus-table" style="width:100%; border-collapse:collapse; font-size:0.9rem;">
          <thead>
            <tr style="background:var(--bg-surface-secondary); text-align:left;">
              <th style="padding:8px 10px; border:1px solid var(--border-subtle);">বিষয়</th>
              <th style="padding:8px 10px; border:1px solid var(--border-subtle);">নম্বর</th>
              <th style="padding:8px 10px; border:1px solid var(--border-subtle);">সিলেবাস</th>
            </tr>
          </thead>
          <tbody>
            ${state.portalData.aboutBcs.preliSyllabus.map(ps => `
              <tr>
                <td style="padding:8px 10px; border:1px solid var(--border-subtle); font-weight:700;">${ps.subject}</td>
                <td style="padding:8px 10px; border:1px solid var(--border-subtle); font-weight:700; color:#e31c25;">${ps.marks}</td>
                <td style="padding:8px 10px; border:1px solid var(--border-subtle); color:var(--text-secondary);">${ps.breakdown}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
    area.innerHTML = sHtml;
  }

  // --- Setup Event Listeners ---
  function initEvents() {
    // Nav Links
    document.getElementById('navSuccess').onclick = () => {
      document.getElementById('cadresModal').classList.add('open');
    };
    document.getElementById('navAboutBcs').onclick = () => {
      document.getElementById('syllabusModal').classList.add('open');
    };
    document.getElementById('navCourses').onclick = () => {
      alert('আমাদের সকল কোর্স: ৫৩তম Pioneer Batch, ৫২তম Exclusive Exam Batch এবং Book Packages! বিস্তারিত জানতে কল করুন: ০৯৬৬৬৭৭৫৫২২');
    };
    document.getElementById('navNotice').onclick = () => {
      alert('সর্বশেষ নোটিশ: ৫১তম ও ৫২তম বিসিএস পরীক্ষার সময়সূচি ও রেজিস্ট্রেশন চলমান!');
    };
    document.getElementById('navMonthly').onclick = () => {
      alert('মাসিক কারেন্ট অ্যাফেয়ার্স ও সাম্প্রতিক সাধারণ জ্ঞান নিয়মিত আপডেট করা হচ্ছে।');
    };
    document.getElementById('navExamCenter').onclick = () => {
      alert('দেশব্যাপী উদ্ভাস-উন্মেষ ও উত্তরণের সকল শাখা ও এক্সাম সেন্টার তালিকা দেখুন: uttoron.academy/Branch');
    };

    // Close 50th BCS Modal
    document.getElementById('btnClose50thExam').onclick = close50thBcsExam;

    // Sub Tabs inside 50th BCS
    document.getElementById('modalSubTabStudy').onclick = () => setExamSubMode('study');
    document.getElementById('modalSubTabExam').onclick = () => setExamSubMode('exam');

    // Search Input
    const sInput = document.getElementById('searchInput');
    if (sInput) {
      sInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        state.currentPage = 1;
        renderQuestions();
      });
    }

    // Jump Input
    const jBtn = document.getElementById('jumpBtn');
    const jInput = document.getElementById('jumpInput');
    if (jBtn && jInput) {
      const doJump = () => {
        const num = parseInt(jInput.value, 10);
        if (num >= 1 && num <= state.allQuestions.length) {
          if (state.examMode === 'exam') {
            const card = document.getElementById(`qcard_${num}`);
            if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } else {
            state.activeSubject = 'ALL';
            state.searchQuery = '';
            if (sInput) sInput.value = '';
            renderSubjectPills();
            state.currentPage = Math.ceil(num / state.pageSize);
            renderQuestions();
            setTimeout(() => {
              const card = document.getElementById(`qcard_${num}`);
              if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                card.style.outline = '2px solid #e31c25';
                setTimeout(() => { card.style.outline = 'none'; }, 2000);
              }
            }, 100);
          }
        }
      };
      jBtn.onclick = doJump;
      jInput.onkeypress = (e) => { if (e.key === 'Enter') doJump(); };
    }

    // Reset
    const rBtn = document.getElementById('resetAnswersBtn');
    if (rBtn) {
      rBtn.onclick = () => {
        if (confirm('সব উত্তর রিসেট করতে চান?')) {
          state.userAnswers = {};
          renderQuestions();
        }
      };
    }

    // Pagination
    document.getElementById('prevPageBtn').onclick = () => {
      if (state.currentPage > 1) {
        state.currentPage--;
        renderQuestions();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };
    document.getElementById('nextPageBtn').onclick = () => {
      state.currentPage++;
      renderQuestions();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Theme Toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      themeBtn.onclick = () => {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', state.theme);
        localStorage.setItem('abm_bcs_theme', state.theme);
        themeBtn.innerHTML = state.theme === 'dark' ? `<i class="fa-solid fa-sun" style="color:#f59e0b;"></i>` : `<i class="fa-solid fa-moon"></i>`;
      };
      if (state.theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeBtn.innerHTML = `<i class="fa-solid fa-sun" style="color:#f59e0b;"></i>`;
      }
    }

    // Sound Toggle
    const soundBtn = document.getElementById('soundToggleBtn');
    if (soundBtn) {
      soundBtn.onclick = () => {
        state.soundEnabled = !state.soundEnabled;
        localStorage.setItem('abm_bcs_sound', state.soundEnabled);
        soundBtn.innerHTML = state.soundEnabled ? `<i class="fa-solid fa-volume-high"></i>` : `<i class="fa-solid fa-volume-xmark" style="color:#ef4444;"></i>`;
        if (state.soundEnabled) playSound('click');
      };
    }

    // Exam Sidebar Controls
    document.getElementById('pauseTimerBtn').onclick = () => {
      state.exam.isPaused = !state.exam.isPaused;
      document.getElementById('pauseTimerBtn').innerHTML = state.exam.isPaused ? `<i class="fa-solid fa-play"></i>` : `<i class="fa-solid fa-pause"></i>`;
    };

    document.getElementById('examSubmitBtn').onclick = submitExam;

    document.getElementById('modalReviewBtn').onclick = () => {
      document.getElementById('resultModal').classList.remove('open');
      renderQuestions();
    };

    document.getElementById('modalRetakeBtn').onclick = retakeExam;

    // Logo Click -> Close any open modal
    document.getElementById('navHomeLogo').onclick = () => {
      close50thBcsExam();
      document.getElementById('cadresModal').classList.remove('open');
      document.getElementById('syllabusModal').classList.remove('open');
    };
  }

  // --- Init ---
  function init() {
    initQuestionBankCards();
    initCadresModal();
    initSyllabusModal();
    initEvents();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
