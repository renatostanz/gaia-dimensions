# nfc_server.py
import http.server
import socketserver
import os
import platform

# --- Configuration ---
PORT = 8000 # The port the server will listen on.
ACTION_COMMAND = "nfc-data" # The text written on your NFC tag.

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # The path of the request will be the data sent from the phone
        # e.g., http://192.168.1.105:8000/action_hello
        request_path = self.path.strip("/")

        print(f"Received request for: {request_path}")

        if request_path == ACTION_COMMAND:
            print("Action triggered! Saying hello...")

            # Execute text-to-speech command based on OS
            system_os = platform.system()
            if system_os == "Darwin": # macOS
                os.system('say "Hello, the NFC tag was scanned."')
            elif system_os == "Windows": # Windows
                # This PowerShell command speaks the text
                os.system('PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'Hello, the NFC tag was scanned.\');"')
            else: # Linux (requires espeak to be installed)
                os.system('espeak-ng "Hello, the NFC tag was scanned."')

            # Respond to the phone app that the request was successful
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Action executed successfully.")
        else:
            # Respond with an error if the command is unknown
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown action.")

# --- Start the server ---
Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server started at localhost:{PORT}")
    print(f"Listening for requests on your local network...")
    print("Tap your NFC tag now!")
    httpd.serve_forever()
