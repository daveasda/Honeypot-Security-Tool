import socket

targets = [
    {"host": "127.0.0.1", "port": 21, "payload": b"USER anonymous\r\nPASS guest\r\n"},
    {"host": "127.0.0.1", "port": 22, "payload": b"root\r\n"},
    {"host": "127.0.0.1", "port": 80, "payload": b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"},
    {"host": "127.0.0.1", "port": 443, "payload": b"GET /secure HTTP/1.1\r\nHost: localhost\r\n\r\n"}
]

for target in targets:
    try:
        sock = socket.socket()
        sock.connect((target["host"], target["port"]))
        banner = sock.recv(1024)
        print(f"[+] Received banner from {target['port']}: {banner.decode(errors='ignore')}")
        sock.sendall(target["payload"])
        response = sock.recv(1024)
        print(f"[+] Response: {response.decode(errors='ignore')}")
        sock.close()
    except Exception as e:
        print(f"[!] Error connecting to {target['port']}: {e}")
