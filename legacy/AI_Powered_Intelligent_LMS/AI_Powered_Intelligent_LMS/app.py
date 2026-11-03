import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import (
    init_db, get_db_connection, get_or_create_default_student,
    fetch_unique_test_questions, record_test_result, record_game_score
)
from summarizer import textrank_summarize
from map_generator import generate_visual_map
from ml_engine import get_student_performance_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'intelligent-lms-secret-key-cse-2026'

# Initialize database tables on startup
with app.app_context():
    init_db()

# -------------------------------------------------------------
# CORE ROUTES
# -------------------------------------------------------------
@app.route('/')
def home():
    """Main landing page: Modern dashboard with category selection."""
    hs_student_id = get_or_create_default_student('highschool')
    puc_student_id = get_or_create_default_student('puc_degree')

    hs_data = get_student_performance_data(hs_student_id, 'highschool')
    puc_data = get_student_performance_data(puc_student_id, 'puc_degree')

    return render_template('index.html', hs_data=hs_data, puc_data=puc_data)

@app.route('/about')
def about():
    """Project documentation, architecture, genuine IEEE citations, and viva guide."""
    return render_template('about.html')

# -------------------------------------------------------------
# HIGH SCHOOL MODULES
# -------------------------------------------------------------
@app.route('/highschool')
def highschool_dashboard():
    """High School Student Hub: 4 Core Modules + Performance Card."""
    student_id = get_or_create_default_student('highschool')
    perf = get_student_performance_data(student_id, 'highschool')
    return render_template('highschool/dashboard.html', perf=perf)

@app.route('/highschool/test')
def highschool_test():
    """50-Question Subject-based MCQ Test."""
    student_id = get_or_create_default_student('highschool')
    return render_template('highschool/test.html', student_id=student_id)

@app.route('/highschool/games')
def highschool_games():
    """Interactive Educational & IQ Games arena."""
    student_id = get_or_create_default_student('highschool')
    return render_template('highschool/games.html', student_id=student_id)

@app.route('/highschool/map-method')
def highschool_map_method():
    """Theory-to-Visual Map generator."""
    return render_template('highschool/map_method.html')

@app.route('/highschool/newspaper')
def highschool_newspaper():
    """TextRank Newspaper Summarizer & Infographic generator."""
    return render_template('highschool/newspaper.html')

@app.route('/highschool/performance')
def highschool_performance():
    """Self-assessment student performance analysis & adaptive recommendations."""
    student_id = get_or_create_default_student('highschool')
    perf = get_student_performance_data(student_id, 'highschool')
    return render_template('highschool/performance.html', perf=perf)

# -------------------------------------------------------------
# PUC & DEGREE MODULES
# -------------------------------------------------------------
@app.route('/puc-degree')
def puc_degree_dashboard():
    """PUC & Degree Student Hub."""
    student_id = get_or_create_default_student('puc_degree')
    perf = get_student_performance_data(student_id, 'puc_degree')
    return render_template('puc_degree/dashboard.html', perf=perf)

@app.route('/puc-degree/test')
def puc_degree_test():
    """100-Question Technical & Logical Assessment."""
    student_id = get_or_create_default_student('puc_degree')
    return render_template('puc_degree/test.html', student_id=student_id)

@app.route('/puc-degree/performance')
def puc_degree_performance():
    """Technical performance dashboard with Chart.js analytics & recommendations."""
    student_id = get_or_create_default_student('puc_degree')
    perf = get_student_performance_data(student_id, 'puc_degree')
    return render_template('puc_degree/performance.html', perf=perf)

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
    count = int(request.args.get('count', 50 if category == 'highschool' else 100))
    subject = request.args.get('subject', None)

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
    category = data.get('category', 'highschool')
    student_id = data.get('student_id') or get_or_create_default_student(category)
    test_title = data.get('test_title', 'General Subject Assessment' if category == 'highschool' else 'Logical & Technical Assessment')
    answers_data = data.get('answers', [])

    result = record_test_result(student_id, category, test_title, answers_data)
    return jsonify({
        "status": "success",
        "result": result
    })

@app.route('/api/save-game-score', methods=['POST'])
def api_save_game_score():
    """Stores educational game results in database."""
    data = request.get_json() or {}
    category = data.get('category', 'highschool')
    student_id = data.get('student_id') or get_or_create_default_student(category)
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
    student_id = get_or_create_default_student(category)
    data = get_student_performance_data(student_id, category)
    return jsonify(data)

if __name__ == '__main__':
    print("Starting AI-Powered Intelligent LMS server on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
