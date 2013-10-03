import os
import re
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


class IdsRequestHandler(SimpleHTTPRequestHandler):
    
    print 'Loading xml ...'
    filename = os.path.join(os.getcwd(),
                            'src', 'tarmii.theme', 'tarmii', 'theme',
                            'tests', 'assessmentitem_ids.xml')
    xml_file = open(filename,'rb')
    content = xml_file.read()
    xml_file.close()
    print 'done.'

    def do_GET(self):
        self.wfile.write(self.content)


HandlerClass = IdsRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
server_address = ('127.0.0.1', port)

HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, HandlerClass)

sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()
