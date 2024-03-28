#!/opt/.pyenv/versions/automation36/bin/python

import os
from flask import Flask, request, abort, jsonify, send_from_directory, render_template

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import socket
# from whitenoise import WhiteNoise
import argparse
from datetime import datetime


# class CherrokeeFix(object):

#     def __init__(self, app, script_name):
#         self.app = app
#         self.script_name = script_name

#     def __call__(self, environ, start_response):
#         path = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
#         environ['SCRIPT_NAME'] = self.script_name
#         environ['PATH_INFO'] = path[len(self.script_name):]
#         # assert path[:len(self.script_name)] == self.script_name
#         return self.app(environ, start_response)



app =Flask(__name__, static_url_path='/static_csv')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.wsgi_app = CherrokeeFix(app.wsgi_app, '/csv')
# app.wsgi_app = WhiteNoise(app.wsgi_app, autorefresh=True)


@app.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    dict_arg = {}
    request_arg = request.args
    request_host = request.host.split(":")[0]
    for each in request_arg.items():
        dict_arg[each[0]] = each[1].encode('utf-8')
    directory = dict_arg["directory"].decode("utf-8")
    # hostname = socket.gethostname()
    # IPAddr = socket.gethostbyname(hostname)
    IPAddr = request_host
    files = []
    for filename in os.listdir(directory):
        dict_tmp = {}
        dict_tmp["filename"] = filename
        path = os.path.join(directory, filename)
        size = os.stat(path).st_size
        time_change = datetime.fromtimestamp(int(os.stat(path).st_ctime))
        # dt_object = datetime.fromtimestamp(timestamp)

        if os.path.isfile(path):
            dict_tmp["type"] = "file"
            dict_tmp["size"] = size
            dict_tmp["ctime"] = time_change

            # dict_tmp["href"] = "http://{}:{}/files/{}?directory={}".format(IPAddr, port, filename, directory)
            dict_tmp["href"] = "/csv/get_csv?csv_file={}/{}".format( directory, filename)
            dict_tmp["download"] = "/csv/files/{}?directory={}".format( filename, directory)
        elif os.path.isdir(path):
            dict_tmp["type"] = "dir"
            dict_tmp["size"] = size
            dict_tmp["ctime"] = time_change

            dict_tmp["href"] = "/csv/files?directory={}/{}".format( directory, filename)
        files.append(dict_tmp)

    return render_template('index.html', files=files, directory=directory)
    # return jsonify(files)


@app.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    # try:
    dict_arg = {}
    request_arg = request.args
    for each in request_arg.items():
        dict_arg[each[0]] = each[1].encode('utf-8')
    directory = dict_arg["directory"].decode('utf-8')
    return send_from_directory(directory, path, as_attachment=True)
    # except:
    #     return "Download ERROR"


@app.route("/get_csv")
def view_file_csv():
    dict_arg = {}
    request_arg = request.args
    for each in request_arg.items():
        dict_arg[each[0]] = each[1].encode('utf-8')
    csv_file = dict_arg["csv_file"].decode("utf-8")
    csv_filename = csv_file.split("/")[-1]
    current_path = os.getcwd()
    data_path = os.path.join(current_path, "static/data/")
    os.system("rm -f {}*".format(data_path))
    os.system("cp -f {} {}".format(csv_file, data_path))
    path = "static_csv/data/{}".format(csv_filename)
    if ".csv" in csv_filename:
        return render_template('csv_to_table.html', path=path, csv_filename=csv_filename)
    else:
        text = open(csv_file, 'r')
        content = text.read()
        text.close()
        return "<pre>{}</pre>".format(content)

# @app.route("/files/<filename>", methods=["POST"])
# def post_file(filename):
#     """Upload a file."""

#     if "/" in filename:
#         # Return 400 BAD REQUEST
#         abort(400, "no subdirectories directories allowed")

#     with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
#         fp.write(request.data)

#     # Return 201 CREATED
#     return "", 201


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#   response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#   response.headers["Pragma"] = "no-cache"
#   response.headers["Expires"] = "0"
#   response.headers['Cache-Control'] = 'public, max-age=0'

    return response


if __name__=='__main__':
    cmdline = argparse.ArgumentParser(description="Csv to HTML")
    cmdline.add_argument("-p", help="port", nargs='?', type=str, default="8000")
    args = cmdline.parse_args()
    app.run(host="0.0.0.0", port=args.p, debug=True)