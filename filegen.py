import os

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Fichiers uniques
write("data/worker1_files/rapport.txt", "Ceci est un rapport confidentiel.\n" * 50)
write("data/worker1_files/notes.txt", "Notes de réunion du 12/03.\n")
write("data/worker2_files/image_info.txt", "Métadonnées de l'image.\n")
write("data/worker3_files/journal.txt", "Journal système.\n")

# Fichiers identiques (doublons) sur différents workers
contenu_commun = "Contenu identique pour tester la détection de doublons.\n" * 30
write("data/worker1_files/rapport_copie.txt", contenu_commun)
write("data/worker2_files/rapport_copie.txt", contenu_commun)
write("data/worker3_files/backup.txt", contenu_commun)

# Un fichier volumineux (pour tester le hachage par blocs)
with open("data/worker1_files/gros_fichier.bin", "wb") as f:
    f.write(os.urandom(5 * 1024 * 1024))  # 5 Mo

print("Fichiers de test créés.")