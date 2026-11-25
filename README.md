exection :
executer d'abord les workers sans fichiers
2.puis avec filegen1
puis avec filegen2

# Terminal 1
python -m worker.worker_server Worker1 127.0.0.1 50001 data/worker1_files

# Terminal 2
python -m worker.worker_server Worker2 127.0.0.1 50002 data/worker2_files

# Terminal 3
python -m worker.worker_server Worker3 127.0.0.1 50003 data/worker3_files
Puis, dans un 4ᵉ terminal :

bash
python -m coordinator.main


