import os
import re
import sys
from DateTime import DateTime
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


class IdsRequestHandler(SimpleHTTPRequestHandler):
    
    components = ['src', 'tarmii.theme', 'tarmii', 'theme', 'tests']
    base_path = os.path.join(os.getcwd(), *components)

    def send_head(self):
        path = self.translate_path(self.path)                                   
        f = None                                                                
        if os.path.isdir(path):                                                 
            if not self.path.endswith('/'):                                     
                # redirect browser - doing basically what apache does           
                self.send_response(301)                                         
                self.send_header("Location", self.path + "/")                   
                self.end_headers()                                              
                return None                                                     
            for index in "index.html", "index.htm":                             
                index = os.path.join(path, index)                               
                if os.path.exists(index):                                       
                    path = index                                                
                    break                                                       
                else:                                                               
                    return self.list_directory(path)                                

        ctype = self.guess_type(path)                                           
        cdisposition = None
        if self.path.endswith('/@@assessmentitem-ids-xml'):
            path = os.path.join(self.base_path, 'assessmentitem_ids.xml')
            ctype = 'text/xml'
        elif self.path.endswith('/@@assessmentitem-xml'):
            path = os.path.join(self.base_path, 'assessmentitems.zip')
            cdisposition = "attachment; filename=assessmentitems.zip"
            ctype = 'application/octet-stream'

        try:                                                                    
            # Always read in binary mode. Opening files in text mode may cause  
            # newline translations, making the actual size of the content       
            # transmitted *less* than the content-length!                       
            f = open(path, 'rb')                                                
        except IOError:                                                         
            self.send_error(404, "File not found")                              
            return None                                                         

        self.send_response(200)                                                 
        self.send_header("Content-type", ctype)                                 
        if cdisposition:
            self.send_header("Content-Disposition", cdisposition)
        fs = os.fstat(f.fileno())                                               
        self.send_header("Content-Length", str(fs[6]))                          
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))   
        self.send_header('expires', 0)
        self.end_headers()                                                      
        return f 

    def do_POST(self):
        """Serve a POST request."""                                              
        f = self.send_head()                                                    
        if f:                                                                   
            self.copyfile(f, self.wfile)                                        
            f.close() 


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
