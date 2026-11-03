import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.cluster import KMeans
from database import get_db_connection

# Synthetic training dataset representing benchmark educational performance data
# Features: [Average Score %, Consistency (1 - variance), Tests Completed, Game Accuracy %, Attempt Rate %]
X_TRAIN = np.array([
    [95.0, 0.95, 8, 92.0, 98.0], # Excellent
    [91.0, 0.90, 6, 88.0, 95.0], # Excellent
    [86.0, 0.88, 5, 85.0, 92.0], # Excellent
    [82.0, 0.82, 5, 80.0, 90.0], # Very Good
    [78.0, 0.80, 4, 76.0, 88.0], # Very Good
    [75.0, 0.78, 4, 72.0, 85.0], # Very Good
    [68.0, 0.70, 3, 65.0, 80.0], # Good
    [64.0, 0.68, 3, 62.0, 78.0], # Good
    [60.0, 0.65, 2, 58.0, 75.0], # Good
    [52.0, 0.55, 2, 50.0, 70.0], # Average
    [48.0, 0.52, 2, 45.0, 65.0], # Average
    [42.0, 0.45, 1, 40.0, 60.0], # Average
    [35.0, 0.40, 1, 35.0, 50.0], # Needs Improvement
    [28.0, 0.35, 1, 30.0, 45.0], # Needs Improvement
    [20.0, 0.30, 1, 25.0, 40.0], # Needs Improvement
])

Y_TRAIN = [
    "Excellent", "Excellent", "Excellent",
    "Very Good", "Very Good", "Very Good",
    "Good", "Good", "Good",
    "Average", "Average", "Average",
    "Needs Improvement", "Needs Improvement", "Needs Improvement"
]

FEATURE_NAMES = ["Average Score", "Consistency", "Tests Count", "Game Accuracy", "Attempt Rate"]

# Initialize and train Decision Tree Model
clf_model = DecisionTreeClassifier(max_depth=4, random_state=42)
clf_model.fit(X_TRAIN, Y_TRAIN)

# Initialize K-Means Clustering (3 Mastery Clusters: High, Medium, Low)
kmeans_model = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans_model.fit(X_TRAIN[:, [0, 3]])

def get_student_performance_data(student_id, category):
    """
    Queries actual tests, test_questions, and game_results from the SQLite database,
    computes aggregate metrics, runs the ML classifier, and returns analytics.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch Tests
    cursor.execute('''
        SELECT id, test_title, total_questions, correct_answers, incorrect_answers,
               unattempted, score, percentage, performance_level, created_at
        FROM tests
        WHERE student_id = ? AND category = ?
        ORDER BY created_at ASC
    ''', (student_id, category))
    test_rows = [dict(r) for r in cursor.fetchall()]

    # 2. Fetch Games
    cursor.execute('''
        SELECT game_type, subject, score, max_score, percentage, time_taken_seconds, created_at
        FROM game_results
        WHERE student_id = ?
        ORDER BY created_at DESC
    ''', (student_id,))
    game_rows = [dict(r) for r in cursor.fetchall()]

    # 3. Fetch Subject-wise performance from test_questions joined with questions
    cursor.execute('''
        SELECT q.subject,
               COUNT(tq.id) as total_asked,
               SUM(tq.is_correct) as correct_count
        FROM test_questions tq
        JOIN questions q ON tq.question_id = q.id
        JOIN tests t ON tq.test_id = t.id
        WHERE t.student_id = ? AND t.category = ?
        GROUP BY q.subject
    ''', (student_id, category))
    subject_rows = [dict(r) for r in cursor.fetchall()]

    conn.close()

    total_tests = len(test_rows)
    if total_tests == 0:
        # Default empty state with constructive initial profile
        return {
            "has_data": False,
            "category": category,
            "total_tests": 0,
            "total_questions": 0,
            "total_correct": 0,
            "total_incorrect": 0,
            "total_unattempted": 0,
            "average_score": 0.0,
            "highest_score": 0.0,
            "latest_score": 0.0,
            "overall_percentage": 0.0,
            "performance_level": "Needs Evaluation",
            "ml_predicted_level": "Needs Evaluation",
            "ml_decision_rule": "No active test records in database yet.",
            "ml_cluster": "Unassigned",
            "strong_subjects": [],
            "weak_subjects": [],
            "subject_breakdown": [],
            "game_stats": {"total_games": len(game_rows), "avg_accuracy": 0.0},
            "history_labels": [],
            "history_scores": [],
            "recommendation": "Start by taking your first assessment or educational game to generate performance insights!"
        }

    total_q = sum(t['total_questions'] for t in test_rows)
    total_corr = sum(t['correct_answers'] for t in test_rows)
    total_inc = sum(t['incorrect_answers'] for t in test_rows)
    total_unatt = sum(t['unattempted'] for t in test_rows)

    percentages = [t['percentage'] for t in test_rows]
    avg_score = round(sum(percentages) / total_tests, 2)
    highest_score = max(percentages)
    latest_score = percentages[-1]
    overall_pct = round((total_corr / total_q * 100), 2) if total_q > 0 else 0.0

    # Game accuracy
    if game_rows:
        game_acc = round(sum(g['percentage'] for g in game_rows) / len(game_rows), 2)
    else:
        game_acc = avg_score

    attempt_rate = round(((total_q - total_unatt) / max(1, total_q)) * 100, 2)
    variance = np.var(percentages) if len(percentages) > 1 else 0.0
    consistency = round(max(0.1, 1.0 - (min(variance, 1000.0) / 1000.0)), 2)

    # Prepare features for ML Model
    student_features = np.array([[avg_score, consistency, min(total_tests, 10), game_acc, attempt_rate]])
    ml_predicted_level = clf_model.predict(student_features)[0]

    # Cluster prediction
    cluster_id = kmeans_model.predict([[avg_score, game_acc]])[0]
    cluster_labels = {0: "High Mastery", 1: "Intermediate Proficiency", 2: "Developing Foundation"}
    ml_cluster = cluster_labels.get(cluster_id, "Standard")

    # Subject analysis
    subject_breakdown = []
    strong_subjects = []
    weak_subjects = []

    for s in subject_rows:
        tot = s['total_asked']
        cor = s['correct_count'] or 0
        pct = round((cor / tot * 100), 1) if tot > 0 else 0.0
        item = {
            "subject": s['subject'],
            "total_asked": tot,
            "correct": cor,
            "percentage": pct
        }
        subject_breakdown.append(item)
        if pct >= 75.0:
            strong_subjects.append(s['subject'])
        elif pct < 60.0:
            weak_subjects.append(s['subject'])

    # Sort breakdown by percentage descending
    subject_breakdown.sort(key=lambda x: x['percentage'], reverse=True)

    # Intelligent Adaptive Recommendation Generation
    if strong_subjects and weak_subjects:
        strong_str = ", ".join(strong_subjects[:2])
        weak_str = ", ".join(weak_subjects[:2])
        if category == 'highschool':
            recommendation = (f"Your understanding in {strong_str} is exceptionally strong! "
                              f"To raise your overall percentage, focus more revision and practice tests on {weak_str}.")
        else:
            recommendation = (f"Excellent proficiency demonstrated in {strong_str}. "
                              f"We recommend prioritizing deep-dive algorithmic problem solving in {weak_str}.")
    elif weak_subjects:
        weak_str = ", ".join(weak_subjects)
        recommendation = (f"You need additional practice in: {weak_str}. "
                          f"Use the Map Method to visualize core concepts before attempting tests.")
    elif strong_subjects:
        recommendation = "Outstanding performance across all evaluated topics! Continue challenging yourself with advanced assessment sets."
    else:
        recommendation = f"Consistent effort observed with an average score of {avg_score}%. Continue taking subject assessments to unlock personalized weak-topic drills."

    # Explainable ML Decision Rule for Viva
    ml_decision_rule = (
        f"Decision Tree Split: [Average Score = {avg_score}%, Consistency = {consistency}, Attempt Rate = {attempt_rate}%] "
        f"-> Classified into Performance Tier: '{ml_predicted_level}'"
    )

    history_labels = [f"Test {i+1}" for i in range(total_tests)]
    history_scores = percentages

    return {
        "has_data": True,
        "category": category,
        "total_tests": total_tests,
        "total_questions": total_q,
        "total_correct": total_corr,
        "total_incorrect": total_inc,
        "total_unattempted": total_unatt,
        "average_score": avg_score,
        "highest_score": highest_score,
        "latest_score": latest_score,
        "overall_percentage": overall_pct,
        "performance_level": test_rows[-1]['performance_level'],
        "ml_predicted_level": ml_predicted_level,
        "ml_decision_rule": ml_decision_rule,
        "ml_cluster": ml_cluster,
        "strong_subjects": strong_subjects,
        "weak_subjects": weak_subjects,
        "subject_breakdown": subject_breakdown,
        "game_stats": {
            "total_games": len(game_rows),
            "avg_accuracy": game_acc
        },
        "history_labels": history_labels,
        "history_scores": history_scores,
        "recommendation": recommendation,
        "algorithm_info": {
            "name": "Decision Tree Classifier & K-Means Educational Data Mining",
            "paper": "Using Data Mining to Predict Secondary School Student Performance",
            "authors": "P. Cortez and A. M. G. Silva (FUBUTEC)",
            "ieee_reference": "S. K. Mohamad and Z. Tasir, 'Educational Data Mining: A Review,' 2013 IEEE 9th CITA, pp. 1-6."
        }
    }

if __name__ == '__main__':
    # Test with default student
    res = get_student_performance_data(1, 'highschool')
    print("Performance has_data:", res['has_data'])
    print("ML predicted level:", res['ml_predicted_level'])
    print("Decision rule:", res['ml_decision_rule'])
