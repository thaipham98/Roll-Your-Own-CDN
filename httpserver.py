import sys
import threading
import time
from http.server import *
import urllib.request

hostName = "localhost"
serverPort = 8080
origin = "cs5700cdnorigin.ccs.neu.edu"


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        #print(origin + ":" + str(serverPort) + self.path)

        with urllib.request.urlopen("http://" + origin + ":" + str(serverPort) + self.path) as response:
            html = response.read()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(html))


class HTTPServer:
    def __init__(self, port, origin):
        self.server = ThreadingHTTPServer((hostName, serverPort), RequestHandler)
        self.port = port
        self.origin = origin

    def run(self):
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()
        print("%s server loop running in thread: %s" % (self.server.RequestHandlerClass.__name__[:3], thread.name))

        try:
            while 1:
                time.sleep(1)
                sys.stderr.flush()
                sys.stdout.flush()

        except KeyboardInterrupt:
            pass
        finally:
            self.server.shutdown()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit("Invalid number of arguments")

    #TODO init cache
    port = sys.argv[2]
    origin = sys.argv[4]
    http_server = HTTPServer(port, origin)
    http_server.run()
