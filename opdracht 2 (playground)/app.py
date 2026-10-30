from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = 'jouw_geheime_sleutel_hier'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')
SCHEMA = os.path.join(BASE_DIR, 'database.sql')

# Complete puntensleutel voor alle 25 psychologische vragen
SCORING_KEY = {
    1: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'junko'], 'D': ['nobu', 'shin', 'miu', 'takumi']},
    2: {'A': ['takumi', 'ren'], 'B': ['hachi', 'reira', 'shin'], 'C': ['junko', 'yasu'], 'D': ['nana', 'nobu', 'miu']},
    3: {'A': ['nana'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'takumi', 'junko'], 'D': ['shin', 'nobu', 'miu', 'ren']},
    4: {'A': ['nana', 'ren', 'takumi'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'junko', 'nobu'], 'D': ['shin', 'miu']},
    5: {'A': ['nana', 'ren'], 'B': ['hachi', 'shin', 'reira'], 'C': ['takumi', 'junko'], 'D': ['nobu', 'miu', 'yasu']},
    6: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'takumi', 'junko'], 'D': ['shin', 'miu', 'nobu']},
    7: {'A': ['nana', 'shin'], 'B': ['hachi', 'reira', 'miu'], 'C': ['takumi', 'ren', 'junko'], 'D': ['nobu', 'yasu']},
    8: {'A': ['nana', 'ren', 'shin'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'junko', 'nobu', 'miu'], 'D': ['takumi']},
    9: {'A': ['nana'], 'B': ['hachi', 'shin', 'reira'], 'C': ['yasu', 'takumi', 'junko'], 'D': ['nobu', 'miu', 'ren']},
    10: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['takumi', 'yasu', 'junko'], 'D': ['nobu', 'shin', 'miu']},
    11: {'A': ['nana', 'ren', 'reira'], 'B': ['hachi'], 'C': ['yasu', 'takumi'], 'D': ['nobu', 'shin', 'miu', 'junko']},
    12: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira', 'shin'], 'C': ['takumi', 'yasu', 'junko'], 'D': ['nobu', 'miu']},
    13: {'A': ['nana', 'ren', 'shin'], 'B': ['hachi', 'reira', 'miu'], 'C': ['takumi'], 'D': ['nobu', 'yasu', 'junko']},
    14: {'A': ['nana', 'hachi', 'shin'], 'B': ['takumi', 'junko'], 'C': ['ren', 'reira', 'miu'], 'D': ['yasu', 'nobu']},
    15: {'A': ['nana', 'ren', 'takumi'], 'B': ['hachi', 'reira', 'shin'], 'C': ['yasu', 'junko'], 'D': ['nobu', 'miu']},
    16: {'A': ['nana'], 'B': ['hachi', 'reira'], 'C': ['takumi', 'yasu', 'junko'], 'D': ['shin', 'ren', 'miu', 'nobu']},
    17: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'junko', 'nobu'], 'D': ['shin', 'miu', 'takumi']},
    18: {'A': ['nana', 'ren', 'shin'], 'B': ['hachi', 'reira'], 'C': ['takumi', 'junko'], 'D': ['nobu', 'yasu', 'miu']},
    19: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['yasu', 'takumi', 'junko'], 'D': ['nobu', 'shin', 'miu']},
    20: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['takumi', 'yasu', 'junko'], 'D': ['nobu', 'shin', 'miu']},
    21: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['takumi', 'junko', 'yasu'], 'D': ['nobu', 'shin', 'miu']},
    22: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira', 'shin'], 'C': ['takumi', 'junko', 'yasu'], 'D': ['nobu', 'miu']},
    23: {'A': ['nana', 'shin', 'ren'], 'B': ['hachi', 'reira', 'miu'], 'C': ['takumi', 'yasu', 'junko'], 'D': ['nobu']},
    24: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira'], 'C': ['takumi', 'junko', 'yasu'], 'D': ['nobu', 'shin', 'miu']},
    25: {'A': ['nana', 'ren'], 'B': ['hachi', 'reira', 'shin'], 'C': ['takumi', 'junko'], 'D': ['nobu', 'miu', 'yasu']}
}

CHARACTER_INFO = {
    'nana': {
        'name': 'Nana Osaki',
        'description': 'Fiercely independent and driven by raw passion. You guard your freedom with everything you have, but beneath your punk exterior lies a deeply loyal soul terrified of abandonment.',
        'image': 'nana.png'
    },
    'hachi': {
        'name': 'Nana "Hachi" Komatsu',
        'description': 'A romantic idealist with an anxious attachment style. You feel things deeply, love unconditionally, and seek constant emotional warmth, wearing your heart proudly on your sleeve.',
        'image': 'hachi.png'
    },
    'yasu': {
        'name': 'Yasushi "Yasu" Takagi',
        'description': 'The ultimate anchor. Rational, protective, and calm under pressure. You quietly sacrifice your own needs to stabilize the people around you, serving as their moral compass.',
        'image': 'yasu.png'
    },
    'nobu': {
        'name': 'Nobuhiro "Nobu" Grand',
        'description': 'Pure-hearted, empathetic, and endlessly optimistic. You approach life and love with honest intentions, though your sensitivity leaves you vulnerable to heartbreak.',
        'image': 'nobu.png'
    },
    'shin': {
        'name': 'Shinichi Okazaki',
        'description': 'Carrying fragmented vulnerability beneath a cool facade. You crave deep, unconditional affection to heal an inner emptiness, often masking your pain with sensory escapes.',
        'image': 'shin.png'
    },
    'ren': {
        'name': 'Ren Honjo',
        'description': 'Intense, ambitious, and counter-dependent. Your life is fueled by your art and deep attachments, fighting a constant internal battle between freedom and the fear of losing what you love.',
        'image': 'ren.png'
    },
    'takumi': {
        'name': 'Takumi Ichinose',
        'description': 'Calculated, controlling, and pragmatic. You engineer security and dominance to protect your inner circle, often hiding your vulnerabilities behind a flawless, strategic mask.',
        'image': 'takumi.png'
    },
    'reira': {
        'name': 'Reira Serizawa',
        'description': 'An emotional siren with an ethereal voice and a fragile psyche. You live for the idealized perfection of romance, but struggle deeply with a fear of being left alone.',
        'image': 'reira.png'
    },
    'miu': {
        'name': 'Miu Shinoda',
        'description': 'Gentle, observant, and artistically intuitive. You navigate complex emotional landscapes with quiet grace and a unique, alternative perspective on the world.',
        'image': 'miu.png'
    },
    'junko': {
        'name': 'Junko Saotome',
        'description': 'Fiercely grounded, practical, and sharp. You possess strict personal boundaries and offer no-nonsense wisdom, acting as the ultimate realist among your peers.',
        'image': 'junko.png'
    }
}


# ---------- Database ----------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """Maakt de tabellen aan als ze nog niet bestaan."""
    conn = get_db_connection()
    with open(SCHEMA, encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


init_db()


# ---------- Hulpfuncties ----------

def get_char_info(key):
    return CHARACTER_INFO.get(key, {
        'name': key.capitalize(),
        'description': 'Jouw unieke persoonlijkheidsprofiel.',
        'image': 'default.png'
    })


def calculate_scores(answers):
    scores = {char: 0 for char in CHARACTER_INFO}
    for q_num in range(1, 26):
        selected = answers.get(f'q{q_num}')
        if selected:
            for char in SCORING_KEY[q_num].get(selected, []):
                scores[char] += 1
    return scores


def sort_percentages(scores):
    max_possible_points = 25
    percentages = {
        char: round(min((pts / max_possible_points) * 100, 100), 1)
        for char, pts in scores.items()
    }
    return sorted(percentages.items(), key=lambda x: x[1], reverse=True)


# ---------- Routes ----------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()

        
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ? AND password = ?',
                (username, password)
            ).fetchone()
        except Exception as e:
            user = None
            print("SQL Error:", e)

        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user'] = user['username']
            return redirect(url_for('quiz'))
        else:
            error = 'Ongeldige gebruikersnaam of wachtwoord.'

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            error = 'Vul alle velden in.'
        else:
            conn = get_db_connection()
            try:
                cur = conn.execute(
                    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, password)
                )
                conn.commit()
                session['user_id'] = cur.lastrowid
                session['user'] = username
                return redirect(url_for('quiz'))
            except sqlite3.IntegrityError:
                error = 'Deze gebruikersnaam bestaat al.'
            finally:
                conn.close()

    return render_template('register.html', error=error)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        answers = {f'q{n}': request.form.get(f'q{n}') for n in range(1, 26)}
        scores = calculate_scores(answers)
        top_character = sort_percentages(scores)[0][0]

        conn = get_db_connection()
        cur = conn.execute(
            'INSERT INTO quiz_results (user_id, answers, scores, top_character) VALUES (?, ?, ?, ?)',
            (session['user_id'], json.dumps(answers), json.dumps(scores), top_character)
        )
        conn.commit()
        result_id = cur.lastrowid
        conn.close()

        return redirect(url_for('result', result_id=result_id))

    return render_template('quiz.html')


@app.route('/result')
@app.route('/result/<int:result_id>')
def result(result_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if result_id is None:
        # Laatste resultaat van deze gebruiker
        row = conn.execute(
            'SELECT * FROM quiz_results WHERE user_id = ? ORDER BY id DESC LIMIT 1',
            (session['user_id'],)
        ).fetchone()
    else:
        # Alleen eigen resultaten mogen bekeken worden
        row = conn.execute(
            'SELECT * FROM quiz_results WHERE id = ? AND user_id = ?',
            (result_id, session['user_id'])
        ).fetchone()
    conn.close()

    if row is None:
        return redirect(url_for('quiz'))

    scores = json.loads(row['scores'])
    sorted_scores = sort_percentages(scores)
    char_info = get_char_info(row['top_character'])

    return render_template('result.html', char_info=char_info, sorted_scores=sorted_scores)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute(
        'SELECT username, email, created_at FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    rows = conn.execute(
        'SELECT id, top_character, created_at FROM quiz_results WHERE user_id = ? ORDER BY id DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    if user is None:
        session.clear()
        return redirect(url_for('login'))

    history = [
        {
            'id': r['id'],
            'name': get_char_info(r['top_character'])['name'],
            'date': r['created_at'][:16]
        }
        for r in rows
    ]

    latest = get_char_info(rows[0]['top_character']) if rows else None

    # Meest voorkomende match
    most_common = None
    if rows:
        counts = {}
        for r in rows:
            counts[r['top_character']] = counts.get(r['top_character'], 0) + 1
        most_common = get_char_info(max(counts, key=counts.get))['name']

    return render_template('profile.html', user=user, history=history,
                           latest=latest, most_common=most_common)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)