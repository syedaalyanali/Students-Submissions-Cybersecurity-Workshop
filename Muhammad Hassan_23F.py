# vuln_cmd_injection.py
# Command injection demo - Flask (local lab only)
from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

PAGE = '''
<h2>Ping Host (Command Injection Demo)</h2>
<form method="post">
  Host: <input name="host"><button type="submit">Ping</button>
</form>
<pre>{{ output }}</pre>
'''

@app.route('/', methods=['GET','POST'])
def home():
    output = ''
    if request.method == 'POST':
        host = request.form.get('host','').strip()
        # VULNERABLE: passing user input to shell command unsafely
        try:
            # WARNING: intentionally unsafe for demo only.
            output = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        except Exception as e:
            output = str(e)
    return render_template_string(PAGE, output=output)

if __name__ == '__main__':
    app.run(port=5012, debug=True)
