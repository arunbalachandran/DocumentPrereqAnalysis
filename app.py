from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import os, json, subprocess, shlex, sys
import wikiprereq_finder
import sys
import scholar_user
import os
import amazonscraper
# from pathlib import Path
# path_var = Path('.')
app = Flask(__name__)
app.secret_key = 'This is a very very top secret key.'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'docs')
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
        else:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print ('save should be successful')
            nodes = wikiprereq_finder.get_concepts(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if len(nodes) == 0:
                flash("Sorry but the system couldn't find any concepts in the document.")
                return redirect(request.url)
            print ('nodes are ', nodes)
            # add a central node
            add_central_node = {}
            add_central_node[filename] = nodes
            return render_template('graph_page.html', nodes=add_central_node)

# api request
@app.route('/make_callout', methods=['POST'])
def node_clicked():
    if request.method == 'POST':
        data = request.get_json()
        clickedNode = data["clickdata"]
        print ("Clicked node was " + str(clickedNode))
        # check if clicked node is not central node
        if (clickedNode not in os.listdir(app.config['UPLOAD_FOLDER'])):
            scholardata = scholar_user.get_query_html(str(clickedNode))
            amazondata = amazonscraper.get_products(str(clickedNode))
            print ('Successfully clicked node')
            return json.dumps({"data1": str(scholardata), "data2": str(amazondata)})
        else:
            return json.dumps({'error': True}), 200, {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run()
