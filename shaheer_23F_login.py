from flask import Flask, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "demo-csrf-key"

USERS = {"alice": "alice@example.com"}
PASSWORDS = {"alice": "initial"}

LOGIN = """
<form method="post" action="/login">
  Username: <input name="username"><br>
  <button type="submit">Login</button>
</form>
"""

CHANGE = """
<h3>Password Change (vulnerable to CSRF)</h3>
<form method="post" action="/change">
  New Password: <input name="newpass"><br>
  <button type="submit">Change</button>
</form>
<p>Logged in as: {{user}}</p>
"""

@app.route('/', methods=['GET'])
def index():
    if 'user' in session:
        return render_template_string(CHANGE, user=session['user'])
    return render_template_string(LOGIN)

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username','').strip()
    if u in USERS:
        session['user'] = u
        return redirect(url_for('index'))
    return "Unknown user", 400

@app.route('/change', methods=['POST'])
def change():
    if 'user' not in session:
        return "Not logged in", 403
    new = request.form.get('newpass','')
    PASSWORDS[session['user']] = new
    return f"Password changed for {session['user']}."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
