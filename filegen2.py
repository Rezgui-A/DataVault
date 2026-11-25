"""
Générateur de fichiers de test pour DataVault.
Crée ~400 fichiers répartis sur 3 workers, avec :
- Des fichiers uniques de tailles variées
- Des doublons INTRA-worker (même contenu dans le même dossier)
- Des doublons INTER-workers (même contenu sur plusieurs machines)
- Des fichiers volumineux pour tester le hachage par blocs
- Une structure de sous-dossiers pour tester le scan récursif
"""
import os
import random
import shutil
import time

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = "data"
WORKERS = ["worker1_files", "worker2_files", "worker3_files"]

# Nombre de fichiers par catégorie (par worker)
NB_UNIQUE_SMALL   = 40     # petits fichiers texte uniques
NB_UNIQUE_MEDIUM  = 15     # fichiers moyennes tailles uniques
NB_INTRA_DUP      = 10     # doublons dans le même worker
NB_BIG_FILES      = 3      # gros fichiers pour tester le chunking

# Taille des gros fichiers (en Mo)
BIG_FILE_SIZE_MB  = 8

# Graine pour reproductibilité
random.seed(42)


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def write_file(path, content_bytes):
    """Écrit un fichier (texte ou binaire) en créant les dossiers parents."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content_bytes)


def random_text(size_bytes):
    """Génère un contenu texte aléatoire d'environ size_bytes octets."""
    words = ["alpha", "beta", "gamma", "delta", "epsilon",
             "zeta", "eta", "theta", "iota", "kappa"]
    chunks = []
    current_size = 0
    while current_size < size_bytes:
        line = " ".join(random.choices(words, k=8)) + "\n"
        chunks.append(line)
        current_size += len(line)
    return "".join(chunks).encode("utf-8")


def random_binary(size_bytes):
    """Génère un contenu binaire aléatoire (os.urandom)."""
    return os.urandom(size_bytes)


# ---------------------------------------------------------------------------
# Nettoyage
# ---------------------------------------------------------------------------
def clean_previous():
    """Supprime les anciens fichiers de test pour repartir de zéro."""
    print("🧹 Nettoyage des anciens fichiers de test...")
    for w in WORKERS:
        path = os.path.join(BASE_DIR, w)
        if os.path.exists(path):
            shutil.rmtree(path)
    manifest = os.path.join(BASE_DIR, "manifests", "baseline.pkl")
    if os.path.exists(manifest):
        os.remove(manifest)
        print("   -> ancien manifeste supprimé")


# ---------------------------------------------------------------------------
# Génération
# ---------------------------------------------------------------------------
def generate_for_worker(worker_name, shared_duplicates):
    """
    Génère tous les fichiers d'un worker.
    - shared_duplicates : dict {nom_logique: contenu} transmis entre workers
                          pour créer des doublons INTER-workers.
    """
    worker_dir = os.path.join(BASE_DIR, worker_name)
    stats = {"unique": 0, "intra_dup": 0, "inter_dup": 0, "big": 0}

    # ----- 1. Petits fichiers texte uniques (sous-dossier 'docs/') -----
    for i in range(NB_UNIQUE_SMALL):
        size = random.randint(200, 3000)  # 200 B à 3 Ko
        filename = f"docs/doc_{i:03d}.txt"
        write_file(os.path.join(worker_dir, filename), random_text(size))
        stats["unique"] += 1

    # ----- 2. Fichiers de taille moyenne uniques (sous-dossier 'data/') -----
    for i in range(NB_UNIQUE_MEDIUM):
        size = random.randint(50_000, 500_000)  # 50 Ko à 500 Ko
        filename = f"data/medium_{i:03d}.bin"
        write_file(os.path.join(worker_dir, filename), random_binary(size))
        stats["unique"] += 1

    # ----- 3. Doublons INTRA-worker (même contenu, deux noms différents) -----
    for i in range(NB_INTRA_DUP):
        size = random.randint(1_000, 10_000)
        content = random_text(size)
        write_file(os.path.join(worker_dir, f"docs/dup_{i:03d}_a.txt"), content)
        write_file(os.path.join(worker_dir, f"docs/dup_{i:03d}_b.txt"), content)
        stats["intra_dup"] += 2

    # ----- 4. Doublons INTER-workers (partagés entre tous les workers) -----
    # On crée un pool une seule fois, réutilisé par tous les workers
    for name, content in shared_duplicates.items():
        write_file(os.path.join(worker_dir, "shared", name), content)
        stats["inter_dup"] += 1

    # ----- 5. Gros fichiers pour tester le hachage par blocs -----
    for i in range(NB_BIG_FILES):
        size = BIG_FILE_SIZE_MB * 1024 * 1024
        filename = f"big/large_{i:02d}.bin"
        print(f"   ⏳ {worker_name}/{filename} ({BIG_FILE_SIZE_MB} Mo)...")
        write_file(os.path.join(worker_dir, filename), random_binary(size))
        stats["big"] += 1

    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    start = time.time()
    clean_previous()

    # Préparer les doublons inter-workers (contenu identique sur les 3 workers)
    print("\n📦 Préparation des doublons inter-workers...")
    shared_duplicates = {
        "shared_report.txt":  random_text(5_000),
        "shared_config.ini":  random_text(2_000),
        "shared_log.txt":     random_text(8_000),
    }

    # Générer les fichiers de chaque worker
    global_stats = {"unique": 0, "intra_dup": 0, "inter_dup": 0, "big": 0}
    for w in WORKERS:
        print(f"\n🚀 Génération pour {w}...")
        stats = generate_for_worker(w, shared_duplicates)
        for k in global_stats:
            global_stats[k] += stats[k]
        print(f"   ✅ {sum(stats.values())} fichiers créés")

    # Compter réellement les fichiers et la taille totale
    total_files = 0
    total_size = 0
    for w in WORKERS:
        for root, _, files in os.walk(os.path.join(BASE_DIR, w)):
            for f in files:
                total_files += 1
                total_size += os.path.getsize(os.path.join(root, f))

    elapsed = time.time() - start

    # ----- Rapport final -----
    print("\n" + "=" * 60)
    print("📊 RAPPORT DE GÉNÉRATION")
    print("=" * 60)
    print(f"  Fichiers uniques (small + medium) : {global_stats['unique']}")
    print(f"  Doublons intra-worker             : {global_stats['intra_dup']} "
          f"({global_stats['intra_dup'] // 2} paires)")
    print(f"  Doublons inter-workers            : {global_stats['inter_dup']} "
          f"(mêmes fichiers sur les 3 workers)")
    print(f"  Gros fichiers (> 1 Mo)            : {global_stats['big']}")
    print("-" * 60)
    print(f"  TOTAL FICHIERS                    : {total_files}")
    print(f"  TAILLE TOTALE                     : {total_size / (1024*1024):.2f} Mo")
    print(f"  TEMPS DE GÉNÉRATION               : {elapsed:.2f} s")
    print("=" * 60)

    # Estimation du gaspillage d'espace (doublons)
    print("\n💡 À propos des doublons :")
    print(f"   - {global_stats['intra_dup'] // 2} paires intra-worker "
          f"(même dossier)")
    print(f"   - {len(shared_duplicates)} fichiers × 3 workers = "
          f"{len(shared_duplicates) * 3} fichiers, "
          f"soit {len(shared_duplicates) * 2} copies inutiles")
    print(f"\n👉 Total de groupes de doublons attendus : "
          f"{global_stats['intra_dup'] // 2 + len(shared_duplicates)}")

    print("\n✅ Prêt ! Lancez maintenant les 3 workers puis le coordinateur.")


if __name__ == "__main__":
    main()