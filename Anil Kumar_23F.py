# phish_simulator_safe.py
from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """<!doctype html>
<title>Phishing Training (Safe)</title>
<h2>Phishing Training Page (Simulation)</h2>
<p>This is a simulated phishing email landing page for training only.</p>
<ul>
  <li>Look at the sender: <strong>workshop-news@youruniversity.edu</strong></li>
  <li>Check the URL and hover the link (locally)</li>
  <li>Look for urgency, spelling mistakes, and unexpected attachments</li>
</ul>

<p><strong>Task for students:</strong> choose the 3 indicators that show this is suspicious.</p>

<form method="post">
  <label><input type="checkbox" name="ind" value="sender"> Suspicious sender</label><br>
  <label><input type="checkbox" name="ind" value="urgency"> Urgent language</label><br>
  <label><input type="checkbox" name="ind" value="link"> Shortened/strange link</label><br>
  <label><input type="checkbox" name="ind" value="attachment"> Unexpected attachment</label><br>
  <button type="submit">Submit</button>
</form>
"""

RESULT = """<!doctype html>
<title>Result</title>
<h2>Thanks — this was a training page</h2>
<p>Good job. Remember: never enter passwords from a link; always open the site manually and enable 2FA.</p>
"""

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        return render_template_string(RESULT)
    return render_template_string(PAGE)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
