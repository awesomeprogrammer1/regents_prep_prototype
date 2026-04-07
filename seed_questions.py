"""Populate the database with questions from questions/algebra1.json."""
import json
import os
import database

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), 'questions', 'algebra1.json')


def seed():
    database.init_db()
    conn = database.get_db()

    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

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
