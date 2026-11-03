/**
 * Educational & IQ Games Engine
 * Implements 6 fully working interactive games with instructions,
 * score calculation, feedback, restart, and database persistence.
 */

// -------------------------------------------------------------
// GAME 1: BIOLOGY DIAGRAM LABELING (HUMAN HEART & ORGANS)
// -------------------------------------------------------------
const BIOLOGY_DATA = [
  { id: "left_atrium", label: "Left Atrium", desc: "Receives oxygenated blood from pulmonary veins" },
  { id: "right_atrium", label: "Right Atrium", desc: "Receives deoxygenated blood from vena cava" },
  { id: "left_ventricle", label: "Left Ventricle", desc: "Pumps oxygen-rich blood into the aorta" },
  { id: "right_ventricle", label: "Right Ventricle", desc: "Pumps deoxygenated blood to pulmonary arteries" },
  { id: "aorta", label: "Aorta", desc: "Main artery carrying blood to systemic circulation" }
];

let bioState = { score: 0, currentIdx: 0, maxScore: 50 };

function initBiologyGame() {
  bioState = { score: 0, currentIdx: 0, maxScore: BIOLOGY_DATA.length * 10 };
  document.getElementById('bioScore').textContent = '0';
  document.getElementById('bioFeedback').innerHTML = '';
  document.getElementById('bioNextBtn').classList.add('d-none');
  renderBioStep();
}

function renderBioStep() {
  const container = document.getElementById('bioQuestionArea');
  if (!container) return;

  if (bioState.currentIdx >= BIOLOGY_DATA.length) {
    finishGame('Biology Diagram & Function Challenge', 'Biology', bioState.score, bioState.maxScore);
    return;
  }

  const currentItem = BIOLOGY_DATA[bioState.currentIdx];
  // Shuffle options
  const shuffled = [...BIOLOGY_DATA].sort(() => Math.random() - 0.5);

  container.innerHTML = `
    <div class="mb-3 text-center">
      <div class="stat-icon bg-danger-subtle text-danger mx-auto mb-2" style="width: 50px; height: 50px;">
        <i class="fa-solid fa-heart-pulse fs-3"></i>
      </div>
      <h5 class="fw-bold text-dark mb-1">Target Function:</h5>
      <p class="lead text-primary fw-medium mb-0">"${currentItem.desc}"</p>
    </div>
    <div class="row g-2">
      ${shuffled.map(item => `
        <div class="col-md-6">
          <button class="btn btn-outline-secondary w-100 py-3 rounded-3 text-start fw-bold d-flex justify-content-between align-items-center"
                  onclick="checkBioAnswer('${item.id}', '${currentItem.id}', this)">
            <span>${item.label}</span>
            <i class="fa-regular fa-circle-check opacity-50"></i>
          </button>
        </div>
      `).join('')}
    </div>
  `;
}

function checkBioAnswer(selectedId, correctId, btnEl) {
  const allBtns = document.querySelectorAll('#bioQuestionArea button');
  allBtns.forEach(b => b.disabled = true);

  const fbBox = document.getElementById('bioFeedback');

  if (selectedId === correctId) {
    bioState.score += 10;
    btnEl.className = 'btn btn-success w-100 py-3 rounded-3 text-start fw-bold text-white';
    fbBox.innerHTML = `<div class="alert alert-success mt-3 py-2 fw-semibold"><i class="fa-solid fa-check-circle me-1"></i> Correct! +10 Points</div>`;
  } else {
    btnEl.className = 'btn btn-danger w-100 py-3 rounded-3 text-start fw-bold text-white';
    fbBox.innerHTML = `<div class="alert alert-danger mt-3 py-2 fw-semibold"><i class="fa-solid fa-circle-xmark me-1"></i> Incorrect! That organ does not match the description.</div>`;
  }

  document.getElementById('bioScore').textContent = bioState.score;
  const nextBtn = document.getElementById('bioNextBtn');
  nextBtn.classList.remove('d-none');
  nextBtn.onclick = () => {
    bioState.currentIdx++;
    fbBox.innerHTML = '';
    nextBtn.classList.add('d-none');
    renderBioStep();
  };
}

// -------------------------------------------------------------
// GAME 2: MATHEMATICS SEQUENCE & MISSING NUMBER PUZZLE
// -------------------------------------------------------------
const MATH_PUZZLES = [
  { seq: "2, 3, 5, 7, 11, ?", ans: 13, options: [12, 13, 15, 17], rule: "Prime Number Sequence" },
  { seq: "1, 1, 2, 3, 5, 8, ?", ans: 13, options: [11, 12, 13, 15], rule: "Fibonacci Sequence (sum of preceding two)" },
  { seq: "3, 9, 27, 81, ?", ans: 243, options: [162, 214, 243, 300], rule: "Geometric Progression (multiply by 3)" },
  { seq: "4, 9, 16, 25, 36, ?", ans: 49, options: [45, 48, 49, 52], rule: "Consecutive Squares (2², 3², 4², 5², 6², 7²)" },
  { seq: "100, 93, 86, 79, ?", ans: 72, options: [70, 71, 72, 74], rule: "Arithmetic Progression (subtract 7)" }
];

let mathState = { score: 0, currentIdx: 0, maxScore: 50 };

function initMathGame() {
  mathState = { score: 0, currentIdx: 0, maxScore: MATH_PUZZLES.length * 10 };
  document.getElementById('mathScore').textContent = '0';
  document.getElementById('mathFeedback').innerHTML = '';
  document.getElementById('mathNextBtn').classList.add('d-none');
  renderMathStep();
}

function renderMathStep() {
  const container = document.getElementById('mathQuestionArea');
  if (!container) return;

  if (mathState.currentIdx >= MATH_PUZZLES.length) {
    finishGame('Mathematics Sequence Puzzle', 'Mathematics', mathState.score, mathState.maxScore);
    return;
  }

  const puzzle = MATH_PUZZLES[mathState.currentIdx];
  container.innerHTML = `
    <div class="text-center mb-4">
      <span class="badge bg-primary-subtle text-primary px-3 py-1 rounded-pill mb-2">Puzzle ${mathState.currentIdx + 1} of ${MATH_PUZZLES.length}</span>
      <h3 class="display-6 fw-bold font-monospace text-dark">${puzzle.seq}</h3>
      <p class="text-muted small">Find the missing pattern rule and choose the correct number.</p>
    </div>
    <div class="row g-3 justify-content-center">
      ${puzzle.options.map(opt => `
        <div class="col-6 col-md-3">
          <button class="btn btn-outline-primary w-100 py-3 fs-5 fw-bold rounded-4 shadow-sm"
                  onclick="checkMathAnswer(${opt}, ${puzzle.ans}, '${puzzle.rule}', this)">
            ${opt}
          </button>
        </div>
      `).join('')}
    </div>
  `;
}

function checkMathAnswer(selected, correct, rule, btnEl) {
  const allBtns = document.querySelectorAll('#mathQuestionArea button');
  allBtns.forEach(b => b.disabled = true);

  const fbBox = document.getElementById('mathFeedback');

  if (selected === correct) {
    mathState.score += 10;
    btnEl.className = 'btn btn-success w-100 py-3 fs-5 fw-bold rounded-4 text-white';
    fbBox.innerHTML = `<div class="alert alert-success mt-3 py-2 fw-semibold">🟢 Correct! Pattern: ${rule} (+10 Points)</div>`;
  } else {
    btnEl.className = 'btn btn-danger w-100 py-3 fs-5 fw-bold rounded-4 text-white';
    fbBox.innerHTML = `<div class="alert alert-danger mt-3 py-2 fw-semibold">🔴 Incorrect! The correct answer was ${correct}. (${rule})</div>`;
  }

  document.getElementById('mathScore').textContent = mathState.score;
  const nextBtn = document.getElementById('mathNextBtn');
  nextBtn.classList.remove('d-none');
  nextBtn.onclick = () => {
    mathState.currentIdx++;
    fbBox.innerHTML = '';
    nextBtn.classList.add('d-none');
    renderMathStep();
  };
}

// -------------------------------------------------------------
// GAME 3: HISTORY CHRONOLOGICAL ORDER CHALLENGE
// -------------------------------------------------------------
const HISTORY_EVENTS = [
  { event: "Indus Valley Civilization (Mohenjo-daro)", year: "2500 BCE", order: 1 },
  { event: "Battle of Panipat (First)", year: "1526 CE", order: 2 },
  { event: "Storming of the Bastille (French Revolution)", year: "1789 CE", order: 3 },
  { event: "Dandi Salt March (Mahatma Gandhi)", year: "1930 CE", order: 4 },
  { event: "Indian Independence Day", year: "1947 CE", order: 5 }
];

let histOrder = [];

function initHistoryGame() {
  histOrder = [];
  document.getElementById('historyScore').textContent = '0';
  document.getElementById('historyFeedback').innerHTML = '';
  renderHistoryGame();
}

function renderHistoryGame() {
  const pool = document.getElementById('historyPool');
  const target = document.getElementById('historyTarget');
  if (!pool || !target) return;

  target.innerHTML = '<span class="text-muted small fst-italic">Click historical events from below in chronological order (Oldest to Most Recent):</span>';

  // Randomize pool
  const shuffled = [...HISTORY_EVENTS].sort(() => Math.random() - 0.5);
  pool.innerHTML = '';

  shuffled.forEach(ev => {
    const card = document.createElement('button');
    card.className = 'btn btn-outline-dark m-1 py-2 px-3 rounded-pill text-start small fw-semibold';
    card.id = `hist-item-${ev.order}`;
    card.textContent = ev.event;
    card.onclick = () => addToChronology(ev, card);
    pool.appendChild(card);
  });
}

function addToChronology(eventObj, btnEl) {
  histOrder.push(eventObj);
  btnEl.disabled = true;
  btnEl.classList.add('opacity-25');

  const target = document.getElementById('historyTarget');
  if (histOrder.length === 1) target.innerHTML = '';

  const tag = document.createElement('div');
  tag.className = 'd-flex align-items-center gap-2 p-2 mb-2 bg-white rounded-3 border shadow-sm';
  tag.innerHTML = `
    <span class="badge bg-secondary rounded-circle" style="width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center;">${histOrder.length}</span>
    <strong class="text-dark small">${eventObj.event}</strong>
    <span class="badge bg-light text-muted ms-auto">${eventObj.year}</span>
  `;
  target.appendChild(tag);

  if (histOrder.length === HISTORY_EVENTS.length) {
    evaluateHistoryOrder();
  }
}

function evaluateHistoryOrder() {
  let isPerfect = true;
  for (let i = 0; i < histOrder.length; i++) {
    if (histOrder[i].order !== i + 1) {
      isPerfect = false;
      break;
    }
  }

  const fb = document.getElementById('historyFeedback');
  const score = isPerfect ? 50 : 20;

  if (isPerfect) {
    fb.innerHTML = `<div class="alert alert-success fw-bold">🟢 Brilliant! Perfect Chronological Sequence (+50 Points)</div>`;
  } else {
    fb.innerHTML = `<div class="alert alert-warning fw-bold">🟡 Good try! Some events were slightly out of historical order (+20 Points)</div>`;
  }

  document.getElementById('historyScore').textContent = score;
  finishGame('History Chronology Challenge', 'History', score, 50);
}

// -------------------------------------------------------------
// GAME 4: GEOGRAPHY COUNTRY & CAPITAL PAIR MATCHING
// -------------------------------------------------------------
const GEO_PAIRS = [
  { country: "Japan", capital: "Tokyo" },
  { country: "France", capital: "Paris" },
  { country: "Australia", capital: "Canberra" },
  { country: "India", capital: "New Delhi" },
  { country: "Egypt", capital: "Cairo" }
];

let geoSelected = null;
let geoMatches = 0;
let geoScore = 0;

function initGeoGame() {
  geoSelected = null;
  geoMatches = 0;
  geoScore = 0;
  document.getElementById('geoScore').textContent = '0';
  document.getElementById('geoFeedback').innerHTML = '';

  const countriesCol = document.getElementById('geoCountries');
  const capitalsCol = document.getElementById('geoCapitals');
  if (!countriesCol || !capitalsCol) return;

  countriesCol.innerHTML = '';
  capitalsCol.innerHTML = '';

  const shuffledCountries = [...GEO_PAIRS].sort(() => Math.random() - 0.5);
  const shuffledCapitals = [...GEO_PAIRS].sort(() => Math.random() - 0.5);

  shuffledCountries.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline-primary w-100 py-2 mb-2 rounded-3 text-start fw-bold geo-country-btn';
    btn.textContent = p.country;
    btn.onclick = () => selectGeoCountry(p, btn);
    countriesCol.appendChild(btn);
  });

  shuffledCapitals.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline-info text-dark w-100 py-2 mb-2 rounded-3 text-start fw-bold geo-capital-btn';
    btn.textContent = p.capital;
    btn.onclick = () => selectGeoCapital(p, btn);
    capitalsCol.appendChild(btn);
  });
}

function selectGeoCountry(pair, btn) {
  document.querySelectorAll('.geo-country-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  geoSelected = { pair: pair, btn: btn };
}

function selectGeoCapital(pair, btn) {
  if (!geoSelected) {
    alert("Please select a Country first!");
    return;
  }

  const fb = document.getElementById('geoFeedback');

  if (geoSelected.pair.capital === pair.capital) {
    // Match!
    geoScore += 10;
    geoMatches++;
    geoSelected.btn.className = 'btn btn-success w-100 py-2 mb-2 rounded-3 text-start fw-bold text-white';
    geoSelected.btn.disabled = true;
    btn.className = 'btn btn-success w-100 py-2 mb-2 rounded-3 text-start fw-bold text-white';
    btn.disabled = true;
    fb.innerHTML = `<div class="alert alert-success py-1 small">🟢 Correct Match: ${pair.country} → ${pair.capital}</div>`;
  } else {
    fb.innerHTML = `<div class="alert alert-danger py-1 small">🔴 Mismatch! Try again.</div>`;
    geoSelected.btn.classList.remove('active');
  }

  geoSelected = null;
  document.getElementById('geoScore').textContent = geoScore;

  if (geoMatches === GEO_PAIRS.length) {
    finishGame('Geography Capital Matching', 'Geography', geoScore, 50);
  }
}

// -------------------------------------------------------------
// GAME 5: GK & LOGIC ODD-ONE-OUT CHALLENGE
// -------------------------------------------------------------
const ODD_ITEMS = [
  { group: ["Mercury", "Venus", "Moon", "Mars"], odd: "Moon", reason: "Moon is a natural satellite, whereas Mercury, Venus, and Mars are planets." },
  { group: ["Oxygen", "Nitrogen", "Iron", "Argon"], odd: "Iron", reason: "Iron is a metallic solid at room temperature, while the others are atmospheric gases." },
  { group: ["Square", "Rectangle", "Rhombus", "Triangle"], odd: "Triangle", reason: "Triangle has 3 sides (trilateral); the others are 4-sided quadrilaterals." },
  { group: ["Tiger", "Lion", "Leopard", "Kangaroo"], odd: "Kangaroo", reason: "Kangaroo is a marsupial native to Australia, while the others are big felid carnivores." }
];

let oddState = { score: 0, currentIdx: 0, maxScore: 40 };

function initOddGame() {
  oddState = { score: 0, currentIdx: 0, maxScore: ODD_ITEMS.length * 10 };
  document.getElementById('oddScore').textContent = '0';
  document.getElementById('oddFeedback').innerHTML = '';
  document.getElementById('oddNextBtn').classList.add('d-none');
  renderOddStep();
}

function renderOddStep() {
  const container = document.getElementById('oddQuestionArea');
  if (!container) return;

  if (oddState.currentIdx >= ODD_ITEMS.length) {
    finishGame('Logical Odd-One-Out Challenge', 'General Knowledge', oddState.score, oddState.maxScore);
    return;
  }

  const item = ODD_ITEMS[oddState.currentIdx];
  container.innerHTML = `
    <div class="text-center mb-3">
      <span class="badge bg-warning-subtle text-dark px-3 py-1 rounded-pill mb-2">Round ${oddState.currentIdx + 1} of ${ODD_ITEMS.length}</span>
      <h5 class="fw-bold text-dark">Spot the Odd Item Out:</h5>
    </div>
    <div class="row g-2 justify-content-center">
      ${item.group.map(word => `
        <div class="col-6">
          <button class="btn btn-outline-dark w-100 py-3 fw-bold rounded-3 shadow-sm"
                  onclick="checkOddAnswer('${word}', '${item.odd}', '${item.reason}', this)">
            ${word}
          </button>
        </div>
      `).join('')}
    </div>
  `;
}

function checkOddAnswer(selected, correct, reason, btnEl) {
  const allBtns = document.querySelectorAll('#oddQuestionArea button');
  allBtns.forEach(b => b.disabled = true);

  const fbBox = document.getElementById('oddFeedback');

  if (selected === correct) {
    oddState.score += 10;
    btnEl.className = 'btn btn-success w-100 py-3 fw-bold rounded-3 text-white';
    fbBox.innerHTML = `<div class="alert alert-success mt-3 py-2 fw-semibold">🟢 Correct! Reason: ${reason}</div>`;
  } else {
    btnEl.className = 'btn btn-danger w-100 py-3 fw-bold rounded-3 text-white';
    fbBox.innerHTML = `<div class="alert alert-danger mt-3 py-2 fw-semibold">🔴 Incorrect! Odd item: ${correct}. (${reason})</div>`;
  }

  document.getElementById('oddScore').textContent = oddState.score;
  const nextBtn = document.getElementById('oddNextBtn');
  nextBtn.classList.remove('d-none');
  nextBtn.onclick = () => {
    oddState.currentIdx++;
    fbBox.innerHTML = '';
    nextBtn.classList.add('d-none');
    renderOddStep();
  };
}

// -------------------------------------------------------------
// FINISH GAME & DATABASE RECORDING
// -------------------------------------------------------------
async function finishGame(gameType, subject, score, maxScore) {
  const pct = Math.round((score / maxScore) * 100);

  // Send to backend
  try {
    await fetch('/api/save-game-score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: 'highschool',
        game_type: gameType,
        subject: subject,
        score: score,
        max_score: maxScore
      })
    });
  } catch (e) {
    console.error("Game score sync error:", e);
  }

  // Display modal
  const modalEl = document.getElementById('gameResultModal');
  if (modalEl) {
    document.getElementById('modalGameTitle').textContent = gameType;
    document.getElementById('modalGameScore').textContent = `${score}/${maxScore}`;
    document.getElementById('modalGamePct').textContent = `${pct}%`;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}
