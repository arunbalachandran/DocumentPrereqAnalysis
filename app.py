# from waitress import serve
from flask import Flask, request, redirect, url_for, render_template, flash, session, send_file
from werkzeug.utils import secure_filename
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import os, json, subprocess, shlex, sys
import prereq_fetcher
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
app.config['GOOGLE_KEY'] = os.environ.get('GOOGLE_KEY')
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

def insert_paper_rating(data):
    conn = mysql.connection
    cursor = conn.cursor()
    query = 'SELECT paper_id, paper_title, rating, paper_user_rated_count, paper_rating_sum FROM paper_rating WHERE paper_title=%s'
    cursor.execute(query, (session['CURRENT_PAPER_TITLE'],))
    paper_rating = 0
    if cursor.rowcount > 0:  # if there is data
        cdata = cursor.fetchall()
        paper_rating = float((cdata[0][4] + int(data['value'])) / (cdata[0][3] + 1))
        paper_users_rated = cdata[0][3] + 1
        query_update = 'UPDATE paper_rating SET rating = %s, paper_user_rated_count = %s, paper_rating_sum = %s WHERE paper_id = %s'
        cursor.execute(query_update,(paper_rating, paper_users_rated, (cdata[0][4] + int(data['value'])), cdata[0][0],))
        conn.commit()
    else:  # paper not found for rating
        print ('Data not found......')
        # insert new record here.
        query_insert_first_rate = 'INSERT INTO paper_rating (paper_title, rating, paper_user_rated_count, paper_rating_sum) values (%s, %s, %s, %s)'
        cursor.execute(query_insert_first_rate, (session['CURRENT_PAPER_TITLE'], data['value'], 1, data['value'], ))
        conn.commit()
    return paper_rating

def get_paper_rating():
    conn = mysql.connection
    cursor = conn.cursor()
    query = 'SELECT paper_id, paper_title, rating, paper_user_rated_count, paper_rating_sum FROM paper_rating WHERE paper_title=%s'
    cursor.execute(query, (session['CURRENT_PAPER_TITLE'],))
    paper_rating = 0
    if cursor.rowcount > 0:  # if there is data
        cdata = cursor.fetchall()
        paper_rating = cdata[0][2]
    return paper_rating

def check_file_exists():
    conn = mysql.connection
    cursor = conn.cursor()
    query = 'SELECT user_id, paper_title FROM pdf_user_trace WHERE user_id=%s AND paper_title=%s'
    cursor.execute(query, (session['CURRENT_USER_ID'], session['CURRENT_PAPER_TITLE'], ))
    if cursor.rowcount == 0:
        query_insert = 'INSERT INTO pdf_user_trace (user_id, paper_abstract, paper_path, paper_title, paper_prerequisite) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query_insert, (session['CURRENT_USER_ID'], session['CURRENT_PAPER_ABSTRACT'], str(session['CURRENT_PAPER_PATH']), session['CURRENT_PAPER_TITLE'], json.dumps(session['CURRENT_PAPER_NODES']),))
        conn.commit()

def populate_library():
    conn = mysql.connection
    cursor = conn.cursor()
    query = 'SELECT user_id, paper_abstract, paper_path, paper_title, paper_prerequisite FROM pdf_user_trace WHERE user_id=%s'
    cursor.execute(query, (session['CURRENT_USER_ID'],))
    data = cursor.fetchall()
    return data

def get_path_from_title(temp_title):
    conn = mysql.connection
    cursor = conn.cursor()
    query = 'SELECT paper_path FROM pdf_user_trace WHERE paper_title=%s AND user_id=%s'
    cursor.execute(query, (temp_title, session['CURRENT_USER_ID']))
    data = cursor.fetchall()[0][0]
    return data


def get_abstract_nodes_from_title():
    conn = mysql.connection
    cursor = conn.cursor()
    query = 'SELECT paper_abstract, paper_prerequisite FROM pdf_user_trace WHERE paper_title=%s AND user_id=%s'
    cursor.execute(query, (session['CURRENT_PAPER_TITLE'], session['CURRENT_USER_ID']))
    data = cursor.fetchall()
    abstract, prereq = data[0][0], data[0][1]
    return (abstract, prereq)

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
                session['CURRENT_USER_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], session['CURRENT_USER'])
                if not os.path.exists(session['CURRENT_USER_FOLDER']):
                    os.makedirs(session['CURRENT_USER_FOLDER'])
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
            title = request.get_json()
            title = urllib.parse.parse_qs(title)['titleText'][0]
            print ('title is', title)
            session['CURRENT_PAPER_TITLE'] = title
            return json.dumps({'success': 'Paper title received'}), 200, {'contentType': 'application/json'}
            # urllib.urlparse.parse_qs

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
                session['CURRENT_PAPER_PATH'] = os.path.join(session['CURRENT_USER_FOLDER'], filename)
                nodes, abstract = prereq_fetcher.get_concepts(os.path.join(session['CURRENT_USER_FOLDER'], filename))
                print ('Current detected nodes', nodes)
                print ('Current paper abstract is', abstract)
                session['CURRENT_PAPER_ABSTRACT'] = abstract
                if len(nodes) == 0:
                    return json.dumps({'error': 'No concepts'}), 400, {'ContentType': 'application/json'}
                    # add a central node
                add_central_node = {}
                add_central_node[filename[:-4]] = nodes
                session['CURRENT_PAPER_NODES'] = add_central_node
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
                return json.dumps({'success': 'Successful check for title existence'}), 200, {'ContentType': 'application/json'}

@app.route('/userHome', methods=['GET', 'POST'])
def show_home():
    if session.get('CURRENT_USER'):
        if request.method == 'GET':
            current_paper_rating = get_paper_rating()
            check_file_exists()
            return render_template('graph_page.html', nodes=session['CURRENT_PAPER_NODES'], googlecx=app.config['GOOGLE_KEY'], paper_rating=current_paper_rating)

@app.route('/userLibrary', methods=['GET'])
def show_library():
    if session.get('CURRENT_USER'):
        if request.method == 'GET':
            data = populate_library()
            return render_template('userlibrary.html', dataset=enumerate(data))

@app.route('/viewPdf', methods=['GET', 'POST'])
def show_pdf():
    if session.get('CURRENT_USER'):
        if request.method == 'GET':
            show_path = get_path_from_title(session['SHOW_PDF'])
            # filename = os.path.basename(show_path)
            return send_file(show_path)
            # return render_template('viewpdf.html')
            # with open(show_path, 'rb') as static_file:
            #     return send_file(show_path)
        if request.method == 'POST':
            data = request.get_json()
            print ('data received is', data)
            session['SHOW_PDF'] = data
            return json.dumps({'success': 'Got file data'}), 200, {'contentType': 'application/json'}
            # return render_template('viewpdf.html', data=data)

@app.route('/viewPrereq', methods=['POST'])
def show_prereq():
    if session.get('CURRENT_USER'):
        if request.method == 'POST':
            data = request.get_json()
            session['CURRENT_PAPER_TITLE'] = data
            session['CURRENT_PAPER_PATH'] = get_path_from_title(data)
            session['CURRENT_PAPER_ABSTRACT'], prereqs = get_abstract_nodes_from_title()
            session['CURRENT_PAPER_NODES'] = json.loads(prereqs)
            return json.dumps({'success': 'Successfully retrieved paper data'}), 200, {'contentType': 'application/json'}

@app.route('/paperRating', methods=['POST'])
def paper_rating():
    if session.get('CURRENT_USER'):
        if request.method == 'POST':
            data = request.get_json()
            print ('data is', data)
            result_rating = insert_paper_rating(data)
            return json.dumps({'success': result_rating}), 200, {'ContentType': 'application/json'}

@app.route('/logout', methods=['GET'])
def show_logout():
    session.pop('CURRENT_USER')
    return redirect(url_for('show_index'))

# api request
@app.route('/make_callout', methods=['POST'])
def node_clicked():
    if session.get('CURRENT_USER'):
        if request.method == 'POST':
            data = request.get_json('data')
            clickedNode = data["clickdata"]
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
