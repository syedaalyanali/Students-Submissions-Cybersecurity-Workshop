from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/')
def index():
    return "<p>Demo: try /debug or /env</p>"

@app.route('/debug')
def debug():
    1/0  # cause an error that shows debug trace if app is in debug mode
    return "ok"

@app.route('/env')
def env():
    # purposely return environment-like info (simulated)
    return {
        "SECRET_KEY": app.secret_key,
        "DB_PATH": "/var/data/prod.db",
        "ADMIN_EMAIL": "admin@example.com"
    }

if __name__ == '__main__':
    app.run(debug=True)
