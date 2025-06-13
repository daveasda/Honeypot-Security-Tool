import socket
import sys
import threading
import datetime
import json
from pathlib import Path

# Directory for logs
LOG_DIR = Path("honeypot_logs")
LOG_DIR.mkdir(exist_ok=True)

class Honeypot:
    def __init__(self, ip='0.0.0.0', ports=None):
        self.ip = ip
        self.ports = ports if ports else [21, 22, 80, 443]
        self.log_file = LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.json"

        # Service emulation banners
        self.banners = {
            21: b"220 FTP server ready\r\n",
            22: b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n",
            80: b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n",
            443: b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n"
        }

    def log_connection(self, port, remote_ip, data):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "port": port,
            "data": data.decode(errors="ignore")
        }
        with open(self.log_file, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')
        print(f"[+] Logged connection from {remote_ip}:{port}")

    def handle_client(self, client_socket, remote_ip, port):
        try:
            # Send banner
            banner = self.banners.get(port)
            if banner:
                client_socket.sendall(banner)

            # Receive all incoming data
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.log_connection(port, remote_ip, data)
                client_socket.sendall(b"Command not recognized\r\n")
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            client_socket.close()

    def start_server(self, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.ip, port))
            server.listen(5)
            print(f"[+] Listening on {self.ip}:{port}")
        except Exception as e:
            print(f"[!] Failed to bind port {port}: {e}")
            return

        while True:
            client_socket, addr = server.accept()
            remote_ip = addr[0]
            print(f"[+] Connection from {remote_ip}:{port}")
            threading.Thread(target=self.handle_client, args=(client_socket, remote_ip, port), daemon=True).start()

    def run(self):
        print("[*] Starting honeypot...")
        for port in self.ports:
            t = threading.Thread(target=self.start_server, args=(port,), daemon=True)
            t.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n[!] Shutting down honeypot.")
            sys.exit(0)

if __name__ == "__main__":
    honeypot = Honeypot()
    honeypot.run()
