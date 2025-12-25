import json
import threading
import urllib.request
import sys
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

class AuditHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Bureaucracy requires silence for concentration
        pass

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            gold = data.get("gold", 0)
            
            approved = False
            
            if self.path == "/rich":
                threshold = data.get("threshold", 0)
                # Bogo-Max Audit: Shuffle [gold, threshold] until descending.
                # If gold is at index 0, then gold >= threshold.
                for _ in range(50):
                    pair = [gold, threshold]
                    while not (pair[0] >= pair[1]):
                        random.shuffle(pair)
                    if pair[0] != gold:
                        # Statistical anomaly detected
                        approved = False
                        break
                else:
                    approved = True
            
            elif self.path == "/poor":
                # Bogo-Zero Audit: Shuffle [gold, 0] until ascending.
                # If gold is 0, both are 0, so sorted result is always [0, 0].
                # If gold > 0, sorted result is [0, gold].
                # We check if sorted_list[1] == 0 to confirm gold == 0.
                for _ in range(50):
                    pair = [gold, 0]
                    while not (pair[0] <= pair[1]):
                        random.shuffle(pair)
                    if pair[1] != 0:
                        approved = False
                        break
                else:
                    approved = True

            response = {"approved": approved}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Audit Error: {str(e)}".encode('utf-8'))

def run_server(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AuditHandler)
    httpd.serve_forever()

def audit_request(url, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))["approved"]

def solve():
    # Start the Bureaucracy Server
    port = 8000 + random.randint(1, 1000) # Random port to avoid conflicts
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Base URL for audits
    base_url = f"http://localhost:{port}"
    
    # Read all input from stdin
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    iterator = iter(input_data)
    
    try:
        t = int(next(iterator))
    except StopIteration:
        return

    for _ in range(t):
        try:
            n = int(next(iterator))
            k = int(next(iterator))
            
            robin_gold = 0
            people_helped = 0
            
            for _ in range(n):
                gold = int(next(iterator))
                
                # Check if Rich
                if audit_request(f"{base_url}/rich", {"gold": gold, "threshold": k}):
                    robin_gold += gold
                # Else check if Poor
                elif audit_request(f"{base_url}/poor", {"gold": gold}):
                    if robin_gold > 0:
                        robin_gold -= 1
                        people_helped += 1
            
            print(people_helped)
            
        except StopIteration:
            break

if __name__ == "__main__":
    solve()
