import socket
import json
import subprocess
import sys

# --- Configuration ---
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8000         # Port to listen on (must match the port in the Android app)
ADB_PATH = 'adb'    # Assuming 'adb' is in your system's PATH

def setup_adb_reverse():
    """Sets up the adb reverse proxy for communication."""
    print(f"--- Attempting to set up adb reverse for tcp:{PORT} ---")
    try:
        # Command to forward the phone's port to the computer's port
        command = [ADB_PATH, 'reverse', f'tcp:{PORT}', f'tcp:{PORT}']
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Success: {result.stdout.strip() or 'adb reverse completed.'}")
        return True
    except FileNotFoundError:
        print("\n[ERROR] `adb` command not found.")
        print("Please ensure the Android SDK Platform-Tools are installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] adb reverse failed: {e.stderr}")
        print("Is your phone connected with USB Debugging enabled and authorized?")
        return False

def start_server():
    """Starts the TCP server to listen for NFC data from the phone."""
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
            print(f"\n--- Server listening on {HOST}:{PORT} ---")
            print("--- Scan an NFC tag with the helper app on your phone... ---")

            while True:
                # Wait for a connection
                conn, addr = s.accept()
                with conn:
                    print(f"\n[INFO] Connection accepted from {addr}")
                    data_chunks = []
                    while True:
                        # Receive data in chunks
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        data_chunks.append(chunk)
                        print(data_chunks)
                    
                    # Combine, decode, and clean the data by stripping whitespace
                    raw_data = b''.join(data_chunks).decode('utf-8').strip()
                    print(f"[DATA] Received raw string: '{raw_data}'")

                    # Attempt to parse the data as JSON
                    try:
                        json_data = json.loads(raw_data)
                        print("[JSON] Successfully parsed JSON:")
                        # Pretty print the JSON
                        print(json.dumps(json_data, indent=4))
                    except json.JSONDecodeError:
                        print("[ERROR] Failed to parse string as JSON. It might be plain text or malformed.")
                    
                    print("\n--- Waiting for the next NFC tag scan... ---")

        except OSError as e:
            print(f"\n[ERROR] Could not start server: {e}")
            print(f"Is another application already using port {PORT}?")
        except KeyboardInterrupt:
            print("\n--- Server shutting down. ---")
            sys.exit(0)

if __name__ == '__main__':
    if setup_adb_reverse():
        start_server()
    else:
        print("\n--- Exiting due to adb setup failure. Please resolve the issues above. ---")
        sys.exit(1)


