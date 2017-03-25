from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os, json
import wikiprereq_finder

app = Flask(__name__)
app.secret_key = 'This is a top secret key'
app.config['UPLOAD_FOLDER'] = '.'
ALLOWED_EXTENSIONS = set(['pdf'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def showIndex():
    if request.method == 'GET':
        return render_template('index.html')
    else: ## if request method = post
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        f = request.files['file']
        # if user does not select file, browser submit a empty part without filename
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nodes = wikiprereq_finder.get_concepts(filename)
            if nodes == 0:
                return '''<h1>Error!</h1>'''
            return render_template('graph_page.html', nodes=nodes)

# api request
# @app.route('/links')
# def getSubPages():
#     page = request.args.get("page")
#     print ("This is inside getSubPages " + str(json.dumps(first_paragraph_links(page))))
#     return json.dumps(first_paragraph_links(page))

# @app.route('/graph', methods=['GET', 'POST'])
# def showGraph():
#     nodes = request.args['nodes']
#     if request.method == 'GET':

if __name__ == '__main__':
    app.run()
