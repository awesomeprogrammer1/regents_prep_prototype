import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'regents.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def get_practice_questions(subject, limit=10):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM questions WHERE subject = ? ORDER BY RANDOM() LIMIT ?',
        (subject, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_question_by_id(question_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_response(user_id, question_id, selected_answer, is_correct, session_id):
    conn = get_db()
    conn.execute(
        'INSERT INTO responses (user_id, question_id, selected_answer, is_correct, session_id) VALUES (?, ?, ?, ?, ?)',
        (user_id, question_id, selected_answer, int(is_correct), session_id)
    )
    conn.commit()
    conn.close()


def get_session_results(session_id, user_id):
    """Return per-topic breakdown for a completed session."""
    conn = get_db()
    rows = conn.execute(
        '''
        SELECT q.topic,
               COUNT(*) AS attempted,
               SUM(r.is_correct) AS correct
        FROM responses r
        JOIN questions q ON q.id = r.question_id
        WHERE r.session_id = ? AND r.user_id = ?
        GROUP BY q.topic
        ORDER BY (CAST(SUM(r.is_correct) AS REAL) / COUNT(*)) ASC
        ''',
        (session_id, user_id)
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        attempted = row['attempted']
        correct = row['correct']
        accuracy = round((correct / attempted) * 100) if attempted else 0
        results.append({
            'topic': row['topic'],
            'attempted': attempted,
            'correct': correct,
            'accuracy': accuracy,
            'needs_work': accuracy < 60,
        })
    return results


def get_session_score(session_id, user_id):
    """Return total correct and total attempted for a session."""
    conn = get_db()
    row = conn.execute(
        'SELECT COUNT(*) AS attempted, SUM(is_correct) AS correct FROM responses WHERE session_id = ? AND user_id = ?',
        (session_id, user_id)
    ).fetchone()
    conn.close()
    attempted = row['attempted'] or 0
    correct = row['correct'] or 0
    return correct, attempted


def get_dashboard_data(user_id):
    """Return cumulative per-topic stats and weak topic recommendations."""
    conn = get_db()
    rows = conn.execute(
        '''
        SELECT q.topic,
               COUNT(*) AS attempted,
               SUM(r.is_correct) AS correct
        FROM responses r
        JOIN questions q ON q.id = r.question_id
        WHERE r.user_id = ?
        GROUP BY q.topic
        ORDER BY (CAST(SUM(r.is_correct) AS REAL) / COUNT(*)) ASC
        ''',
        (user_id,)
    ).fetchall()

    session_count = conn.execute(
        'SELECT COUNT(DISTINCT session_id) AS cnt FROM responses WHERE user_id = ?',
        (user_id,)
    ).fetchone()['cnt']

    total_row = conn.execute(
        'SELECT COUNT(*) AS attempted, SUM(is_correct) AS correct FROM responses WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    conn.close()

    topics = []
    for row in rows:
        attempted = row['attempted']
        correct = row['correct']
        accuracy = round((correct / attempted) * 100) if attempted else 0
        topics.append({
            'topic': row['topic'],
            'attempted': attempted,
            'correct': correct,
            'accuracy': accuracy,
            'needs_work': accuracy < 60,
        })

    total_attempted = total_row['attempted'] or 0
    total_correct = total_row['correct'] or 0
    overall_accuracy = round((total_correct / total_attempted) * 100) if total_attempted else 0

    weak_topics = [t for t in topics if t['needs_work']][:3]

    return {
        'topics': topics,
        'weak_topics': weak_topics,
        'session_count': session_count,
        'total_attempted': total_attempted,
        'total_correct': total_correct,
        'overall_accuracy': overall_accuracy,
    }


def create_user(username, password_hash):
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        conn.commit()
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_username(username):
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


