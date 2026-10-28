"""Serve this folder over HTTPS so a phone on the same Wi-Fi can use the mic.

Run:  python3 serve-https.py   then open the printed https:// link on your phone.
The certificate in .cert/ is self-signed, so the phone shows a warning the first time.
"""
import http.server
import os
import socket
import ssl

PORT = 8443
ROOT = os.path.dirname(os.path.abspath(__file__))


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(os.path.join(ROOT, ".cert/cert.pem"), os.path.join(ROOT, ".cert/key.pem"))
httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
print(f"On your phone (same Wi-Fi): https://{lan_ip()}:{PORT}", flush=True)
httpd.serve_forever()
