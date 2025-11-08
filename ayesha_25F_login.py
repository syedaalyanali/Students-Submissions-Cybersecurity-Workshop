from flask import Flask, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "dev-secret-key"

profiles = {
    "1": {"name": "Alice", "email": "alice@example.com"},
    "2": {"name": "Bob", "email": "bob@example.com"},
    "3": {"name": "Charlie", "email": "charlie@example.com"}
}

credentials = {
    "alice": "alicepass",
    "bob": "bobpass",
    "charlie": "charliepass"
}

LOGIN_PAGE = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post" action="/login">
  Username: <input name="username"><br>
  Password: <input name="password"><br>
  <button type="submit">Login</button>
</form>
<p><a href="/profile">Go to profile</a></p>
"""

PROFILE_PAGE = """
<!doctype html>
<title>Profile</title>
<h2>Profile Viewer</h2>
{% if user %}
  <p>Viewing profile of: <strong>{{ user['name'] }}</strong></p>
  <p>Email: {{ user['email'] }}</p>
{% else %}
  <p>No profile found.</p>
{% endif %}
<p>Logged in as: {{ logged_in }}</p>
<p>To view another profile change the URL parameter `?id=` (e.g. /profile?id=2)</p>
<p><a href="/logout">Logout</a></p>
"""

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        if credentials.get(u) == p:
            if u == 'alice':
                session['user_id'] = '1'
            elif u == 'bob':
                session['user_id'] = '2'
            elif u == 'charlie':
                session['user_id'] = '3'
            return redirect(url_for('profile'))
        return "<p>Login failed. <a href='/login'>Try again</a></p>"
    return render_template_string(LOGIN_PAGE)

@app.route('/profile')
def profile():
    logged_in = session.get('user_id', 'None')
    req_id = request.args.get('id')
    # Vulnerable behavior: trust client-supplied id and show that profile without authorization checks
    show_id = req_id if req_id else logged_in
    user = profiles.get(show_id)
    return render_template_string(PROFILE_PAGE, user=user, logged_in=logged_in)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
