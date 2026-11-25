import socket
import os
import threading
import time
from common.protocol import send_msg, recv_msg
from worker.file_processor import process_parallel

class WorkerNode:
    def __init__(self, worker_id, host, port, directory, num_procs=4):
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.directory = os.path.abspath(directory)
        self.num_procs = num_procs

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        print(f"[{self.worker_id}] En écoute sur {self.host}:{self.port}...")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle_coordinator, args=(conn,), daemon=True).start()

    def handle_coordinator(self, conn):
        try:
            msg = recv_msg(conn)
            if msg and msg.get("type") == "START_SCAN":
                print(f"[{self.worker_id}] Ordre de scan reçu. Démarrage...")
                files = self.scan_directory()
                
                # Calcul parallèle
                start_time = time.time()
                results = process_parallel(files, self.num_procs)
                exec_time = time.time() - start_time

                # Formatage des résultats
                valid_results = []
                for path, hash_val, size in results:
                    if hash_val:
                        valid_results.append({
                            "path": path, "name": os.path.basename(path),
                            "size": size, "fingerprint": hash_val, "worker_id": self.worker_id
                        })
                
                send_msg(conn, {
                    "type": "SCAN_RESULTS", 
                    "data": valid_results,
                    "exec_time": exec_time
                })
                print(f"[{self.worker_id}] Scan terminé en {exec_time:.2f}s.")
        except Exception as e:
            print(f"[{self.worker_id}] Erreur: {e}")
        finally:
            conn.close()

    def scan_directory(self):
        file_paths = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_paths.append(os.path.normpath(os.path.join(root, file)))
        return file_paths

if __name__ == "__main__":
    # Simulation de 3 workers en local
    import sys
    if len(sys.argv) < 5:
        print("Usage: python worker_server.py <ID> <IP> <PORT> <DIRECTORY>")
        sys.exit(1)
    
    w_id, ip, port, directory = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    os.makedirs(directory, exist_ok=True)
    worker = WorkerNode(w_id, ip, port, directory)
    worker.start()