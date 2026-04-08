"""Populate the database with questions from the questions/ directory."""
import json
import os
import database

_DIR = os.path.dirname(__file__)
QUESTION_FILES = [
    os.path.join(_DIR, 'questions', 'algebra1.json'),
    os.path.join(_DIR, 'questions', 'geometry.json'),
]


def seed():
    database.init_db()
    conn = database.get_db()

    questions = []
    for path in QUESTION_FILES:
        with open(path, 'r', encoding='utf-8') as f:
            questions.extend(json.load(f))

    inserted = 0
    for q in questions:
        # Use (subject, exam_year, exam_session, question_number) as a unique key
        existing = conn.execute(
            'SELECT id FROM questions WHERE subject=? AND exam_year=? AND exam_session=? AND question_number=?',
            (q['subject'], q['exam_year'], q['exam_session'], q['question_number'])
        ).fetchone()
        if existing:
            # Update explanation in case it changed
            conn.execute(
                'UPDATE questions SET explanation=? WHERE subject=? AND exam_year=? AND exam_session=? AND question_number=?',
                (q.get('explanation', 'To Be Changed'), q['subject'], q['exam_year'], q['exam_session'], q['question_number'])
            )
            continue
        conn.execute(
            '''INSERT INTO questions
               (subject, topic, question_text, choice_a, choice_b, choice_c, choice_d,
                correct_answer, exam_year, exam_session, question_number, question_type, explanation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                q['subject'], q['topic'], q['question_text'],
                q['choice_a'], q['choice_b'], q['choice_c'], q['choice_d'],
                q['correct_answer'], q['exam_year'], q['exam_session'],
                q['question_number'], q.get('question_type', 'multiple_choice'),
                q.get('explanation', 'To Be Changed'),
            )
        )
        inserted += 1

    conn.commit()
    total = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    conn.close()
    print(f'Inserted {inserted} new questions. Total: {total}.')


if __name__ == '__main__':
    seed()
