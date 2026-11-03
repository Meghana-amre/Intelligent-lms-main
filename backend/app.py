import csv
import io
import os
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from database import (
    init_db, get_db_connection, get_or_create_default_student,
    get_student_profile, authenticate_student, create_student, fetch_unique_test_questions,
    record_test_result, record_game_score
)
from summarizer import textrank_summarize
from map_generator import generate_visual_map
from ml_engine import get_student_performance_data, get_model_explainability_metrics
from ai_services import generate_quiz_from_notes, solve_doubt_ai, compare_summarization_study

app = Flask(__name__)
app.config['SECRET_KEY'] = 'intelligent-lms-secret-key-cse-2026'

# Initialize database tables on startup
with app.app_context():
    init_db()

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'student_id' not in session or not current_student():
            session.clear()
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped_view

def current_student():
    return get_student_profile(session['student_id'])

# -------------------------------------------------------------
# CORE ROUTES
# -------------------------------------------------------------
@app.route('/')
def home():
    """Shows login first, or routes students to their self-assessment dashboard."""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = current_student()
    if not student:
        session.clear()
        return redirect(url_for('login'))
    perf = get_student_performance_data(student['id'], student['category'])
    return render_template(
        'index.html',
        student=student,
        perf=perf,
        hs_data=perf,
        puc_data=perf,
        hs_student=student,
        puc_student=student
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        next_url = request.args.get('next')
        try:
            student_id = int(request.form.get('student_id', '').strip())
        except ValueError:
            student_id = 0
        student = authenticate_student(student_id, request.form.get('password', ''))
        if student:
            session.clear()
            session['student_id'] = student['id']
            destination = next_url or url_for('home')
            return redirect(destination)
        else:
            error = 'Invalid Student ID or password.'

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or category not in ('highschool', 'puc_degree') or len(password) < 6:
            error = 'Enter a name, choose a category, and use a password of at least 6 characters.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        else:
            student_id = create_student(name, category, password)
            session.clear()
            session['student_id'] = student_id
            return redirect(url_for('home'))

    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/about')
def about():
    """Deprecated page redirect to the main dashboard."""
    return redirect(url_for('home'))

# -------------------------------------------------------------
# HIGH SCHOOL MODULES
# -------------------------------------------------------------
@app.route('/highschool')
@login_required
def highschool_dashboard():
    """High School Student Hub: 4 Core Modules + Performance Card."""
    student = current_student()
    if student['category'] != 'highschool':
        return redirect(url_for('puc_degree_dashboard'))
    student_id = student['id']
    perf = get_student_performance_data(student_id, 'highschool')
    return render_template('highschool/dashboard.html', perf=perf)

@app.route('/highschool/test')
@login_required
def highschool_test():
    """Advanced Subject Mastery Challenge."""
    student_id = current_student()['id']
    return render_template('highschool/test.html', student_id=student_id)

@app.route('/highschool/games')
@login_required
def highschool_games():
    """Interactive Educational & IQ Games arena."""
    student_id = current_student()['id']
    return render_template('highschool/games.html', student_id=student_id)

@app.route('/highschool/map-method')
@login_required
def highschool_map_method():
    """Theory-to-Visual Map generator."""
    return render_template('highschool/map_method.html')

@app.route('/highschool/newspaper')
@login_required
def highschool_newspaper():
    """TextRank Newspaper Summarizer & Infographic generator."""
    return render_template('highschool/newspaper.html')

@app.route('/highschool/performance')
@login_required
def highschool_performance():
    """Self-assessment student performance analysis & adaptive recommendations."""
    student = current_student()
    if student['category'] != 'highschool':
        return redirect(url_for('puc_degree_performance'))
    student_id = student['id']
    perf = get_student_performance_data(student_id, 'highschool')
    return render_template('highschool/performance.html', perf=perf)

@app.route('/highschool/performance/download')
@login_required
def download_highschool_performance():
    """Downloads the authenticated high school student's performance analysis as CSV."""
    return download_performance_report('highschool', 'high_school')

# -------------------------------------------------------------
# PUC & DEGREE MODULES
# -------------------------------------------------------------
@app.route('/puc-degree')
@login_required
def puc_degree_dashboard():
    """PUC & Degree Student Hub."""
    student = current_student()
    if student['category'] != 'puc_degree':
        return redirect(url_for('highschool_dashboard'))
    student_id = student['id']
    perf = get_student_performance_data(student_id, 'puc_degree')
    return render_template('puc_degree/dashboard.html', perf=perf)

@app.route('/puc-degree/test')
@login_required
def puc_degree_test():
    """Subject-balanced CET/JEE or DSA Aptitude assessment."""
    student_id = current_student()['id']
    subject = request.args.get('subject', 'CET')
    allowed_subjects = {'CET', 'JEE', 'DSA Aptitude'}
    if subject not in allowed_subjects:
        return redirect(url_for('puc_degree_dashboard'))
    question_count = 150 if subject in {'CET', 'JEE'} else 50
    return render_template(
        'puc_degree/test.html',
        student_id=student_id,
        assessment_subject=subject,
        question_count=question_count,
        questions_per_subject=50,
    )

@app.route('/puc-degree/performance')
@login_required
def puc_degree_performance():
    """Technical performance dashboard with Chart.js analytics & recommendations."""
    student = current_student()
    if student['category'] != 'puc_degree':
        return redirect(url_for('highschool_performance'))
    student_id = student['id']
    perf = get_student_performance_data(student_id, 'puc_degree')
    return render_template('puc_degree/performance.html', perf=perf)

@app.route('/puc-degree/performance/download')
@login_required
def download_puc_degree_performance():
    """Downloads the authenticated PUC/Degree student's performance analysis as CSV."""
    return download_performance_report('puc_degree', 'puc_degree')

def download_performance_report(category, filename_prefix):
    """Builds a portable CSV report from the same data shown on the dashboard."""
    student = current_student()
    if student['category'] != category:
        return redirect(url_for('highschool_performance' if category == 'puc_degree' else 'puc_degree_performance'))

    perf = get_student_performance_data(student['id'], category)
    report = io.StringIO(newline='')
    writer = csv.writer(report)
    writer.writerow(['Performance Analysis Report'])
    writer.writerow(['Student ID', student['id']])
    writer.writerow(['Student Name', student['name']])
    writer.writerow(['Category', 'High School' if category == 'highschool' else 'PUC & Degree'])
    writer.writerow([])

    writer.writerow(['Summary Metric', 'Value'])
    summary = [
        ('Tests Attempted', perf['total_tests']),
        ('Questions Evaluated', perf['total_questions']),
        ('Correct Answers', perf['total_correct']),
        ('Incorrect Answers', perf['total_incorrect']),
        ('Unattempted Questions', perf['total_unattempted']),
        ('Average Score (%)', perf['average_score']),
        ('Highest Score (%)', perf['highest_score']),
        ('Latest Score (%)', perf['latest_score']),
        ('Overall Percentage (%)', perf['overall_percentage']),
        ('Performance Tier', perf['ml_predicted_level']),
        ('Mastery Cluster', perf['ml_cluster']),
        ('Games Recorded', perf['game_stats']['total_games']),
        ('Games Average Score (%)', perf['game_stats']['avg_accuracy']),
    ]
    for label, value in summary:
        writer.writerow([label, value])

    writer.writerow([])
    writer.writerow(['Subject / Topic Breakdown'])
    writer.writerow(['Subject', 'Correct', 'Total Asked', 'Percentage'])
    for subject in perf['subject_breakdown']:
        writer.writerow([
            subject['subject'],
            subject['correct'],
            subject['total_asked'],
            f"{subject['percentage']}%"
        ])

    if category == 'puc_degree':
        for assessment in perf['assessment_breakdowns']:
            writer.writerow([])
            writer.writerow([f"{assessment['exam']} Subject Scores"])
            writer.writerow(['Subject', 'Correct', 'Total Asked', 'Score (%)'])
            for subject in assessment['subjects']:
                writer.writerow([
                    subject['subject'],
                    subject['correct'],
                    subject['total_asked'],
                    f"{subject['percentage']}%"
                ])
            writer.writerow([
                'Overall Score',
                assessment['total_correct'],
                assessment['total_asked'],
                f"{assessment['percentage']}%"
            ])

    writer.writerow([])
    writer.writerow(['Test History'])
    writer.writerow(['Test', 'Score (%)'])
    for label, score in zip(perf['history_labels'], perf['history_scores']):
        writer.writerow([label, score])

    writer.writerow([])
    writer.writerow(['Recommendations'])
    writer.writerow(['Recommendation', perf['recommendation']])
    writer.writerow(['ML Decision Rule', perf['ml_decision_rule']])
    writer.writerow(['Strong Areas', ', '.join(perf['strong_subjects']) or 'None recorded'])
    writer.writerow(['Areas Needing Improvement', ', '.join(perf['weak_subjects']) or 'None recorded'])

    response = make_response('\ufeff' + report.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}_performance_analysis.csv'
    return response

# -------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/questions', methods=['GET'])
def api_get_questions():
    """
    Returns unique questions for a test session.
    Strictly guarantees NO duplicates within the active test set.
    """
    category = request.args.get('category', 'highschool')
    subject = request.args.get('subject', None)
    requested_count = request.args.get('count')
    if category == 'puc_degree' and subject in {'CET', 'JEE'}:
        count = 150
    elif requested_count in (None, '', 'all'):
        count = 50 if category == 'puc_degree' else 100
    else:
        count = max(1, int(requested_count))

    questions = fetch_unique_test_questions(category, count=count, subject=subject)

    # Re-number with serial numbers 1 to count
    formatted = []
    for idx, q in enumerate(questions, start=1):
        item = dict(q)
        item['serial_number'] = idx
        formatted.append(item)

    return jsonify({
        "status": "success",
        "category": category,
        "count": len(formatted),
        "questions": formatted
    })

@app.route('/api/submit-test', methods=['POST'])
def api_submit_test():
    """
    Evaluates submitted test answers, persists record to SQLite,
    and returns comprehensive evaluation metrics.
    """
    data = request.get_json() or {}
    if 'student_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in first'}), 401
    category = data.get('category', 'highschool')
    student_id = session['student_id']
    student = current_student()
    if student['category'] != category or data.get('student_id') not in (None, student_id):
        return jsonify({'status': 'error', 'message': 'Student session does not match this test'}), 403
    exam = data.get('exam')
    if category == 'puc_degree':
        if exam not in {'CET', 'JEE', 'DSA Aptitude'}:
            return jsonify({'status': 'error', 'message': 'Select a valid PUC/Degree assessment'}), 400
    else:
        exam = None
    test_title = data.get('test_title', 'General Subject Assessment' if category == 'highschool' else 'Logical & Technical Assessment')
    answers_data = data.get('answers', [])

    result = record_test_result(student_id, category, test_title, answers_data, exam=exam)
    return jsonify({
        "status": "success",
        "result": result
    })

@app.route('/api/save-game-score', methods=['POST'])
def api_save_game_score():
    """Stores educational game results in database."""
    data = request.get_json() or {}
    if 'student_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in first'}), 401
    category = data.get('category', 'highschool')
    student_id = session['student_id']
    if current_student()['category'] != category:
        return jsonify({'status': 'error', 'message': 'Student session does not match this game'}), 403
    game_type = data.get('game_type', 'IQ Game')
    subject = data.get('subject', 'General')
    score = int(data.get('score', 0))
    max_score = int(data.get('max_score', 100))
    time_taken = int(data.get('time_taken', 0))

    game_id = record_game_score(student_id, game_type, subject, score, max_score, time_taken)
    return jsonify({
        "status": "success",
        "game_id": game_id,
        "message": "Game score recorded successfully!"
    })

@app.route('/api/summarize-news', methods=['POST'])
def api_summarize_news():
    """TextRank extractive summarization API."""
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"status": "error", "message": "Please enter article text"}), 400

    result = textrank_summarize(text)
    return jsonify({
        "status": "success",
        "data": result
    })

@app.route('/api/generate-map', methods=['POST'])
def api_generate_map():
    """Dynamic theory-to-visual map generation API."""
    data = request.get_json() or {}
    text = data.get('theory_text', '').strip()
    if not text:
        return jsonify({"status": "error", "message": "Please enter theory text"}), 400

    result = generate_visual_map(text)
    return jsonify({
        "status": "success",
        "data": result
    })

@app.route('/api/performance/<category>')
def api_get_performance(category):
    """Returns real-time performance metrics for Chart.js graphing."""
    if 'student_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in first'}), 401
    student_id = session['student_id']
    if current_student()['category'] != category:
        return jsonify({'status': 'error', 'message': 'Student session does not match this category'}), 403
    data = get_student_performance_data(student_id, category)
    return jsonify(data)

@app.route('/api/students/<int:student_id>')
def api_get_student(student_id):
    """Returns a student's non-sensitive ID card details."""
    student = get_student_profile(student_id)
    if not student:
        return jsonify({'status': 'error', 'message': 'Student not found'}), 404
    return jsonify({'status': 'success', 'student': student})

# -------------------------------------------------------------
# GENERATIVE AI & NLP SERVICES
# -------------------------------------------------------------
@app.route('/ai/quiz-studio')
@login_required
def ai_quiz_studio():
    """Interactive AI Notes-to-Quiz Generator and ROUGE Summarization Studio."""
    return render_template('ai_quiz_gen.html')

@app.route('/api/ai/generate-quiz', methods=['POST'])
def api_ai_generate_quiz():
    """Converts user lecture notes or paragraphs into structured MCQs."""
    data = request.get_json() or {}
    notes = data.get('notes_text', '').strip()
    if not notes:
        return jsonify({"status": "error", "message": "Please provide notes or textbook excerpt"}), 400
    subject = data.get('subject', 'General')
    num_q = int(data.get('num_questions', 5))
    difficulty = data.get('difficulty', 'Medium')

    res = generate_quiz_from_notes(notes, num_questions=num_q, subject=subject, difficulty=difficulty)
    return jsonify(res)

@app.route('/api/ai/solve-doubt', methods=['POST'])
def api_ai_solve_doubt():
    """Contextual academic doubt solver explaining why an option is right/wrong."""
    data = request.get_json() or {}
    q_text = data.get('question', '').strip()
    options = data.get('options', {})
    correct_opt = data.get('correct_option', '')
    selected_opt = data.get('selected_option', '')
    student_query = data.get('student_query', '')

    res = solve_doubt_ai(q_text, options, correct_opt, selected_opt, student_query)
    return jsonify(res)

@app.route('/api/ai/compare-summary', methods=['POST'])
def api_ai_compare_summary():
    """Runs TextRank vs Abstractive summarization and computes ROUGE metrics."""
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"status": "error", "message": "Please provide text for summarization study"}), 400

    res = compare_summarization_study(text)
    return jsonify(res)

# -------------------------------------------------------------
# MACHINE LEARNING EXPLAINABILITY
# -------------------------------------------------------------
@app.route('/ml-insights')
@login_required
def ml_insights():
    """Interactive visual dashboard of Confusion Matrix, Feature Importance, and Model Comparison."""
    metrics = get_model_explainability_metrics()
    return render_template('ml_insights.html', metrics=metrics)

@app.route('/api/ml/metrics')
def api_ml_metrics():
    """JSON API exposing multi-model evaluation metrics for academic verification."""
    metrics = get_model_explainability_metrics()
    return jsonify(metrics)

if __name__ == '__main__':
    print("Starting AI-Powered Intelligent LMS server on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
