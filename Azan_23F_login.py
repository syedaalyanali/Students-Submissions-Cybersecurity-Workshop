# safe_fetch_whitelist.py
from flask import Flask, request, render_template_string
import requests
from urllib.parse import urlparse

app = Flask(__name__)
WHITELIST = {"example.com", "httpbin.org", "api.github.com"}

PAGE = """
<form method="get" action="/fetch">
  URL to fetch (whitelisted hosts only): <input name="url" size="60"><br>
  <button type="submit">Fetch</button>
</form>
"""

RESULT = """
<h3>Result (first 800 chars)</h3>
<pre>{{content}}</pre>
<p><a href="/">Back</a></p>
"""

@app.route('/')
def index():
    return render_template_string(PAGE)

@app.route('/fetch')
def fetch():
    url = request.args.get('url','').strip()
    if not url:
        return "<p>No URL provided. <a href='/'>Back</a></p>"
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname or hostname.lower() not in WHITELIST:
        return "<p>Host not allowed. Only approved hosts permitted.</p>"
    try:
        r = requests.get(url, timeout=4)
        content = r.text[:800]
    except Exception as e:
        content = f"Error: {e}"
    return render_template_string(RESULT, content=content)

if __name__=='__main__':
    app.run(debug=True)
