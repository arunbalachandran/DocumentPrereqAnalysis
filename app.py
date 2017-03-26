from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import os, json, subprocess, shlex, sys
import wikiprereq_finder
import sys

app = Flask(__name__)
app.secret_key = 'This is a very very top secret key.'
app.config['UPLOAD_FOLDER'] = 'docs'
ALLOWED_EXTENSIONS = set(['pdf'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def showIndex():
    if request.method == 'GET':
        return render_template('index.html')
    else: ## if request method = post
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '' or not allowed_file(f.filename):
            flash("Invalid file or none selected! Please select a file or check if the file is a 'pdf' before pressing the submit button.")
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            nodes = wikiprereq_finder.get_concepts(filepath)
            if len(nodes) == 0:
                flash("Sorry but the system couldn't find any concepts in the document.")
                return redirect(request.url)
            return render_template('graph_page.html', nodes=nodes)

# api request
@app.route('/make_callout', methods=['POST'])
def node_clicked():
    if request.method == 'POST':
        data = request.get_json()
        clickedNode = data["clickdata"]
        print ("Clicked node was " + str(clickedNode))
        cmd = "python scholar.py -A '" + clickedNode + "'  -c 100 --after=1970"
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        sys.stdout.write('\noutput is ' + str(output) + '\n ')
        return json.dumps({"data": str(output)})

if __name__ == '__main__':
    app.run()
