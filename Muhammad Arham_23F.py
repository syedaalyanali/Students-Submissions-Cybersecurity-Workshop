# vuln_comments_xss.py
# Vulnerable comment board (Stored XSS) — LOCAL LAB ONLY
from flask import Flask, request, render_template_string

app = Flask(__name__)
comments = []

PAGE = """<!doctype html>
<title>Vulnerable Comments (Stored XSS)</title>
<h2>Comment Board (Vulnerable)</h2>
<form method="post">
  Name: <input name="name"><br>
  Comment: <input name="comment"><br>
  <button type="submit">Post</button>
</form>
<hr>
<h3>Comments</h3>
{% for nm, cm in comments %}
  <!-- VULNERABLE: rendering raw comment text without escaping -->
  <div><strong>{{ nm }}</strong>: {{ cm | safe }}</div>
{% else %}
  <div>No comments yet.</div>
{% endfor %}
"""

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        nm = request.form.get('name','').strip()
        cm = request.form.get('comment','').strip()
        comments.append((nm or "Anon", cm))
    return render_template_string(PAGE, comments=comments)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
