# vuln_profile_idor.py
# IDOR (Insecure Direct Object Reference) demo - Flask (local lab only)
from flask import Flask, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "demo-secret"

# Simple "database" of profiles
profiles = {
    "1": {"name": "Ayesha", "email": "ayesha@example.com"},
    "2": {"name": "Bilal", "email": "bilal@example.com"},
    "3": {"name": "Chen", "email": "chen@example.com"}
}

# Simple login for demo (no DB)
users = {"user1": "1", "user2": "2"}  # username -> profile id

LOGIN_PAGE = '''
<h2>Login (demo)</h2>
<form method="post" action="/login">
  Username: <input name="username"><br>
  <button type="submit">Login</button>
</form>
<p>Demo users: user1, user2</p>
'''

@app.route('/', methods=['GET'])
def index():
    if 'uid' in session:
        return f"Logged in as {session.get('user')} - <a href='/profile?id={session.get('uid')}'>My Profile</a> | <a href='/logout'>Logout</a>"
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username','').strip()
    if username in users:
        session['user'] = username
        session['uid'] = users[username]
        return redirect(url_for('index'))
    return "Unknown user. Use user1 or user2. <a href='/'>Back</a>"

@app.route('/profile')
def profile():
    # VULNERABLE: trusts client-supplied 'id' parameter without authorization check
    pid = request.args.get('id','')
    if pid in profiles:
        p = profiles[pid]
        return f"<h3>Profile {pid}</h3>Name: {p['name']}<br>Email: {p['email']}<br><a href='/'>Home</a>"
    return "Profile not found. <a href='/'>Home</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5010, debug=True)
