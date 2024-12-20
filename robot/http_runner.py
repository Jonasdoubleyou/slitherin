from http.server import HTTPServer, BaseHTTPRequestHandler

PATH = "/home/robot/robot/"

index_file = ""
with open(PATH + "index.html", "r") as f:
    index_file = f.read().encode(encoding='utf_8')

class WebServer(BaseHTTPRequestHandler):
    def set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_GET(self):
        if self.path == "/status":
            self.get_status()
        else:
            self.get_index()

    def do_POST(self):
        print("Do POST" + self.path)
        if self.path == "/command":
            self.post_command()

    def do_OPTIONS(self):
        """ Answer CORS request """
        self.send_response(200, "ok")
        self.set_cors()
        self.end_headers()
        
    def get_index(self):
        self.send_response(200)
        self.set_cors()
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(index_file)

    def get_status(self):
        self.send_response(200)
        self.set_cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        with open(PATH + "status.json", "r") as f:
            self.wfile.write(f.read().encode(encoding='utf_8'))

    def post_command(self):
        command = self.rfile.read(int(self.headers['content-length'])).decode("utf-8")
        print("command: " + command)
        with open(PATH + "command.json", "w") as f:
            f.write(command)
        self.send_response(200)
        self.set_cors()
        self.end_headers()
        self.wfile.write("OK".encode(encoding='utf_8'))

httpd = HTTPServer(('', 80), WebServer)
httpd.serve_forever()