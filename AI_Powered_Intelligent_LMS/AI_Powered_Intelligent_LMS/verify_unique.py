from database import fetch_unique_test_questions

def test_no_duplicates():
    print("Testing High School 50-Question Test Uniqueness...")
    hs_q = fetch_unique_test_questions('highschool', count=50)
    assert len(hs_q) == 50, f"Expected 50 questions, got {len(hs_q)}"
    hs_ids = [q['id'] for q in hs_q]
    assert len(set(hs_ids)) == 50, f"Duplicate detected in High School test: {len(hs_ids)} vs {len(set(hs_ids))} unique"
    print(f"PASS: High School test has {len(hs_q)} unique questions with 0 duplicates.")

    print("\nTesting PUC & Degree 100-Question Test Uniqueness...")
    puc_q = fetch_unique_test_questions('puc_degree', count=100)
    assert len(puc_q) == 100, f"Expected 100 questions, got {len(puc_q)}"
    puc_ids = [q['id'] for q in puc_q]
    assert len(set(puc_ids)) == 100, f"Duplicate detected in PUC & Degree test: {len(puc_ids)} vs {len(set(puc_ids))} unique"
    print(f"PASS: PUC & Degree test has {len(puc_q)} unique questions with 0 duplicates.")

    print("\nAll uniqueness tests passed successfully!")

if __name__ == '__main__':
    test_no_duplicates()
