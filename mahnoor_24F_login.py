from flask import Flask, request, render_template_string

app = Flask(__name__)
comments = []

PAGE = """
<!doctype html>
<title>Vulnerable Comments (XSS)</title>
<h2>Vulnerable Comments (Stored XSS Demo)</h2>
<form method="post" action="/post">
  <textarea name="comment" rows="3" cols="40" placeholder="Add comment"></textarea><br>
  <button type="submit">Post Comment</button>
</form>
<h3>Comments</h3>
<ul>
  {% for c in comments %}
    <li>{{ c|safe }}</li>
  {% endfor %}
</ul>
<p style="color:gray">Demo only - local use</p>
"""

@app.route('/')
def index():
    return render_template_string(PAGE, comments=comments)

@app.route('/post', methods=['POST'])
def post():
    comment = request.form.get('comment', '')
    if comment:
        comments.append(comment)
    return render_template_string(PAGE, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
