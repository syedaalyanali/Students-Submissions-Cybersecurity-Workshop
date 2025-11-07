# secure_profile_viewer_auth.py
from flask import Flask, request, session, redirect, url_for, render_template_string, g
import sqlite3, os, bcrypt

app = Flask(__name__)
app.secret_key = "replace-with-secure-random"
DB = "profiles.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
    return g.db

def init_db():
    if not os.path.exists(DB):
        db = sqlite3.connect(DB)
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash BLOB, fullname TEXT, email TEXT)")
        pw = bcrypt.hashpw("Demo123!".encode('utf-8'), bcrypt.gensalt())
        db.execute("INSERT INTO users (username, password_hash, fullname, email) VALUES (?, ?, ?, ?)",
                   ("user1", pw, "User One", "one@example.com"))
        db.commit()
        db.close()

init_db()

HOME = """
<!doctype html><title>Profile Viewer</title>
{% if user %}
  <h2>Profile</h2>
  <p>Name: {{ user['fullname'] }}</p>
  <p>Email: {{ user['email'] }}</p>
  <p><a href="/logout">Logout</a></p>
{% else %}
  <p><a href="/login">Login</a></p>
{% endif %}
"""

LOGIN = """
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
"""

@app.route('/')
def index():
    uid = session.get('user_id')
    user = None
    if uid:
        row = get_db().execute("SELECT fullname,email FROM users WHERE id = ?", (uid,)).fetchone()
        if row:
            user = {"fullname": row[0], "email": row[1]}
    return render_template_string(HOME, user=user)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','')
        row = get_db().execute("SELECT id,password_hash FROM users WHERE username = ?", (u,)).fetchone()
        if row and bcrypt.checkpw(p.encode('utf-8'), row[1]):
            session['user_id'] = row[0]
            return redirect(url_for('index'))
        return "<p>Login failed. <a href='/login'>Back</a></p>"
    return render_template_string(LOGIN)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

if __name__=='__main__':
    app.run(debug=True)
