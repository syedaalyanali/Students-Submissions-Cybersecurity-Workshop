from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "vuln_login.db"

# --- Setup/demo DB: create table and one user ---
def init_db():
    need_seed = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    if need_seed:
        # NOTE: passwords stored in plaintext here for demo only (DON'T do this in real apps)
        c.execute("INSERT INTO users (username, password) VALUES ('alice', 'alicepass')")
        c.execute("INSERT INTO users (username, password) VALUES ('bob', 'bobpass')")
    conn.commit()
    conn.close()

init_db()

# --- Template strings (very small) ---
LOGIN_PAGE = """
<!doctype html>
<title>Vulnerable Login (SQLi)</title>
<h2>Vulnerable Login (SQLi Demo)</h2>
<form method="post" action="/login">
  Username: <input name="username"><br>
  Password: <input name="password"><br>
  <button type="submit">Login</button>
</form>
<p style="color:gray">Demo only - local use</p>
"""

SECRET_PAGE = """
<!doctype html>
<title>Secret</title>
<h2>Secret Page</h2>
<p>Welcome, {{user}}! You reached the secret area.</p>
<p><a href="/">Back</a></p>
"""

# --- Routes ---
@app.route('/')
def index():
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')


    query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
    print("DEBUG - Executing SQL:", query)  # show executed query in console for teaching

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(query)   # <-- vulnerable: string-built SQL executed directly
        row = c.fetchone()
    except Exception as e:
        # show error in console (teaching only)
        print("SQL error:", e)
        row = None
    conn.close()

    if row:
        # login "successful"
        return render_template_string(SECRET_PAGE, user=username)
    else:
        return "<p>Login failed. <a href='/'>Try again</a></p>"

if __name__ == '__main__':
    # run on localhost for demo
    app.run(debug=True)
