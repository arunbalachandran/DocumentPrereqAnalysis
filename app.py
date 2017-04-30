# from waitress import serve
from flask import Flask, request, redirect, url_for, render_template, flash, session
from werkzeug.utils import secure_filename
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import os, json, subprocess, shlex, sys
import wikiprereq_finder
import sys
import scholar_user
import os
import amazonscraper
import urllib
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfparser import PDFDocument
app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET']
db_url = os.environ['MYSQL_DATABASE_URL'].split('//')
# db_url = os.environ['CLEARDB_DATABASE_URL'].split('//')
app.config['MYSQL_USER'] = db_url[1].split(':')[0]
app.config['MYSQL_PASSWORD'] = db_url[1].split(':')[1].split('@')[0]
app.config['MYSQL_DB'] = db_url[1].split(':')[1].split('@')[1].split('/')[1].split('?')[0]
app.config['MYSQL_HOST'] = db_url[1].split(':')[1].split('@')[1].split('/')[0]
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'docs')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
ALLOWED_EXTENSIONS = set(['pdf'])
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_credentials(emailid):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_tab  WHERE user_name = "' + emailid + '";')
    data = cursor.fetchall()
    return data

def insert_user_credentials(emailid, hashed_password):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_tab (user_name, password) VALUES ("' + emailid + '", "' + hashed_password + '");')
    conn.commit()
    print ('Added user to table.')

@app.route('/', methods=['GET'])
def show_index():
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def show_registration():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        data = request.get_json('data')
        emailid, password, password1 = data.split('&')
        if (password != password1):
            return json.dumps({'error': 'Failed to login. Passwords dont match.'}), 400, {'contentType': 'application/json;charset=UTF-8'}
        emailid, password = urllib.parse.unquote(emailid.split('=')[1]), urllib.parse.unquote(password.split('=')[1])
        hashed_password = generate_password_hash(password)
        insert_user_credentials(emailid, hashed_password)
        return json.dumps({'success': 'Successful registration.'}), 200, {'contentType': 'application/json;charset=UTF-8'}

@app.route('/signin', methods=['GET', 'POST'])
def show_signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        formdata = request.get_json('data')
        emailid, password = formdata.split('&')
        emailid, password = urllib.parse.unquote(emailid.split('=')[1]), urllib.parse.unquote(password.split('=')[1])
        data = get_user_credentials(emailid)
        if (len(data) > 0):
            if (check_password_hash(str(data[0][2]), password)):
                sys.stdout.write('The password matches correctly\n')
                session['CURRENT_USER'] = emailid
                session['CURRENT_USER_ID'] = data[0][0]
                session['CURRENT_USER_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], session['CURRENT_USER_ID'])
                return json.dumps({'success': 'Successful login'}), 200, {'contentType': 'application/json;charset=UTF-8'}
            else:
                sys.stdout.write("The password for the username doesn't match stored record\n")
            sys.stdout.flush()
        # should I close connections here?
        return json.dumps({'error': 'Failed to login'}), 400, {'contentType': 'application/json;charset=UTF-8'}

@app.route('/upload', methods=['GET', 'POST'])
def show_upload():
    if session.get('CURRENT_USER'):
        if request.method == 'GET':
            return render_template('upload.html')
        elif request.method == 'POST':
            

@app.route('/titleCheck', methods=['POST'])
def title_check():
    if session.get('CURRENT_USER'):
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part.')
                return redirect(request.url)
            f = request.files['file']
            print ('is allowed file name', allowed_file(f.filename))
            if f.filename == '' or not allowed_file(f.filename):
                return json.dumps({'error': 'Invalid file'}), 400, {'ContentType': 'application/json'}
            else:
                filename = secure_filename(f.filename)
                f.save(os.path.join(session['CURRENT_USER_FOLDER'], filename))
                fp = open(os.path.join(session['CURRENT_USER_FOLDER'], filename), 'rb')
                parser = PDFParser(fp)
                doc = PDFDocument(parser)
                parser.set_document(doc)
                doc.set_parser(parser)
                if len(doc.info) > 0:
                    if doc.info[0].get('Title'):
                        title = doc.info[0]['Title']
                        session['CURRENT_PAPER_TITLE'] = title
                    else:
                        return json.dumps({'error': 'Title not found'}), 400, {'ContentType': 'application/json'}
                else:
                    return json.dumps({'error': 'Title not found'}), 400, {'ContentType': 'application/json'}
                nodes = prereq_fetcher.get_concepts(session['CURRENT_USER_FOLDER'], filename))
                if len(nodes) == 0:
                    return json.dumps({'error': 'No concepts'}), 400, {'ContentType': 'application/json'}
                # add a central node
                add_central_node = {}
                add_central_node[filename] = nodes
                return render_template('graph_page.html', nodes=add_central_node, page_ranking=0)

@app.route('/logout', methods=['GET'])
def show_logout():
    session.pop('CURRENT_USER')
    return redirect(url_for('show_index'))

# api request
@app.route('/make_callout', methods=['POST'])
def node_clicked():
    if session.get('CURRENT_USER'):
        if request.method == 'POST':
            data = request.get_json()
            clickedNode = data["clickdata"][:-4]
            print ("The clicked node was " + str(clickedNode))
            # check if clicked node is not central node
            # if (clickedNode not in os.listdir(app.config['UPLOAD_FOLDER'])):
            scholardata = scholar_user.get_query_html(str(clickedNode))
            # amazondata = amazonscraper.get_products(str(clickedNode))
            print ('Successfully clicked the node')
            # return json.dumps({"data1": str(scholardata), "data2": str(amazondata)})
            return json.dumps({"data1": str(scholardata), "data2": 'Test Data'})
            # else:
            #     return json.dumps({'error': True}), 200, {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run()
    # print ('Port that should set is', os.environ.get('PORT'))
    # serve(app, port=os.environ.get('PORT', 8000), cleanup_interval=100)
