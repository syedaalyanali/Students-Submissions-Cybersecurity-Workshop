from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

PAGE = """
<!doctype html>
<title>SSRF Demo</title>
<h2>SSRF Demo</h2>
<form method="get" action="/fetch">
  URL to fetch: <input name="url"><br>
  <button type="submit">Fetch</button>
</form>
<p style="color:gray">Local lab only</p>
"""

RESULT = """
<h3>Fetched content (first 500 chars)</h3>
<pre>{{content}}</pre>
<p><a href="/">Back</a></p>
"""

@app.route('/')
def index():
    return render_template_string(PAGE)

@app.route('/fetch')
def fetch():
    url = request.args.get('url','').strip()
    try:
        r = requests.get(url, timeout=3)
        text = r.text[:500]
    except Exception as e:
        text = f"Error: {e}"
    return render_template_string(RESULT, content=text)

if __name__ == '__main__':
    app.run(debug=True)
