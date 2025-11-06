from flask import Flask, request, redirect, url_for, render_template_string, session, g
import sqlite3
import os
import bcrypt
import time

app = Flask(__name__)
app.secret_key = "secure-demo-key"
DB = "secure_dashboard.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db():
    need_seed = not os.path.exists(DB)
    db = sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash BLOB, fullname TEXT, email TEXT)')
    if need_seed:
        pw = bcrypt.hashpw("DemoPass1!".encode('utf-8'), bcrypt.gensalt())
        db.execute("INSERT INTO users (username, password_hash, fullname, email) VALUES (?, ?, ?, ?)",
                   ("alice", pw, "Alice Demo", "alice@example.com"))
    db.commit()
    db.close()

init_db()

HOME = """
<!doctype html>
<title>Secure Dashboard</title>
<h2>Secure Dashboard Demo</h2>
{% if user %}
  <p>Welcome, {{ user['fullname'] }} ({{ user['username'] }})</p>
  <p>Email: {{ user['email'] }}</p>
  <p><a href="/logout">Logout</a></p>
{% else %}
  <p><a href="/signup">Sign up</a> | <a href="/login">Login</a></p>
{% endif %}
"""

SIGNUP = """
<!doctype html>
<title>Sign Up</title>
<h2>Create Account</h2>
<form method="post">
  Username: <input name="username" maxlength="50"><br>
  Full name: <input name="fullname" maxlength="100"><br>
  Email: <input name="email" maxlength="254"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Sign Up</button>
</form>
<p><a href="/">Home</a></p>
"""

LOGIN = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
<p><a href="/">Home</a></p>
"""

@app.route('/')
def index():
    uid = session.get('user_id')
    user = None
    if uid:
        db = get_db()
        row = db.execute("SELECT username, fullname, email FROM users WHERE id = ?", (uid,)).fetchone()
        if row:
            user = {"username": row[0], "fullname": row[1], "email": row[2]}
    return render_template_string(HOME, user=user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not username or not password or not fullname or not email:
            return "<p>All fields are required. <a href='/signup'>Back</a></p>"
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password_hash, fullname, email) VALUES (?, ?, ?, ?)",
                       (username, pw_hash, fullname, email))
            db.commit()
        except Exception:
            return "<p>Username taken or error. <a href='/signup'>Back</a></p>"
        return redirect(url_for('login'))
    return render_template_string(SIGNUP)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        row = db.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if row:
            user_id, pw_hash = row[0], row[1]
            try:
                if bcrypt.checkpw(password.encode('utf-8'), pw_hash):
                    session['user_id'] = user_id
                    session['last_login'] = int(time.time())
                    return redirect(url_for('dashboard'))
            except Exception:
                pass
        time.sleep(1)  # simple slowdown to deter brute-force
        return "<p>Login failed. <a href='/login'>Try again</a></p>"
    return render_template_string(LOGIN)

@app.route('/dashboard')
def dashboard():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('login'))
    db = get_db()
    row = db.execute("SELECT username, fullname, email FROM users WHERE id = ?", (uid,)).fetchone()
    if not row:
        session.clear()
        return redirect(url_for('login'))
    user = {"username": row[0], "fullname": row[1], "email": row[2]}
    return render_template_string(HOME, user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
