
import socket
import threading

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

import util

TMPL = '''
<!DOCTYPE html>
<html>
    <head>
        <title>OpenLava</title>
        <link rel="stylesheet"
            href="http://yui.yahooapis.com/pure/0.6.0/pure-min.css">
        <style type="text/css">
            body {
                padding: 8px;
            }
            table {
                margin: 0px auto;
            }
        </style>
    </head>
    <body>
        <img src="http://www.openlava.org/images/openlava_logo_slogan.gif"
            alt="OpenLava logo" />
        %s
    </body>
</html>
'''


def get_hostname():
    return socket.gethostname()


def create_table(data):
    tmp = '<table class="pure-table"><thead><tr>'
    for item in data[0]:
        tmp += '<th>' + item + '</th>'
    tmp += '</tr></thead><tbody>'
    i = 1
    while i < len(data):
        tmp += '<tr>'
        for item in data[i]:
            tmp += '<td>' + item + '</td>'
        tmp += '</tr>'
        i += 1
    tmp += '</tbody></table>'
    return tmp


def simple_app(environ, start_response):
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)

    return TMPL % create_table(util.get_hosts())


def serve():
    httpd = make_server('', 9876, simple_app)
    t = threading.Thread(target=httpd.serve_forever)
    t.start()