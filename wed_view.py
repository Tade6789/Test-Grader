# simple_server.py
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

PORT = 5000
Handler = SimpleHTTPRequestHandler

print(f"Starting server on http://0.0.0.0:{PORT}")
print("Serving files from the current directory...")

# Create the server instance
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    # Keep the server running until you press Ctrl+C
    httpd.serve_forever()
