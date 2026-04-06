import uuid
from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import database
import seed_questions

app = Flask(__name__)
app.secret_key = 'dev-secret-change-in-production'

# Initialise DB and seed questions on every startup (both are idempotent)
database.init_db()
seed_questions.seed()

GUEST_USER_ID = 0
SESSION_LENGTH = 10

SUBJECTS = ['Algebra I']


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def current_user():
    user_id = session.get('user_id')
    if user_id and user_id != GUEST_USER_ID:
        return database.get_user_by_id(user_id)
    return None


def check_grid_in(submitted, correct):
    """Case-insensitive, whitespace-stripped comparison for grid-in answers.
    Also normalises numeric equivalence (e.g. '4.0' == '4')."""
    s = submitted.strip().lower()
    c = correct.strip().lower()
    if s == c:
        return True
    try:
        return float(s) == float(c)
    except ValueError:
        return False


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id') or session.get('user_id') == GUEST_USER_ID:
            flash('Please log in to view this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Username and password are required.')
            return render_template('register.html')
        if len(username) < 3 or len(username) > 30:
            flash('Username must be 3-30 characters.')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.')
            return render_template('register.html')
        password_hash = generate_password_hash(password)
        user_id = database.create_user(username, password_hash)
        if user_id is None:
            flash('That username is already taken.')
            return render_template('register.html')
        session['user_id'] = user_id
        session['username'] = username
        flash(f'Welcome, {username}!')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = database.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Main routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html', subjects=SUBJECTS)


@app.route('/practice/<subject>')
def practice(subject):
    if subject not in SUBJECTS:
        flash('Subject not found.')
        return redirect(url_for('index'))

    # Set up guest session if not logged in
    if not session.get('user_id'):
        session['user_id'] = GUEST_USER_ID
        session['username'] = 'Guest'

    questions = database.get_practice_questions(subject, limit=SESSION_LENGTH)
    if not questions:
        flash('No questions available for this subject yet.')
        return redirect(url_for('index'))

    practice_session_id = str(uuid.uuid4())
    session['practice_session_id'] = practice_session_id
    session['question_ids'] = [q['id'] for q in questions]
    session['question_index'] = 0
    session['subject'] = subject

    return redirect(url_for('question'))


@app.route('/question')
def question():
    if 'question_ids' not in session:
        return redirect(url_for('index'))

    index = session.get('question_index', 0)
    question_ids = session['question_ids']

    if index >= len(question_ids):
        return redirect(url_for('results'))

    q = database.get_question_by_id(question_ids[index])
    if not q:
        return redirect(url_for('results'))

    return render_template(
        'practice.html',
        question=q,
        question_number=index + 1,
        total=len(question_ids),
    )


@app.route('/answer', methods=['POST'])
def answer():
    if 'question_ids' not in session:
        return redirect(url_for('index'))

    index = session.get('question_index', 0)
    question_ids = session['question_ids']
    question_id = question_ids[index]

    q = database.get_question_by_id(question_id)
    if not q:
        return redirect(url_for('results'))

    is_grid_in = q.get('question_type') == 'grid_in'

    if is_grid_in:
        selected = request.form.get('grid_answer', '').strip()
        is_correct = check_grid_in(selected, q['correct_answer'])
    else:
        selected = request.form.get('answer', '').upper()
        is_correct = selected == q['correct_answer'].upper()

    user_id = session.get('user_id', GUEST_USER_ID)
    if user_id != GUEST_USER_ID:
        database.save_response(
            user_id=user_id,
            question_id=question_id,
            selected_answer=selected,
            is_correct=is_correct,
            session_id=session['practice_session_id'],
        )

    choices = {
        'A': q['choice_a'],
        'B': q['choice_b'],
        'C': q['choice_c'],
        'D': q['choice_d'],
    }

    return render_template(
        'feedback.html',
        question=q,
        selected=selected,
        is_correct=is_correct,
        choices=choices,
        is_grid_in=is_grid_in,
        question_number=index + 1,
        total=len(question_ids),
        is_last=(index + 1 >= len(question_ids)),
        is_guest=(user_id == GUEST_USER_ID),
    )


@app.route('/next')
def next_question():
    if 'question_ids' not in session:
        return redirect(url_for('index'))
    session['question_index'] = session.get('question_index', 0) + 1
    return redirect(url_for('question'))


@app.route('/results')
def results():
    user_id = session.get('user_id')
    practice_session_id = session.get('practice_session_id')

    if not practice_session_id or user_id == GUEST_USER_ID or not user_id:
        return render_template('results.html', guest=True, topics=[], correct=0, attempted=0, accuracy=0)

    topic_breakdown = database.get_session_results(practice_session_id, user_id)
    correct, attempted = database.get_session_score(practice_session_id, user_id)
    accuracy = round((correct / attempted) * 100) if attempted else 0

    weak_topics = [t for t in topic_breakdown if t['needs_work']][:3]

    return render_template(
        'results.html',
        guest=False,
        topics=topic_breakdown,
        correct=correct,
        attempted=attempted,
        accuracy=accuracy,
        weak_topics=weak_topics,
        subject=session.get('subject', ''),
    )


@app.route('/map')
def network_map():
    return render_template('map.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    data = database.get_dashboard_data(user_id)
    return render_template('dashboard.html', **data, username=session.get('username'))


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)


