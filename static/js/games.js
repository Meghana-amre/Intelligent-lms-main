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
  { id: "aorta", label: "Aorta", desc: "Main artery carrying blood to systemic circulation" },
  { id: "alveoli", label: "Alveoli", desc: "Tiny air sacs where oxygen and carbon dioxide are exchanged" },
  { id: "nephron", label: "Nephron", desc: "Functional unit that filters blood in the kidney" },
  { id: "pancreas", label: "Pancreas", desc: "Produces insulin and digestive enzymes" },
  { id: "small_intestine", label: "Small Intestine", desc: "Absorbs most digested nutrients into the bloodstream" },
  { id: "cerebellum", label: "Cerebellum", desc: "Coordinates balance and fine muscular movement" },
  { id: "thyroid", label: "Thyroid Gland", desc: "Regulates metabolism through thyroid hormones" },
  { id: "platelets", label: "Platelets", desc: "Help form clots and stop bleeding" }
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
// BIOLOGY IMAGE PAIR MATCHING (MBBS MEDICAL SPECIMENS)
// -------------------------------------------------------------
const MBBS_SPECIMENS_DATABASE = {
  heart: {
    id: 'heart',
    image: '/static/images/mbbs/heart.svg',
    label: 'Heart: 4-Chamber Internal Anatomy & Conduction',
    shortLabel: 'Heart (4-Chamber)',
    discipline: 'Cardiovascular Anatomy',
    mag: 'Gross Coronal Section',
    structures: 'Left Ventricular Myocardium, Interventricular Septum, Tricuspid & Mitral Valves, Aorta, SA & AV Nodes',
    clinicalNote: 'Muscular interventricular septum separates systemic LV from pulmonary RV. SA node (Keith-Flack) coordinates atrial syncytial depolarization.'
  },
  brain: {
    id: 'brain',
    image: '/static/images/mbbs/brain.svg',
    label: 'Brain: Cerebral Cortex & Brainstem Topography',
    shortLabel: 'Brain (Cerebral Cortex)',
    discipline: 'Neuroanatomy',
    mag: 'Medial Sagittal Hemisection',
    structures: 'Frontal/Parietal/Occipital/Temporal Lobes, Central Sulcus, Corpus Callosum, Thalamus, Pons, Cerebellar Arbor Vitae',
    clinicalNote: 'Central sulcus separates Brodmann Area 4 (precentral primary motor) from Brodmann 3,1,2 (postcentral primary somatosensory cortex).'
  },
  lungs: {
    id: 'lungs',
    image: '/static/images/mbbs/lungs.svg',
    label: 'Lungs & Alveolar Gas Exchange Barrier',
    shortLabel: 'Lungs & Alveoli',
    discipline: 'Pulmonary Histology',
    mag: 'Bronchial Tree + Alveolar High-Power (400x)',
    structures: 'Trachea, Carina, Right (3 lobes) / Left (2 lobes), Type I & II Pneumocytes, Capillary diffusion barrier',
    clinicalNote: 'Type II pneumocytes produce surfactant (dipalmitoylphosphatidylcholine - DPPC), reducing alveolar surface tension and preventing atelectasis.'
  },
  bone: {
    id: 'bone',
    image: '/static/images/mbbs/bone.svg',
    label: 'Bone: Haversian System (Osteon)',
    shortLabel: 'Bone (Osteon System)',
    discipline: 'Osteology & Histology',
    mag: 'Ground Bone Section (400x)',
    structures: 'Central Haversian Canal (neurovascular bundle), Concentric Lamellae, Osteocytes in Lacunae, Radiating Canaliculi',
    clinicalNote: 'Volkmann canals connect adjacent Haversian systems. Bone remodeling involves osteoclast resorption in Howship lacunae followed by osteoblast osteoid deposition.'
  },
  cell: {
    id: 'cell',
    image: '/static/images/mbbs/cell.svg',
    label: 'Cell Ultrastructure & Organelles',
    shortLabel: 'Cell (TEM Organelles)',
    discipline: 'Medical Cytology & Cell Biology',
    mag: 'Transmission Electron Microscopy (TEM)',
    structures: 'Double-membrane Nucleus with Pores, Nucleolus, Rough ER with Ribosomes, Smooth ER, Golgi Cisternae, Mitochondria Cristae, Lysosomes',
    clinicalNote: 'Rough ER synthesizes secretory proteins; Smooth ER handles steroidogenesis and hepatic cytochrome P450 drug detoxification; Mitochondria drive ATP oxidative phosphorylation.'
  },
  dna: {
    id: 'dna',
    image: '/static/images/mbbs/dna.svg',
    label: 'B-DNA Double Helix & Molecular Genetics',
    shortLabel: 'DNA Double Helix',
    discipline: 'Medical Biochemistry',
    mag: 'Watson-Crick B-DNA Model (34 Å Pitch)',
    structures: 'Antiparallel Deoxyribose Backbone, Major Groove (22 Å), Minor Groove (12 Å), A=T (2 H-bonds), G≡C (3 H-bonds), Histone Octamer',
    clinicalNote: 'Topoisomerase inhibitors (e.g. fluoroquinolones, etoposide) cause lethal DNA double-strand breaks during replication and transcription.'
  },
  renal_glomerulus: {
    id: 'renal_glomerulus',
    image: '/static/images/mbbs/renal_glomerulus.svg',
    label: 'Renal Glomerulus & Podocyte Barrier',
    shortLabel: 'Renal Glomerulus',
    discipline: 'Renal Histology (H&E)',
    mag: 'Light Microscopy (H&E Stain 400x)',
    structures: 'Bowman\'s Capsule, Fenestrated Capillary Loops, Podocyte Pedicels, Mesangium, Macula Densa',
    clinicalNote: 'Podocyte effacement causes Minimal Change Nephrotic Syndrome with massive proteinuria. Mesangial expansion and Kimmelstiel-Wilson nodules characterize diabetic nephropathy.'
  },
  purkinje_cells: {
    id: 'purkinje_cells',
    image: '/static/images/mbbs/purkinje_cells.svg',
    label: 'Cerebellar Purkinje Neurons & Cortical Layers',
    shortLabel: 'Purkinje Neurons',
    discipline: 'Neurohistology',
    mag: 'Cerebellar Cortex Folium (200x)',
    structures: 'Molecular Layer, Flask-shaped Purkinje Cell Somas, Dendritic Fan Arborization, Granule Cell Layer, Axons',
    clinicalNote: 'Purkinje cells represent the sole inhibitory (GABAergic) output from the cerebellar cortex, projecting to the deep cerebellar nuclei (Dentate, Emboliform, Globose, Fastigial).'
  },
  hepatic_triad: {
    id: 'hepatic_triad',
    image: '/static/images/mbbs/hepatic_triad.svg',
    label: 'Hepatic Lobule & Portal Triad',
    shortLabel: 'Hepatic Portal Triad',
    discipline: 'Gastrointestinal Histology',
    mag: 'Liver Parenchyma (H&E 200x)',
    structures: 'Portal Venule Branch, Hepatic Arteriole Branch, Interlobular Bile Ductule, Hepatocyte Cords, Sinusoids, Central Vein',
    clinicalNote: 'Blood flows from portal triad inward to central vein; bile flows outward to bile ductule. Zone 3 (centrilobular) is most vulnerable to ischemia and toxic damage.'
  },
  cardiac_intercalated_discs: {
    id: 'cardiac_intercalated_discs',
    image: '/static/images/mbbs/cardiac_intercalated_discs.svg',
    label: 'Cardiac Muscle & Intercalated Discs',
    shortLabel: 'Cardiac Intercalated Discs',
    discipline: 'Cardiovascular Histology',
    mag: 'Striated Cardiomyocytes (400x)',
    structures: 'Branching Cardiomyocytes, Central Vesicular Nuclei, Cross-Striations, Step-like Intercalated Discs, Gap Junctions',
    clinicalNote: 'Intercalated discs contain Fascia Adherens (anchor actin), Desmosomes (prevent separation during contraction), and Gap Junctions (low electrical resistance for syncytium).'
  },
  circle_of_willis: {
    id: 'circle_of_willis',
    image: '/static/images/mbbs/circle_of_willis.svg',
    label: 'Circle of Willis Cerebral Arterial Circle',
    shortLabel: 'Circle of Willis',
    discipline: 'Neurovascular Anatomy',
    mag: 'Base of Brain Angiography',
    structures: 'Anterior Communicating (ACom), Anterior Cerebral (ACA), Internal Carotid (ICA), Posterior Communicating (PCom), Posterior Cerebral (PCA), Basilar Artery',
    clinicalNote: 'ACom junction is the most frequent site of congenital saccular (berry) aneurysms; rupture causes sudden severe thunderclap headache (subarachnoid hemorrhage).'
  },
  neutrophil_granulocyte: {
    id: 'neutrophil_granulocyte',
    image: '/static/images/mbbs/neutrophil_granulocyte.svg',
    label: 'Neutrophil Granulocyte (PMN Blood Film)',
    shortLabel: 'Neutrophil PMN',
    discipline: 'Hematology & Pathology',
    mag: 'Leishman Stain (1000x Oil Immersion)',
    structures: '3-5 Lobed Connected Nucleus, Fine Lilac Specific Granules, Barr Body / Drumstick, Surrounding Biconcave Normocytes & Platelets',
    clinicalNote: 'Neutrophilia with toxic granulation and band forms indicates acute bacterial infection. Hypersegmented neutrophils (>5 lobes) are diagnostic of Vitamin B12/Folate deficiency.'
  }
};

const MBBS_DECKS = {
  core: ['brain', 'cell', 'dna', 'lungs', 'heart', 'bone'],
  histology: ['renal_glomerulus', 'purkinje_cells', 'hepatic_triad', 'cardiac_intercalated_discs', 'circle_of_willis', 'neutrophil_granulocyte'],
  comprehensive: ['brain', 'cell', 'dna', 'lungs', 'heart', 'bone', 'renal_glomerulus', 'purkinje_cells', 'hepatic_triad', 'cardiac_intercalated_discs', 'circle_of_willis', 'neutrophil_granulocyte']
};

let currentMbbsDeck = 'core';
let BIOLOGY_IMAGE_PAIRS = MBBS_DECKS.core.map(id => MBBS_SPECIMENS_DATABASE[id]);

let bioMatchState = { cards: [], first: null, locked: false, matches: 0, attempts: 0 };

function setMbbsDeck(deckKey) {
  if (!MBBS_DECKS[deckKey]) return;
  currentMbbsDeck = deckKey;

  const btnGroup = document.getElementById('mbbsDeckSelector');
  if (btnGroup) {
    btnGroup.querySelectorAll('button').forEach(btn => {
      btn.classList.remove('btn-danger', 'active');
      btn.classList.add('btn-outline-danger');
    });
    const clickedBtn = btnGroup.querySelector(`button[onclick*="'${deckKey}'"]`);
    if (clickedBtn) {
      clickedBtn.classList.remove('btn-outline-danger');
      clickedBtn.classList.add('btn-danger', 'active');
    }
  }

  if (deckKey === 'comprehensive') {
    const shuffled = [...MBBS_DECKS.comprehensive].sort(() => Math.random() - 0.5).slice(0, 8);
    BIOLOGY_IMAGE_PAIRS = shuffled.map(id => MBBS_SPECIMENS_DATABASE[id]);
  } else {
    BIOLOGY_IMAGE_PAIRS = MBBS_DECKS[deckKey].map(id => MBBS_SPECIMENS_DATABASE[id]);
  }

  initBiologyMatchGame();
}

function initBiologyMatchGame() {
  const board = document.getElementById('bioMatchBoard');
  if (!board) return;
  const cards = BIOLOGY_IMAGE_PAIRS.flatMap(pair => [
    { ...pair, cardId: `${pair.id}-1` },
    { ...pair, cardId: `${pair.id}-2` }
  ]).sort(() => Math.random() - 0.5);
  bioMatchState = { cards, first: null, locked: false, matches: 0, attempts: 0 };
  document.getElementById('bioMatchScore').textContent = '0';
  document.getElementById('bioMatchFeedback').innerHTML = '';
  board.innerHTML = cards.map(card => `
    <div class="col">
      <button class="bio-match-card btn btn-outline-danger w-100 p-2 shadow-sm rounded-4 position-relative" data-card-id="${card.cardId}" onclick="selectBiologyMatchCard('${card.cardId}')" aria-label="Hidden medical card" style="transition: all 0.25s ease; min-height: 185px;">
        <span class="bio-match-front d-flex flex-column align-items-center justify-content-center rounded-3 bg-white border border-danger-subtle p-3" style="min-height: 165px;">
          <div class="stat-icon bg-danger-subtle text-danger mx-auto mb-2" style="width: 44px; height: 44px; border-radius: 50%;">
            <i class="fa-solid fa-microscope fs-4"></i>
          </div>
          <span class="badge bg-danger-subtle text-danger border border-danger-subtle rounded-pill px-2 py-0 mb-1" style="font-size: 0.65rem;">MBBS SPECIMEN</span>
          <small class="text-muted fw-bold" style="font-size: 0.72rem;">TAP TO FLIP</small>
        </span>
        <span class="bio-match-face d-none flex-column align-items-center justify-content-center rounded-3 bg-white border border-danger p-2 shadow-sm" style="min-height: 165px;">
          <span class="badge bg-danger text-white rounded-pill px-2 py-0 mb-1 text-truncate" style="font-size: 0.62rem; max-width: 100%;">${card.discipline || 'MBBS Medical'}</span>
          <img src="${card.image}" alt="${card.label}" class="img-fluid rounded-3 border mb-1" style="width: 100%; height: 95px; object-fit: contain; background: #fafafa; padding: 2px;" />
          <span class="fw-bold text-dark text-truncate d-block text-center" style="font-size: 0.78rem; width: 100%;" title="${card.label}">${card.shortLabel || card.label}</span>
          <small class="text-muted text-truncate d-block" style="font-size: 0.65rem;">${card.mag || 'Medical Visual'}</small>
        </span>
      </button>
    </div>
  `).join('');
}

function selectBiologyMatchCard(cardId) {
  if (bioMatchState.locked || bioMatchState.first === cardId) return;
  const card = bioMatchState.cards.find(item => item.cardId === cardId);
  const button = document.querySelector(`[data-card-id="${cardId}"]`);
  if (!card || !button || button.disabled) return;
  button.querySelector('.bio-match-front').classList.add('d-none');
  button.querySelector('.bio-match-face').classList.remove('d-none');

  if (!bioMatchState.first) {
    bioMatchState.first = cardId;
    return;
  }

  bioMatchState.attempts += 1;
  bioMatchState.locked = true;
  const firstCard = bioMatchState.cards.find(item => item.cardId === bioMatchState.first);
  const firstButton = document.querySelector(`[data-card-id="${bioMatchState.first}"]`);
  const feedback = document.getElementById('bioMatchFeedback');

  if (firstCard.id === card.id) {
    bioMatchState.matches += 1;
    firstButton.disabled = true;
    button.disabled = true;
    firstButton.classList.add('border-success', 'bg-success-subtle');
    button.classList.add('border-success', 'bg-success-subtle');
    document.getElementById('bioMatchScore').textContent = bioMatchState.matches;

    feedback.innerHTML = `
      <div class="alert alert-success border-success-subtle shadow-sm py-2 px-3 mt-2 d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2">
        <div>
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <i class="fa-solid fa-circle-check text-success fs-5"></i>
            <strong>Correct Match:</strong> <span class="fw-bold text-dark">${card.label}</span>
            <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill">${card.discipline}</span>
          </div>
          <div class="small text-muted mt-1"><i class="fa-solid fa-stethoscope text-danger me-1"></i><strong>Clinical Pearl:</strong> ${card.clinicalNote}</div>
        </div>
        <button class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-bold text-nowrap mt-1 mt-sm-0" onclick="openMbbsInspectModal('${card.id}')">
          <i class="fa-solid fa-magnifying-glass-plus me-1"></i> Inspect Specimen
        </button>
      </div>
    `;

    bioMatchState.first = null;
    bioMatchState.locked = false;
    if (bioMatchState.matches === BIOLOGY_IMAGE_PAIRS.length) {
      finishGame('Biology Image Pair Matching', 'Biology', bioMatchState.matches, BIOLOGY_IMAGE_PAIRS.length);
      feedback.innerHTML += `<div class="alert alert-success py-2 fw-bold mt-2"><i class="fa-solid fa-trophy text-warning me-1"></i> Outstanding! All MBBS medical specimens matched in ${bioMatchState.attempts} attempts!</div>`;
    }
  } else {
    feedback.innerHTML = '<div class="alert alert-warning py-2 shadow-sm"><i class="fa-solid fa-circle-exclamation me-1"></i> Different medical specimens. Review the features and try another pair.</div>';
    setTimeout(() => {
      firstButton.querySelector('.bio-match-front').classList.remove('d-none');
      firstButton.querySelector('.bio-match-face').classList.add('d-none');
      button.querySelector('.bio-match-front').classList.remove('d-none');
      button.querySelector('.bio-match-face').classList.add('d-none');
      bioMatchState.first = null;
      bioMatchState.locked = false;
    }, 850);
  }
}

function openMbbsInspectModal(specimenId) {
  const item = MBBS_SPECIMENS_DATABASE[specimenId];
  if (!item) return;

  const modalEl = document.getElementById('mbbsSpecimenModal');
  if (!modalEl) return;

  const titleEl = document.getElementById('mbbsModalTitle');
  const imgEl = document.getElementById('mbbsModalImage');
  const magEl = document.getElementById('mbbsModalMag');
  const discEl = document.getElementById('mbbsModalDiscipline');
  const headingEl = document.getElementById('mbbsModalHeading');
  const noteEl = document.getElementById('mbbsModalClinicalNote');
  const structEl = document.getElementById('mbbsModalStructures');

  if (titleEl) titleEl.textContent = item.label;
  if (imgEl) {
    imgEl.src = item.image;
    imgEl.alt = item.label;
  }
  if (magEl) magEl.textContent = item.mag || 'Medical Visual Specimen';
  if (discEl) discEl.textContent = item.discipline || 'MBBS Curriculum';
  if (headingEl) headingEl.textContent = item.shortLabel || item.label;
  if (noteEl) noteEl.textContent = item.clinicalNote || 'Clinical correlation details.';
  if (structEl) structEl.textContent = item.structures || 'Key medical anatomical and histological landmarks.';

  if (window.bootstrap && bootstrap.Modal) {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  }
}

// -------------------------------------------------------------
// GAME 2: MATHEMATICS SEQUENCE & MISSING NUMBER PUZZLE
// -------------------------------------------------------------
const MATH_PUZZLES = [
  { seq: "2, 3, 5, 7, 11, ?", ans: 13, options: [12, 13, 15, 17], rule: "Prime Number Sequence" },
  { seq: "1, 1, 2, 3, 5, 8, ?", ans: 13, options: [11, 12, 13, 15], rule: "Fibonacci Sequence (sum of preceding two)" },
  { seq: "3, 9, 27, 81, ?", ans: 243, options: [162, 214, 243, 300], rule: "Geometric Progression (multiply by 3)" },
  { seq: "4, 9, 16, 25, 36, ?", ans: 49, options: [45, 48, 49, 52], rule: "Consecutive Squares (2², 3², 4², 5², 6², 7²)" },
  { seq: "100, 93, 86, 79, ?", ans: 72, options: [70, 71, 72, 74], rule: "Arithmetic Progression (subtract 7)" },
  { seq: "2, 6, 12, 20, 30, ?", ans: 42, options: [36, 40, 42, 48], rule: "Products n(n+1)" },
  { seq: "81, 27, 9, 3, ?", ans: 1, options: [0, 1, 2, 6], rule: "Divide by 3" },
  { seq: "5, 10, 20, 40, ?", ans: 80, options: [60, 70, 80, 100], rule: "Double each term" },
  { seq: "1, 4, 9, 16, 25, ?", ans: 36, options: [30, 32, 36, 40], rule: "Consecutive squares" },
  { seq: "144, 121, 100, 81, ?", ans: 64, options: [49, 64, 72, 81], rule: "Descending squares" },
  { seq: "7, 14, 28, 56, ?", ans: 112, options: [84, 98, 112, 120], rule: "Multiply by 2" }
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
  { event: "Invention of the Printing Press", year: "1440 CE", order: 2 },
  { event: "Battle of Panipat (First)", year: "1526 CE", order: 3 },
  { event: "American Declaration of Independence", year: "1776 CE", order: 4 },
  { event: "Storming of the Bastille (French Revolution)", year: "1789 CE", order: 5 },
  { event: "First World War begins", year: "1914 CE", order: 6 },
  { event: "Dandi Salt March (Mahatma Gandhi)", year: "1930 CE", order: 7 },
  { event: "Indian Independence Day", year: "1947 CE", order: 8 }
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
// HISTORY IMPORTANT DATES MATCHING
// -------------------------------------------------------------
const HISTORY_DATE_PAIRS = [
  { id: 'independence', event: 'Indian Independence', date: '15 August 1947' },
  { id: 'republic', event: 'Indian Republic Day', date: '26 January 1950' },
  { id: 'dandi', event: 'Dandi Salt March', date: '12 March 1930' },
  { id: 'bastille', event: 'Storming of the Bastille', date: '14 July 1789' },
  { id: 'panipat', event: 'First Battle of Panipat', date: '21 April 1526' },
  { id: 'un', event: 'United Nations founded', date: '24 October 1945' }
];

let historyMatchState = { cards: [], selected: null, locked: false, matches: 0, attempts: 0 };

function initHistoryMatchGame() {
  const board = document.getElementById('historyMatchBoard');
  if (!board) return;
  const cards = HISTORY_DATE_PAIRS.flatMap(pair => [
    { id: pair.id, type: 'event', text: pair.event, pairId: pair.id },
    { id: `${pair.id}-date`, type: 'date', text: pair.date, pairId: pair.id }
  ]).sort(() => Math.random() - 0.5);
  historyMatchState = { cards, selected: null, locked: false, matches: 0, attempts: 0 };
  document.getElementById('historyMatchScore').textContent = '0';
  document.getElementById('historyMatchFeedback').innerHTML = '';
  board.innerHTML = cards.map((card, index) => `
    <div class="col">
      <button class="history-match-card btn btn-outline-warning w-100 p-2" data-history-card="${index}" onclick="selectHistoryMatchCard(${index})">
        <span class="history-match-front d-flex align-items-center justify-content-center rounded-3 border bg-white" style="min-height: 95px; font-size: 1.8rem;">?</span>
        <span class="history-match-face d-none flex-column align-items-center justify-content-center rounded-3 border bg-warning-subtle p-2" style="min-height: 95px;"><i class="fa-solid ${card.type === 'event' ? 'fa-landmark' : 'fa-calendar-day'} mb-1"></i><strong>${card.text}</strong></span>
      </button>
    </div>
  `).join('');
}

function selectHistoryMatchCard(index) {
  if (historyMatchState.locked || historyMatchState.selected === index) return;
  const card = historyMatchState.cards[index];
  const button = document.querySelector(`[data-history-card="${index}"]`);
  if (!card || !button || button.disabled) return;
  button.querySelector('.history-match-front').classList.add('d-none');
  button.querySelector('.history-match-face').classList.remove('d-none');
  if (historyMatchState.selected === null) {
    historyMatchState.selected = index;
    return;
  }

  const firstIndex = historyMatchState.selected;
  const firstCard = historyMatchState.cards[firstIndex];
  const firstButton = document.querySelector(`[data-history-card="${firstIndex}"]`);
  historyMatchState.attempts += 1;
  historyMatchState.locked = true;
  const feedback = document.getElementById('historyMatchFeedback');

  if (firstCard.pairId === card.pairId && firstCard.type !== card.type) {
    historyMatchState.matches += 1;
    firstButton.disabled = true;
    button.disabled = true;
    document.getElementById('historyMatchScore').textContent = historyMatchState.matches;
    feedback.innerHTML = `<div class="alert alert-success py-2">Correct pair: ${card.pairId}.</div>`;
    historyMatchState.selected = null;
    historyMatchState.locked = false;
    if (historyMatchState.matches === HISTORY_DATE_PAIRS.length) {
      finishGame('History Important Dates Matching', 'History', historyMatchState.matches, HISTORY_DATE_PAIRS.length);
      feedback.innerHTML = `<div class="alert alert-success py-2 fw-bold">All important dates matched in ${historyMatchState.attempts} attempts!</div>`;
    }
  } else {
    feedback.innerHTML = '<div class="alert alert-warning py-2">Those cards do not match. Try again.</div>';
    setTimeout(() => {
      firstButton.querySelector('.history-match-front').classList.remove('d-none');
      firstButton.querySelector('.history-match-face').classList.add('d-none');
      button.querySelector('.history-match-front').classList.remove('d-none');
      button.querySelector('.history-match-face').classList.add('d-none');
      historyMatchState.selected = null;
      historyMatchState.locked = false;
    }, 700);
  }
}

// -------------------------------------------------------------
// GAME 4: GEOGRAPHY COUNTRY & CAPITAL PAIR MATCHING
// -------------------------------------------------------------
const GEO_PAIRS = [
  { country: "Japan", capital: "Tokyo" },
  { country: "France", capital: "Paris" },
  { country: "Australia", capital: "Canberra" },
  { country: "India", capital: "New Delhi" },
  { country: "Egypt", capital: "Cairo" },
  { country: "Brazil", capital: "Brasilia" },
  { country: "Canada", capital: "Ottawa" },
  { country: "Kenya", capital: "Nairobi" },
  { country: "Italy", capital: "Rome" },
  { country: "Nepal", capital: "Kathmandu" }
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
    finishGame('Geography Capital Matching', 'Geography', geoScore, GEO_PAIRS.length * 10);
  }
}

// -------------------------------------------------------------
// GAME 5: GK & LOGIC ODD-ONE-OUT CHALLENGE
// -------------------------------------------------------------
const ODD_ITEMS = [
  { group: ["Mercury", "Venus", "Moon", "Mars"], odd: "Moon", reason: "Moon is a natural satellite, whereas Mercury, Venus, and Mars are planets." },
  { group: ["Oxygen", "Nitrogen", "Iron", "Argon"], odd: "Iron", reason: "Iron is a metallic solid at room temperature, while the others are atmospheric gases." },
  { group: ["Square", "Rectangle", "Rhombus", "Triangle"], odd: "Triangle", reason: "Triangle has 3 sides (trilateral); the others are 4-sided quadrilaterals." },
  { group: ["Tiger", "Lion", "Leopard", "Kangaroo"], odd: "Kangaroo", reason: "Kangaroo is a marsupial native to Australia, while the others are big felid carnivores." },
  { group: ["Mercury", "Venus", "Earth", "Sun"], odd: "Sun", reason: "The Sun is a star, while the others are planets." },
  { group: ["HTTP", "FTP", "SMTP", "RAM"], odd: "RAM", reason: "RAM is computer memory, while the others are network or internet protocols." },
  { group: ["Rose", "Lotus", "Mango", "Jasmine"], odd: "Mango", reason: "Mango is a fruit, while the others are flowers." },
  { group: ["Triangle", "Square", "Circle", "Pentagon"], odd: "Circle", reason: "A circle has no straight sides, while the others are polygons." },
  { group: ["Oxygen", "Hydrogen", "Nitrogen", "Granite"], odd: "Granite", reason: "Granite is a solid rock, while the others are gases." },
  { group: ["January", "March", "July", "Monday"], odd: "Monday", reason: "Monday is a weekday, while the others are months." }
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
