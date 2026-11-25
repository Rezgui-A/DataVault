import threading
import pickle
import os
import time
from collections import defaultdict
from coordinator.worker_manager import WorkerThread

class Coordinator:
    def __init__(self):
        self.workers_config = [
            ("Worker1", "127.0.0.1", 50001),
            ("Worker2", "127.0.0.1", 50002),
            ("Worker3", "127.0.0.1", 50003)
        ]
        self.shared_results = []
        self.lock = threading.Lock() # Protège shared_results
        self.semaphore = threading.Semaphore(3) # Limite à 3 connexions simultanées max (optionnel ici)

    def run_distributed_scan(self):
        print("--- Lancement du scan distribué ---")
        self.shared_results.clear()
        start_time = time.time()
        threads = []

        for w_id, ip, port in self.workers_config:
            t = WorkerThread(w_id, ip, port, self.shared_results, self.lock)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        total_time = time.time() - start_time
        print(f"Scan terminé en {total_time:.2f} secondes. {len(self.shared_results)} fichiers traités.")
        return self.shared_results

    def detect_duplicates(self):
        print("\n--- Détection des doublons ---")
        hash_groups = defaultdict(list)
        for f in self.shared_results:
            # On groupe par hash et par taille
            hash_groups[(f["fingerprint"], f["size"])].append(f)

        duplicates = {k: v for k, v in hash_groups.items() if len(v) > 1}
        
        if not duplicates:
            print("Aucun doublon trouvé.")
            return

        wasted_space = 0
        for i, (key, files) in enumerate(duplicates.items(), 1):
            print(f"Groupe {i} (Taille: {files[0]['size']} octets):")
            for f in files:
                print(f"  - [{f['worker_id']}] {f['path']}")
            wasted_space += files[0]['size'] * (len(files) - 1)
        
        print(f"Espace de stockage gaspillé : {wasted_space} octets.")

    def verify_integrity(self, manifest_path="data/manifests/baseline.pkl"):
        print("\n--- Vérification d'intégrité ---")
        current_state = {f["path"]: f["fingerprint"] for f in self.shared_results}
        
        if not os.path.exists(manifest_path):
            print("Création du manifeste de référence...")
            os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
            with open(manifest_path, "wb") as f:
                pickle.dump(current_state, f)
            print("Manifeste sauvegardé.")
            return

        with open(manifest_path, "rb") as f:
            baseline = pickle.load(f)

        modified = []
        deleted = []
        new = []

        for path, old_hash in baseline.items():
            if path not in current_state:
                deleted.append(path)
            elif current_state[path] != old_hash:
                modified.append(path)

        for path in current_state:
            if path not in baseline:
                new.append(path)

        print(f"Fichiers modifiés : {len(modified)}")
        for m in modified: print(f"  - {m}")
        print(f"Fichiers supprimés : {len(deleted)}")
        for d in deleted: print(f"  - {d}")
        print(f"Nouveaux fichiers : {len(new)}")
        for n in new: print(f"  - {n}")