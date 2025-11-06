# secure_file_upload.py
# Secure file upload example - Flask (local)
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED = {'txt', 'pdf', 'png', 'jpg'}

PAGE = '''
<h2>Secure File Upload</h2>
<form method="post" enctype="multipart/form-data">
  File: <input type="file" name="file"><button type="submit">Upload</button>
</form>
<ul>
{% for f in files %}
  <li>{{ f }}</li>
{% endfor %}
</ul>
'''

@app.route('/', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            return "No file", 400
        filename = secure_filename(f.filename)
        ext = filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED:
            return "Disallowed file type", 400
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)
        return redirect(url_for('upload'))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(PAGE, files=files)

if __name__ == '__main__':
    app.run(port=5013, debug=True)
