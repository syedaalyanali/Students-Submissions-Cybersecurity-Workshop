from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

PAGE = """
<!doctype html>
<title>Open Redirect Demo</title>
<h2>Open Redirect Demo</h2>
<form method="get" action="/go">
  Redirect to URL: <input name="next"><br>
  <button type="submit">Go</button>
</form>
"""

@app.route('/')
def index():
    return render_template_string(PAGE)

@app.route('/go')
def go():
    target = request.args.get('next','')
    if not target:
        return "<p>No target specified. <a href='/'>Back</a></p>"
    return redirect(target)

if __name__ == '__main__':
    app.run(debug=True)
