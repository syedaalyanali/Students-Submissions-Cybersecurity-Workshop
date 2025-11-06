from flask import Flask, request, render_template_string, g
import sqlite3
import os
from markupsafe import escape

app = Flask(__name__)
DB = "secure_contact.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def init_db():
    need_seed = not os.path.exists(DB)
    db = sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)')
    db.commit()
    db.close()

init_db()

PAGE = """
<!doctype html>
<title>Secure Contact</title>
<h2>Secure Contact Form</h2>
<form method="post" action="/contact">
  Name: <input name="name" maxlength="100"><br>
  Email: <input name="email" maxlength="254"><br>
  Message:<br>
  <textarea name="message" rows="5" cols="40" maxlength="1000"></textarea><br>
  <button type="submit">Send</button>
</form>
<h3>Recent messages</h3>
<ul>
  {% for c in contacts %}
    <li><strong>{{ c[1] }}</strong> ({{ c[2] }}) — {{ c[3] }}</li>
  {% endfor %}
</ul>
<p style="color:gray">Secure demo — local use</p>
"""

@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; object-src 'none'"
    return response

@app.route('/')
def index():
    db = get_db()
    rows = db.execute("SELECT id, name, email, message FROM contacts ORDER BY id DESC LIMIT 10").fetchall()
    safe_rows = [(r[0], escape(r[1]), escape(r[2]), escape(r[3])) for r in rows]
    return render_template_string(PAGE, contacts=safe_rows)

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '').strip()[:100]
    email = request.form.get('email', '').strip()[:254]
    message = request.form.get('message', '').strip()[:1000]
    if not name or not email or not message:
        return "<p>All fields are required. <a href='/'>Back</a></p>"
    db = get_db()
    db.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    db.commit()
    return "<p>Message received. <a href='/'>Back</a></p>"

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
