# secure_comments_safe.py
from flask import Flask, request, render_template_string, g
import sqlite3, os
from markupsafe import escape

app = Flask(__name__)
DB = "safe_comments.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
    return g.db

def init_db():
    if not os.path.exists(DB):
        db = sqlite3.connect(DB)
        db.execute("CREATE TABLE comments (id INTEGER PRIMARY KEY, author TEXT, message TEXT)")
        db.commit()
        db.close()

init_db()

PAGE = """
<!doctype html><title>Comments (Safe)</title>
<h2>Comments</h2>
<form method="post" action="/post">
  Name: <input name="author" maxlength="50"><br>
  Message:<br>
  <textarea name="message" rows="4" cols="50" maxlength="500"></textarea><br>
  <button type="submit">Post</button>
</form>
<ul>
  {% for a,m in comments %}
    <li><strong>{{ a }}</strong>: {{ m }}</li>
  {% endfor %}
</ul>
"""

@app.after_request
def set_csp(resp):
    resp.headers['Content-Security-Policy'] = "default-src 'self';"
    return resp

@app.route('/')
def index():
    rows = get_db().execute("SELECT author, message FROM comments ORDER BY id DESC LIMIT 50").fetchall()
    # Jinja auto-escapes, so raw HTML won't execute
    return render_template_string(PAGE, comments=rows)

@app.route('/post', methods=['POST'])
def post():
    author = request.form.get('author','').strip()[:50]
    message = request.form.get('message','').strip()[:500]
    if not author or not message:
        return "<p>All fields required. <a href='/'>Back</a></p>"
    db = get_db()
    db.execute("INSERT INTO comments (author, message) VALUES (?, ?)", (author, message))
    db.commit()
    return ("<p>Posted. <a href='/'>Back</a></p>")

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

if __name__ == '__main__':
    app.run(debug=True)
