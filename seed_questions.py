"""Populate the database with questions from questions/algebra1.json."""
import json
import os
import database

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), 'questions', 'algebra1.json')


def seed():
    database.init_db()
    conn = database.get_db()

    existing = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    if existing > 0:
        print(f'Database already has {existing} questions. Skipping seed.')
        conn.close()
        return

    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    for q in questions:
        conn.execute(
            '''INSERT INTO questions
               (subject, topic, question_text, choice_a, choice_b, choice_c, choice_d,
                correct_answer, exam_year, exam_session, question_number)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                q['subject'], q['topic'], q['question_text'],
                q['choice_a'], q['choice_b'], q['choice_c'], q['choice_d'],
                q['correct_answer'], q['exam_year'], q['exam_session'], q['question_number'],
            )
        )

    conn.commit()
    count = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    conn.close()
    print(f'Seeded {count} questions.')


if __name__ == '__main__':
    seed()
