"""
Simple OpenLava dashboard.
"""

import socket
import threading

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

from mesoslava import lava_shim

# TODO: visualize tasks vs pending jobs.

TMPL = '''
<!DOCTYPE html>
<html>
    <head>
        <title>OpenLava</title>
        <link rel="stylesheet" 
            href="https://unpkg.com/purecss@1.0.0/build/pure-min.css" 
            crossorigin="anonymous">
        <style type="text/css">
            body {
                padding: 0.5em;
            }
            table {
            }
            h1 {
                font-size: 1.4em;
                color: #444;
            }
            h2 {
                font-size: 1.2em;
                color: #ff7f00;
            }
        </style>
    </head>
    <body>
        <img src="http://www.openlava.org/images/openlava_logo_slogan.gif"
            alt="OpenLava logo" />
        <h1>OpenLava batch information</h1>
        <h2>Queue information</h2>
        %s
        <h2>Host information</h2>
        %s
        <h1>OpenLava base information</h1>
        <h2>Load information</h2>
        %s
        <h2>Host information</h2>
        %s
    </body>
</html>
'''


def get_hostname():
    return socket.gethostname()


def create_table(data):
    """
    Create a html tables.
    """
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
    """
    Simple WSGI app.
    """
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)

    return TMPL % (create_table(lava_shim.get_bqueues()),
                   create_table(lava_shim.get_bhosts()),
                   create_table(lava_shim.get_hosts_load()),
                   create_table(lava_shim.get_hosts()))


class Dashboard(threading.Thread):
    """
    Dashboard Thread.
    """

    def __init__(self):
        super(Dashboard, self).__init__()
        self.done = False

    def run(self):
        httpd = make_server('', 9876, simple_app)
        while not self.done:
            httpd.handle_request()
