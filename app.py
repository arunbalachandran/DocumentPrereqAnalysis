from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import os, json, subprocess, shlex, sys
import wikiprereq_finder
import sys
import scholar_user
# from pathlib import Path
# path_var = Path('.')
app = Flask(__name__)
app.secret_key = 'This is a very very top secret key.'
# app.config['UPLOAD_FOLDER'] = '.'
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
            # upload_path = path_var/app.config['UPLOAD_FOLDER']/filename
            # upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            upload_path = filename
            # if (upload_path.exists()):
            if (1):
                # resolved_path = upload_path.resolve()
                # print ('resolved_path is', resolved_path)
                # with upload_path.open(mode='wb') as fp:
                #     f.save(fp)
                f.save(upload_path)
                nodes = wikiprereq_finder.get_concepts(upload_path)
                # nodes = wikiprereq_finder.get_concepts(upload_path.resolve())
                if len(nodes) == 0:
                    flash("Sorry but the system couldn't find any concepts in the document.")
                    return redirect(request.url)
                print ('nodes are ', nodes)
                return render_template('graph_page.html', nodes=nodes)

# api request
@app.route('/make_callout', methods=['POST'])
def node_clicked():
    if request.method == 'POST':
        data = request.get_json()
        clickedNode = data["clickdata"]
        print ("Clicked node was " + str(clickedNode))
        output = scholar_user.get_query_html(str(clickedNode))
        return json.dumps({"data": str(output)})

if __name__ == '__main__':
    app.run()
