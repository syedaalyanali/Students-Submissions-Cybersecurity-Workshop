# vuln_login_sqli.py
# Vulnerable login demo (SQL Injection) — LOCAL LAB ONLY
from flask import Flask, request, render_template_string
import sqlite3, os

app = Flask(__name__)
DB = "vuln_login.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        c.execute("INSERT INTO users (username,password) VALUES ('alice','alicepass')")
        c.execute("INSERT INTO users (username,password) VALUES ('bob','bobpass')")
        conn.commit()
        conn.close()

init_db()

LOGIN_HTML = """<!doctype html>
<title>Vuln Login (SQLi)</title>
<h2>Vulnerable Login (SQLi Demo)</h2>
<form method="post" action="/login">
  Username: <input name="username"><br>
  Password: <input name="password"><br>
  <button type="submit">Login</button>
</form>
<p style="color:gray">Local demo only — do not deploy</p>
"""

SECRET_HTML = """<!doctype html>
<title>Secret</title>
<h2>Secret Page</h2>
<p>Welcome, {{user}} — secret area</p>
<a href="/">Back</a>
"""

@app.route('/')
def index():
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username','')
    password = request.form.get('password','')

    # VULNERABLE: building SQL with string concatenation (do NOT do this in real apps)
    query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
    print("DEBUG SQL:", query)

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute(query)   # vulnerable
        row = c.fetchone()
    except Exception as e:
        print("SQL error:", e)
        row = None
    conn.close()

    if row:
        return render_template_string(SECRET_HTML, user=username)
    return "<p>Login failed. <a href='/'>Try again</a></p>"

if __name__ == '__main__':
    app.run(debug=True)
