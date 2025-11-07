# secure_contact_validated.py
from flask import Flask, request, render_template_string, g
import sqlite3, os, time
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
DB = "contact_valid.db"
RATE_WINDOW = 60  # seconds
MAX_PER_WINDOW = 3
visits = {}  # simple in-memory rate limiter {ip: [timestamps]}

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
    return g.db

def init_db():
    if not os.path.exists(DB):
        db = sqlite3.connect(DB)
        db.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)")
        db.commit()
        db.close()

init_db()

PAGE = """
<form method="post" action="/contact">
  Name: <input name="name" maxlength="100"><br>
  Email: <input name="email" maxlength="254"><br>
  Message:<br><textarea name="message" maxlength="1000"></textarea><br>
  <button type="submit">Send</button>
</form>
"""

def allowed(ip):
    now = time.time()
    arr = visits.get(ip, [])
    arr = [t for t in arr if now - t < RATE_WINDOW]
    if len(arr) >= MAX_PER_WINDOW:
        visits[ip] = arr
        return False
    arr.append(now)
    visits[ip] = arr
    return True

@app.route('/')
def index():
    return render_template_string(PAGE)

@app.route('/contact', methods=['POST'])
def contact():
    ip = request.remote_addr or 'unknown'
    if not allowed(ip):
        return "<p>Rate limit exceeded. Try later.</p>"
    name = request.form.get('name','').strip()[:100]
    email = request.form.get('email','').strip()[:254]
    message = request.form.get('message','').strip()[:1000]
    if not name or not email or not message:
        return "<p>All fields required. <a href='/'>Back</a></p>"
    try:
        validate_email(email)
    except EmailNotValidError:
        return "<p>Invalid email. <a href='/'>Back</a></p>"
    db = get_db()
    db.execute("INSERT INTO messages (name,email,message) VALUES (?, ?, ?)", (name, email, message))
    db.commit()
    return "<p>Message received. <a href='/'>Back</a></p>"

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

if __name__=='__main__':
    app.run(debug=True)
