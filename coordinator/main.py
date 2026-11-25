from coordinator.coordinator import Coordinator   

if __name__ == "__main__":
    coord = Coordinator()
    
    #  Scan distribué
    coord.run_distributed_scan()
    
    #  Détection des doublons
    coord.detect_duplicates()
    
    # 3 Vérification d'intégrité
    coord.verify_integrity()


