import hashlib
import os
import multiprocessing

def calculate_hash(filepath, chunk_size=4096):
    """Calcule le SHA-256 en lisant par blocs (gère les gros fichiers)."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return filepath, hasher.hexdigest(), os.path.getsize(filepath)
    except Exception as e:
        return filepath, None, 0

def process_parallel(file_paths, num_processes=4):
    """Utilise multiprocessing.Pool pour paralléliser le calcul."""
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(calculate_hash, file_paths)
    return results