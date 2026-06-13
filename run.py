import http.server, socketserver, os, sys, socket

os.chdir(r'I:\apps\Synth_AI\frontend')

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

server = http.server.ThreadingHTTPServer(
    ('127.0.0.1', port),
    http.server.SimpleHTTPRequestHandler
)

print('=' * 50)
print('  SynthAI Server Running!')
print('=' * 50)
print(f'  Open: http://127.0.0.1:{port}/pages/first.html')
print('  Login: admin / admin123')
print('  Ctrl+C to stop.')
print('=' * 50)
sys.stdout.flush()

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.shutdown()
    print('Server stopped.')
