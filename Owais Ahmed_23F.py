# secure_login_hash.py
# Secure login demo - Flask + sqlite + bcrypt
from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3, os, bcrypt

app = Flask(__name__)
app.secret_key = "change-this-secret-2"
DB = "secure_login.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash BLOB)")
        # seed user: demo / Demo@123
        pw = bcrypt.hashpw(b"Demo@123", bcrypt.gensalt())
        c.execute("INSERT INTO users (username,password_hash) VALUES (?,?)", ("demo", pw))
        conn.commit()
        conn.close()

init_db()

LOGIN = """<h2>Secure Login</h2>
<form method="post" action="/login">
  Username: <input name="username"><br>
  Password: <input type="password" name="password"><br>
  <button type="submit">Login</button>
</form>
<p>Demo user: demo / Demo@123</p>
"""

@app.route('/')
def index():
    if 'user' in session:
        return f"Logged in as {session['user']} - <a href='/logout'>Logout</a>"
    return render_template_string(LOGIN)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username','').strip()
    password = request.form.get('password','').encode('utf-8')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Parameterized query prevents SQL injection
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password, row[0]):
        session['user'] = username
        return redirect(url_for('index'))
    return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5021, debug=True)
