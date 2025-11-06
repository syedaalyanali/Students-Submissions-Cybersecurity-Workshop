# secure_dashboard.py

from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3, os, bcrypt

app = Flask(__name__)
app.secret_key = 'change-this-to-a-random-secret'  
DB = "secure_demo.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash BLOB)")
        # seed hashed user ('demo' / 'Demo@123')
        pw = bcrypt.hashpw(b"Demo@123", bcrypt.gensalt())
        c.execute("INSERT INTO users (username,password_hash) VALUES (?,?)", ("demo", pw))
        conn.commit()
        conn.close()

init_db()

LOGIN_PAGE = """<!doctype html>
<title>Secure Login</title>
<h2>Secure Login (demo)</h2>
<form method="post" action="/login">
  Username: <input name="username"><br>
  Password: <input type="password" name="password"><br>
  <button type="submit">Login</button>
</form>
"""

DASHBOARD = """<!doctype html>
<title>Dashboard</title>
<h2>Welcome {{user}}</h2>
<p>This is your dashboard. Server uses sessions and safe DB access.</p>
<a href="/logout">Logout</a>
"""

@app.route('/')
def index():
    if 'user' in session:
        return render_template_string(DASHBOARD, user=session['user'])
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username','')
    password = request.form.get('password','').encode('utf-8')

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password, row[0]):
        session['user'] = username
        return redirect(url_for('index'))
    return "<p>Invalid credentials.</p><p><a href='/'>Try again</a></p>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5003, debug=True)
