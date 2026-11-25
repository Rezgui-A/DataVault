import threading
from common.protocol import send_msg, recv_msg
import socket
class WorkerThread(threading.Thread):
    def __init__(self, worker_id, ip, port, shared_results, lock):
        super().__init__()
        self.worker_id = worker_id
        self.ip = ip
        self.port = port
        self.shared_results = shared_results
        self.lock = lock # Verrou pour protéger les données partagées
        self.exec_time = 0

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip, self.port))
            
            # Envoi de l'ordre de scan
            send_msg(sock, {"type": "START_SCAN"})
            
            # Réception des résultats
            response = recv_msg(sock)
            if response and response.get("type") == "SCAN_RESULTS":
                # Synchronisation : on modifie la liste partagée
                with self.lock:
                    self.shared_results.extend(response["data"])
                self.exec_time = response["exec_time"]
            
            sock.close()
        except ConnectionRefusedError:
            print(f"[Erreur] Impossible de contacter le worker {self.worker_id} sur {self.ip}:{self.port}")