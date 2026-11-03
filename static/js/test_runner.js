/**
 * Universal Test Runner Engine
 * Handles:
 * - Loading every available unique question for the selected category
 * - Strict duplicate prevention
 * - Real-time 🟢 Correct / 🔴 Incorrect visual feedback with explanations
 * - Navigation palette (1 to N)
 * - Timer & progress calculation
 * - Scorecard calculation & database persistence
 */

class TestRunner {
  constructor(config) {
    this.category = config.category || 'highschool';
    this.subject = config.subject || null;
    this.targetCount = config.count || 'all';
    this.studentId = config.studentId || 1;
    this.testTitle = config.testTitle || (this.category === 'highschool' ? 'High School Advanced Subject Challenge' : 'PUC & Degree Technical Assessment');

    this.questions = [];
    this.currentIndex = 0;
    this.userAnswers = {}; // question_id -> { selected: 'A', isCorrect: bool }
    this.timerSeconds = 0;
    this.timerInterval = null;

    this.init();
  }

  async init() {
    this.renderLoading(true);
    try {
      const subjectParam = this.subject ? `&subject=${encodeURIComponent(this.subject)}` : '';
      const response = await fetch(`/api/questions?category=${this.category}&count=${this.targetCount}${subjectParam}`);
      const data = await response.json();

      if (data.status === 'success' && data.questions && data.questions.length > 0) {
        this.questions = data.questions;
        if (this.category === 'puc_degree') {
          const subjectOrder = { Physics: 0, Chemistry: 1, Mathematics: 2 };
          this.questions.sort((a, b) => {
            const orderDifference = (subjectOrder[a.subject] ?? 3) - (subjectOrder[b.subject] ?? 3);
            return orderDifference || a.subject.localeCompare(b.subject) || a.topic.localeCompare(b.topic);
          });
        }
        this.renderLoading(false);
        this.startTimer();
        this.renderQuestionPalette();
        this.renderSubjectSections();
        this.displayQuestion(0);
      } else {
        this.renderError("Failed to load questions from database.");
      }
    } catch (err) {
      console.error(err);
      this.renderError("Network error while initializing test session.");
    }
  }

  startTimer() {
    const timerElem = document.getElementById('testTimer');
    this.timerInterval = setInterval(() => {
      this.timerSeconds++;
      const mins = Math.floor(this.timerSeconds / 60);
      const secs = this.timerSeconds % 60;
      if (timerElem) {
        timerElem.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      }
    }, 1000);
  }

  renderQuestionPalette() {
    const paletteContainer = document.getElementById('questionPalette');
    if (!paletteContainer) return;

    paletteContainer.innerHTML = '';
    let lastSubject = null;
    this.questions.forEach((q, idx) => {
      if (this.category === 'puc_degree' && q.subject !== lastSubject) {
        const sectionHeading = document.createElement('div');
        sectionHeading.className = 'w-100 small fw-bold text-primary mt-2';
        sectionHeading.textContent = q.subject;
        paletteContainer.appendChild(sectionHeading);
        lastSubject = q.subject;
      }
      const badge = document.createElement('div');
      badge.className = `question-badge ${idx === 0 ? 'active' : ''}`;
      badge.id = `palette-badge-${idx}`;
      badge.textContent = idx + 1;
      badge.title = `Question ${idx + 1} (${q.subject})`;
      badge.onclick = () => this.displayQuestion(idx);
      paletteContainer.appendChild(badge);
    });
  }

  renderSubjectSections() {
    const sectionsContainer = document.getElementById('subjectSections');
    if (!sectionsContainer || this.category !== 'puc_degree') return;

    sectionsContainer.innerHTML = '';
    const firstQuestionBySubject = new Map();
    const counts = new Map();
    this.questions.forEach((question, index) => {
      if (!firstQuestionBySubject.has(question.subject)) {
        firstQuestionBySubject.set(question.subject, index);
      }
      counts.set(question.subject, (counts.get(question.subject) || 0) + 1);
    });

    firstQuestionBySubject.forEach((firstIndex, subject) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-outline-primary btn-sm rounded-pill';
      button.textContent = `${subject} · ${counts.get(subject)} questions`;
      button.onclick = () => this.displayQuestion(firstIndex);
      sectionsContainer.appendChild(button);
    });
  }

  displayQuestion(index) {
    if (index < 0 || index >= this.questions.length) return;
    this.currentIndex = index;
    const q = this.questions[index];

    // Update active badge in palette
    document.querySelectorAll('.question-badge').forEach((b, i) => {
      b.classList.remove('active');
      if (i === index) b.classList.add('active');
    });

    // Update Header labels
    const qNumberElem = document.getElementById('qNumber');
    const qSubjectElem = document.getElementById('qSubject');
    const qDifficultyElem = document.getElementById('qDifficulty');
    const qTextElem = document.getElementById('qText');
    const progressBar = document.getElementById('testProgress');

    if (qNumberElem) qNumberElem.textContent = `Question ${index + 1}`;
    if (qSubjectElem) qSubjectElem.textContent = q.subject;
    if (qDifficultyElem) qDifficultyElem.textContent = q.difficulty || 'Standard';
    if (qTextElem) qTextElem.textContent = q.question;

    // Progress percentage
    const answeredCount = Object.keys(this.userAnswers).length;
    const pct = Math.round((answeredCount / this.questions.length) * 100);
    if (progressBar) {
      progressBar.style.width = `${pct}%`;
      progressBar.setAttribute('aria-valuenow', pct);
    }
    const answeredCounter = document.getElementById('answeredCounter');
    if (answeredCounter) {
      answeredCounter.textContent = `${answeredCount}/${this.questions.length} Answered`;
    }

    // Render Options
    const optionsContainer = document.getElementById('optionsContainer');
    optionsContainer.innerHTML = '';

    const options = [
      { key: 'A', text: q.option_a },
      { key: 'B', text: q.option_b },
      { key: 'C', text: q.option_c },
      { key: 'D', text: q.option_d }
    ];

    const currentAnswer = this.userAnswers[q.id];

    options.forEach(opt => {
      const optDiv = document.createElement('div');
      optDiv.className = 'option-box';
      optDiv.id = `option-${opt.key}`;

      let iconHtml = `<span class="badge bg-light text-dark border me-3 fw-bold">${opt.key}</span>`;

      if (currentAnswer) {
        // Test question already answered, show feedback
        if (opt.key === q.correct_answer) {
          optDiv.classList.add('correct-feedback');
          iconHtml = `<span class="badge bg-success text-white me-3"><i class="fa-solid fa-check"></i></span>`;
        } else if (currentAnswer.selected === opt.key) {
          optDiv.classList.add('incorrect-feedback');
          iconHtml = `<span class="badge bg-danger text-white me-3"><i class="fa-solid fa-xmark"></i></span>`;
        }
      }

      optDiv.innerHTML = `
        ${iconHtml}
        <div class="flex-grow-1 fw-medium">${opt.text}</div>
      `;

      if (!currentAnswer) {
        optDiv.onclick = () => this.handleSelectOption(q, opt.key);
      }

      optionsContainer.appendChild(optDiv);
    });

    // Render Immediate Feedback Banner if answered
    this.renderFeedbackBanner(q, currentAnswer);

    // Update Navigation Buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    if (prevBtn) prevBtn.disabled = (index === 0);
    if (nextBtn) {
      if (index === this.questions.length - 1) {
        nextBtn.innerHTML = '<i class="fa-solid fa-flag-checkered me-1"></i> Submit Test';
        nextBtn.className = 'btn btn-success px-4 py-2 rounded-pill fw-bold shadow-sm';
        nextBtn.onclick = () => this.confirmSubmit();
      } else {
        nextBtn.innerHTML = 'Next Question <i class="fa-solid fa-arrow-right ms-1"></i>';
        nextBtn.className = 'btn btn-primary px-4 py-2 rounded-pill fw-bold shadow-sm';
        nextBtn.onclick = () => this.displayQuestion(this.currentIndex + 1);
      }
    }
  }

  handleSelectOption(question, selectedKey) {
    const isCorrect = (selectedKey === question.correct_answer);
    this.userAnswers[question.id] = {
      selected: selectedKey,
      isCorrect: isCorrect
    };

    // Mark badge in palette
    const badge = document.getElementById(`palette-badge-${this.currentIndex}`);
    if (badge) {
      badge.classList.add('answered');
      if (isCorrect) {
        badge.style.borderBottom = "4px solid #10b981";
      } else {
        badge.style.borderBottom = "4px solid #ef4444";
      }
    }

    // Re-render question to display the 🟢 Correct or 🔴 Incorrect feedback
    this.displayQuestion(this.currentIndex);
  }

  renderFeedbackBanner(question, answerRecord) {
    const feedbackBox = document.getElementById('feedbackBox');
    if (!feedbackBox) return;

    if (!answerRecord) {
      feedbackBox.classList.add('d-none');
      feedbackBox.innerHTML = '';
      return;
    }

    feedbackBox.classList.remove('d-none');

    if (answerRecord.isCorrect) {
      feedbackBox.className = 'feedback-banner bg-success-subtle text-success border border-success-subtle mb-4';
      feedbackBox.innerHTML = `
        <div class="d-flex align-items-center gap-2 fw-bold fs-5 mb-1">
          <span>🟢 Correct</span>
        </div>
        <div class="small text-dark mb-1">
          <strong>Correct Answer:</strong> Option ${question.correct_answer}
        </div>
        <div class="small text-muted">
          <strong>Explanation:</strong> ${question.explanation}
        </div>
      `;
    } else {
      feedbackBox.className = 'feedback-banner bg-danger-subtle text-danger border border-danger-subtle mb-4';
      feedbackBox.innerHTML = `
        <div class="d-flex align-items-center gap-2 fw-bold fs-5 mb-1">
          <span>🔴 Incorrect</span>
        </div>
        <div class="small text-dark mb-1">
          <strong>Your Answer:</strong> Option ${answerRecord.selected} &nbsp;|&nbsp;
          <strong>Correct Answer:</strong> Option ${question.correct_answer}
        </div>
        <div class="small text-muted">
          <strong>Explanation:</strong> ${question.explanation}
        </div>
      `;
    }
  }

  confirmSubmit() {
    const total = this.questions.length;
    const answered = Object.keys(this.userAnswers).length;
    const unattempted = total - answered;

    const modalMsg = document.getElementById('submitModalMsg');
    if (modalMsg) {
      modalMsg.textContent = `You have answered ${answered} of ${total} questions. ${unattempted} questions remain unattempted. Are you ready to finish and submit your assessment?`;
    }

    const modalEl = document.getElementById('submitConfirmModal');
    if (modalEl) {
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    } else {
      this.submitTest();
    }
  }

  async submitTest() {
    if (this.timerInterval) clearInterval(this.timerInterval);

    // Format payload
    const answersPayload = this.questions.map((q, idx) => {
      const record = this.userAnswers[q.id];
      return {
        question_id: q.id,
        question_number: idx + 1,
        selected_option: record ? record.selected : 'NONE',
        correct_answer: q.correct_answer
      };
    });

    try {
      const res = await fetch('/api/submit-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: this.category,
          student_id: this.studentId,
          test_title: this.testTitle,
          exam: this.category === 'puc_degree' ? this.subject : null,
          answers: answersPayload
        })
      });

      const data = await res.json();
      if (data.status === 'success') {
        this.renderResultCard(data.result);
      } else {
        alert("Failed to save score. Please retry.");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting test results.");
    }
  }

  renderResultCard(result) {
    const testArea = document.getElementById('testMainArea');
    const resultArea = document.getElementById('testResultArea');

    if (testArea) testArea.classList.add('d-none');
    if (resultArea) {
      resultArea.classList.remove('d-none');

      document.getElementById('resTotalQ').textContent = result.total_questions;
      document.getElementById('resCorrect').textContent = result.correct_answers;
      document.getElementById('resIncorrect').textContent = result.incorrect_answers;
      document.getElementById('resUnattempted').textContent = result.unattempted;
      document.getElementById('resScore').textContent = `${result.score}/${result.total_questions}`;
      document.getElementById('resPercentage').textContent = `${result.percentage}%`;

      const perfBadge = document.getElementById('resPerfLevel');
      perfBadge.textContent = result.performance_level;

      if (result.percentage >= 75) {
        perfBadge.className = 'badge bg-success fs-5 px-4 py-2 rounded-pill';
      } else if (result.percentage >= 60) {
        perfBadge.className = 'badge bg-primary fs-5 px-4 py-2 rounded-pill';
      } else if (result.percentage >= 40) {
        perfBadge.className = 'badge bg-warning text-dark fs-5 px-4 py-2 rounded-pill';
      } else {
        perfBadge.className = 'badge bg-danger fs-5 px-4 py-2 rounded-pill';
      }
    }
  }

  renderLoading(isLoading) {
    const spinner = document.getElementById('loadingSpinner');
    const content = document.getElementById('testContent');
    if (spinner) spinner.style.display = isLoading ? 'block' : 'none';
    if (content) content.style.display = isLoading ? 'none' : 'block';
  }

  renderError(msg) {
    const errorBox = document.getElementById('testErrorBox');
    if (errorBox) {
      errorBox.textContent = msg;
      errorBox.classList.remove('d-none');
    }
  }
}
