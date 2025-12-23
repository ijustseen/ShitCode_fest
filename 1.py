import json
import threading
import time
import urllib.request
import sys
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

class SortHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            candidate = data.get("candidate")
            arr = data.get("arr", [])
            sort_type = data.get("type", "asc")
            
            def linear_check(a, reverse=False):
                if reverse:
                    return all(a[i] >= a[i+1] for i in range(len(a)-1))
                return all(a[i] <= a[i+1] for i in range(len(a)-1))

            def is_sorted(a, reverse=False):
                if not linear_check(a, reverse):
                    return False
                
                check_copy = list(a)
                random.shuffle(check_copy)
                while not linear_check(check_copy, reverse):
                    random.shuffle(check_copy)
                
                return a == check_copy

            check_results = []
            paranoia_level = 2000
            
            for _ in range(paranoia_level):
                temp_arr = list(arr)
                while not is_sorted(temp_arr, reverse=(sort_type == "desc")):
                    random.shuffle(temp_arr)
                check_results.append(temp_arr[0] == candidate)

            is_valid = all(check_results)

            response = {"valid": is_valid}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SortHandler)
    httpd.serve_forever()

def main():
    port = 8000
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    data_to_sort = [34, 2, 23, 76, 1, 89]
    print(f"Входные данные: {data_to_sort}")
    print("\nВыберите тип сортировки:")
    print("1. По возрастанию")
    print("2. По убыванию")

    try:
        choice = input("Ваш выбор: ")
    except EOFError:
        return

    sort_type = "asc"
    if choice == '1':
        sort_type = "asc"
    elif choice == '2':
        sort_type = "desc"
    else:
        print("Неверный выбор")
        return

    sorted_list = []
    remaining_list = list(data_to_sort)
    
    try:
        url = f"http://localhost:{port}"
        
        while remaining_list:
            found = False
            while not found:
                candidate = random.choice(remaining_list)
                
                payload = {
                    "candidate": candidate,
                    "arr": remaining_list,
                    "type": sort_type
                }
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode('utf-8'))
                    if resp_data["valid"]:
                        sorted_list.append(candidate)
                        remaining_list.remove(candidate)
                        found = True
                    else:
                        pass

        print(f"Выходные данные: {sorted_list}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
