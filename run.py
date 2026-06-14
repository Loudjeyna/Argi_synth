import http.server, socketserver, os, sys, socket

# Set working directory to frontend folder
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend'))

# Detect if we're on a cloud platform (Render, Railway, Koyeb, etc.)
# Render sets PORT environment variable automatically
PORT_ENV = os.environ.get('PORT', '')
is_cloud = PORT_ENV != ''

if is_cloud:
    # CLOUD: Use Render's PORT and bind to 0.0.0.0 (accessible from internet)
    port = int(PORT_ENV)
    host = '0.0.0.0'
else:
    # LOCAL: Find free port and bind to localhost only
    def find_free_port(start=8080, end=8090):
        for port in range(start, end):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    continue
        return None

    port = find_free_port()
    if port is None:
        print('ERROR: No free port available in range 8080-8089.')
        sys.exit(1)
    host = '127.0.0.1'

server = http.server.ThreadingHTTPServer(
    (host, port),
    http.server.SimpleHTTPRequestHandler
)

print('=' * 50)
print('  SynthAI Server Running!')
print('=' * 50)
if is_cloud:
    print(f'  Running on cloud (host={host}, port={port})')
else:
    print(f'  Open: http://127.0.0.1:{port}/pages/index.html')
    print('  Login: admin / admin123')
print('  Ctrl+C to stop.')
print('=' * 50)
sys.stdout.flush()

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.shutdown()
    print('Server stopped.')