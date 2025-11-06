# secure_comment_app.py
# Secure comment board demo (Flask) - local lab
# Features: input length limits, auto-escaped templates, simple rate limiter per-session
from flask import Flask, request, render_template_string, session, redirect, url_for
from markupsafe import escape
import time

app = Flask(__name__)
app.secret_key = "change-this-secret"
COMMENTS = []
MAX_COMMENT_LEN = 400
POST_INTERVAL = 2  # seconds between posts per-session

PAGE = """<!doctype html>
<title>Secure Comment Board</title>
<h2>Secure Comment Board</h2>
<form method="post">
  Name: <input name="name"><br>
  Comment: <br><textarea name="comment" rows="4" cols="60"></textarea><br>
  <button type="submit">Post</button>
</form>
<hr>
<h3>Comments</h3>
{% for nm, cm, t in comments %}
  <div><strong>{{ nm }}</strong> <small>({{ t }})</small>:<div>{{ cm }}</div></div><hr>
{% else %}
  <div>No comments yet.</div>
{% endfor %}
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    now = int(time.time())
    if 'last_post' not in session:
        session['last_post'] = 0
    if request.method == 'POST':
        # basic rate limiting per-session
        if now - session.get('last_post', 0) < POST_INTERVAL:
            return "Posting too fast. Wait a moment.", 429
        name = request.form.get('name','').strip() or "Anon"
        comment = request.form.get('comment','').strip()
        if not comment:
            return "Comment cannot be empty.", 400
        if len(comment) > MAX_COMMENT_LEN:
            return f"Comment too long. Max {MAX_COMMENT_LEN} characters.", 400
        safe_name = escape(name)
        safe_comment = escape(comment)
        COMMENTS.append((safe_name, safe_comment, time.strftime('%Y-%m-%d %H:%M:%S')))
        session['last_post'] = now
        return redirect(url_for('home'))
    return render_template_string(PAGE, comments=list(reversed(COMMENTS)))

if __name__ == '__main__':
    app.run(port=5020, debug=True)
