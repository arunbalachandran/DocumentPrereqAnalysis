from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
import subprocess
import shlex
import sys
import json

app = Flask(__name__)

@app.route('/make_callout', methods=['GET', 'POST'])
def node_clicked():
    if request.method == 'POST':
        # clickedNode = request.args.get('clickedNode')
        data = request.get_json()
        clickedNode = data["clickdata"]
        print "This is the clicked node ====>>>> "+str(clickedNode)
        cmd = "python scholar.py -A '" + clickedNode + "'  -c 100 --after=1970"
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        sys.stdout.write('\noutput is ' + output + '\n ')
        # final_output = output.split('>]')[0][1:] + '>'
        # sys.stdout.write(final_output+'\n')
        return json.dumps({"data": output})

@app.route('/', methods=['POST'])
def upload_file() :
    files = request.files['file']
    print files
    # if 'file' not in request.files:
    #     flash('No file part')
    #     return redirect(request.url)
    # file = request.files['file']
    # # if user does not select file, browser also
    # # submit a empty part without filename
    # if file.filename == '':
    #     flash('No selected file')
    #     return redirect(request.url)
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #     return redirect(url_for('uploaded_file',filename=filename))
    return ''

@app.route('/')
def index() :
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=2000)
