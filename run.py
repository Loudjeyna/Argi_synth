import http.server, socketserver, os, sys

os.chdir(r'D:\Lodj_Memoire\SynthAI\frontend')
port = 8080

# Use ThreadingHTTPServer to handle multiple requests in parallel
server = http.server.ThreadingHTTPServer(
    ('127.0.0.1', port),
    http.server.SimpleHTTPRequestHandler
)

print('=' * 50)
print('  SynthAI Server Running!')
print('=' * 50)
print(f'  Open: http://127.0.0.1:{port}/pages/login.html')
print('  Login: admin / admin123')
print('  Ctrl+C to stop.')
print('=' * 50)
sys.stdout.flush()

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.shutdown()
    print('Server stopped.')
