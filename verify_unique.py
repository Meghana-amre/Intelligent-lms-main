import re

from database import fetch_unique_test_questions, init_db
from question_generator import DSA_APTITUDE_TOPICS

def test_no_duplicates():
    init_db()
    print("Testing High School 50-Question Test Uniqueness...")
    hs_q = fetch_unique_test_questions('highschool', count=50)
    assert len(hs_q) == 50, f"Expected 50 questions, got {len(hs_q)}"
    hs_ids = [q['id'] for q in hs_q]
    assert len(set(hs_ids)) == 50, f"Duplicate detected in High School test: {len(hs_ids)} vs {len(set(hs_ids))} unique"
    hs_text = {' '.join(q['question'].split()).casefold() for q in hs_q}
    assert len(hs_text) == 50, "Repeated question text detected in High School test"
    print(f"PASS: High School test has {len(hs_q)} unique questions with 0 duplicates.")

    print("\nTesting PUC & Degree 50-Question Test Uniqueness...")
    puc_q = fetch_unique_test_questions('puc_degree', count=50)
    assert len(puc_q) == 50, f"Expected 50 questions, got {len(puc_q)}"
    puc_ids = [q['id'] for q in puc_q]
    assert len(set(puc_ids)) == 50, f"Duplicate detected in PUC & Degree test: {len(puc_ids)} vs {len(set(puc_ids))} unique"
    puc_text = {' '.join(q['question'].split()).casefold() for q in puc_q}
    assert len(puc_text) == 50, "Repeated question text detected in PUC & Degree test"
    assert not hs_text & puc_text, "Question text is repeated between High School and PUC/Degree"
    print(f"PASS: PUC & Degree test has {len(puc_q)} unique questions with 0 duplicates.")

    for subject in ('CET', 'JEE', 'DSA Aptitude'):
        required_count = 150 if subject in {'CET', 'JEE'} else 50
        questions = fetch_unique_test_questions('puc_degree', count=required_count, subject=subject)
        texts = {' '.join(q['question'].split()).casefold() for q in questions}
        assert len(questions) == required_count, f"Expected {required_count} {subject} questions, got {len(questions)}"
        assert len(texts) == required_count, f"Repeated question text detected in {subject}"
        if subject in {'CET', 'JEE'}:
            subject_counts = {section: sum(q['subject'] == section for q in questions) for section in (
                'Physics', 'Chemistry', 'Mathematics'
            )}
            assert subject_counts == {
                'Physics': 50, 'Chemistry': 50, 'Mathematics': 50
            }, f'{subject} subject counts are not 50 each: {subject_counts}'
        else:
            topic_counts = {
                topic: sum(question['topic'] == topic for question in questions)
                for topic in DSA_APTITUDE_TOPICS
            }
            assert topic_counts == {
                topic: 5 for topic in DSA_APTITUDE_TOPICS
            }, f'DSA topic counts are not five each: {topic_counts}'
        assert len({q['correct_answer'] for q in questions}) > 1, f"Correct options are not shuffled in {subject}"
        assert not hs_text & texts, f"{subject} repeats a High School question"
        assert not puc_text & texts, f"{subject} repeats the general PUC/Degree bank"
        assert not re.search(
            r'\b(?:question set|in question|in example|in trial)\s+\d+\b',
            ' '.join(q['question'] for q in questions),
            re.IGNORECASE,
        ), f"Generated question index text found in {subject}"
        puc_text.update(texts)
        print(f"PASS: {subject} has {required_count} distinct questions with no cross-bank duplicates.")

    print("\nAll uniqueness tests passed successfully!")

if __name__ == '__main__':
    test_no_duplicates()
