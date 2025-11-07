# secure_login_dashboard.py
from flask import Flask, request, redirect, url_for, render_template_string, session, g
import sqlite3
import os
import bcrypt
import time

app = Flask(__name__)
app.secret_key = "replace-with-secure-random-key"
DB = "secure_login.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db():
    if not os.path.exists(DB):
        db = sqlite3.connect(DB)
        db.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash BLOB, fullname TEXT)')
        pw = bcrypt.hashpw("DemoPass1!".encode('utf-8'), bcrypt.gensalt())
        db.execute("INSERT INTO users (username, password_hash, fullname) VALUES (?, ?, ?)",
                   ("alice", pw, "Alice Demo"))
        db.commit()
        db.close()

init_db()

HOME = """
<!doctype html><title>Secure Dashboard</title>
{% if user %}
  <h2>Welcome {{ user['fullname'] }}</h2>
  <p>Your username: {{ user['username'] }}</p>
  <p><a href="/logout">Logout</a></p>
{% else %}
  <p><a href="/login">Login</a> | <a href="/signup">Sign up</a></p>
{% endif %}
"""

LOGIN = """
<!doctype html><title>Login</title>
<h2>Login</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
<p><a href="/">Home</a></p>
"""

SIGNUP = """
<!doctype html><title>Sign Up</title>
<h2>Sign Up</h2>
<form method="post">
  Username: <input name="username"><br>
  Full name: <input name="fullname"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Create</button>
</form>
<p><a href="/">Home</a></p>
"""

@app.route('/')
def index():
    uid = session.get('user_id')
    user = None
    if uid:
        row = get_db().execute("SELECT username, fullname FROM users WHERE id = ?", (uid,)).fetchone()
        if row:
            user = {"username": row[0], "fullname": row[1]}
    return render_template_string(HOME, user=user)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        fullname = request.form.get('fullname','').strip()
        password = request.form.get('password','')
        if not username or not password:
            return "<p>Missing fields. <a href='/signup'>Back</a></p>"
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            get_db().execute("INSERT INTO users (username, password_hash, fullname) VALUES (?, ?, ?)",
                             (username, pw_hash, fullname))
            get_db().commit()
        except Exception:
            return "<p>Username taken or error. <a href='/signup'>Back</a></p>"
        return redirect(url_for('login'))
    return render_template_string(SIGNUP)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        row = get_db().execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if row and bcrypt.checkpw(password.encode('utf-8'), row[1]):
            session['user_id'] = row[0]
            session['last_login'] = int(time.time())
            return redirect(url_for('index'))
        # generic response to avoid enumeration
        return "<p>Login failed. <a href='/login'>Try again</a></p>"
    return render_template_string(LOGIN)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

if __name__ == '__main__':
    app.run(debug=True)
