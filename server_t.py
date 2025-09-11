from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Classe para testar o servidor HTTPServer
class NFCRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/nfc-data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                json_data = json.loads(post_data.decode('utf-8'))
                print("Dados NFC recebidos:")
                print(json.dumps(json_data, indent=2))

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"status": "success"})
                self.wfile.write(response.encode('utf-8'))
            except json.JSONDecodeError:
                self.send_error(400, "JSON inválido")
        else:
            self.send_error(404, "Endpoint não encontrado")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, NFCRequestHandler)
    print(f"Servidor iniciado na porta {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()