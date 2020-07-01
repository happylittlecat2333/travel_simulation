# import socket
# ip_port = ('127.0.0.1', 9999)
# sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
# sk.bind(ip_port)
#
# while True:
#     data = sk.recv(1024).strip().decode()
#     print(data)
#     if data == "exit":
#         print("客户端主动断开连接！")
#         break
#
#
# sk.close()


from http.server import HTTPServer, BaseHTTPRequestHandler


class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))


httpd = HTTPServer(('localhost', 5000), Serv)
httpd.serve_forever()