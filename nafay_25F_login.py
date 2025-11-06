from flask import Flask, request, render_template_string
import pickle
import base64

app = Flask(__name__)

PAGE = """
<!doctype html>
<title>Insecure Deserialization</title>
<h2>Upload base64 pickle to load</h2>
<form method="post" action="/load">
  Base64 Pickle: <textarea name="p" rows="6" cols="60"></textarea><br>
  <button type="submit">Load</button>
</form>
<p style="color:gray">DEMO ONLY — do not run on public servers</p>
"""

RESULT = """
<h3>Output</h3>
<pre>{{out}}</pre>
<p><a href="/">Back</a></p>
"""

@app.route('/')
def index():
    return render_template_string(PAGE)

@app.route('/load', methods=['POST'])
def load():
    b64 = request.form.get('p','').strip()
    try:
        data = base64.b64decode(b64)
        obj = pickle.loads(data)  # insecure
        out = repr(obj)
    except Exception as e:
        out = f"Error: {e}"
    return render_template_string(RESULT, out=out)

if __name__ == '__main__':
    app.run(debug=True)
