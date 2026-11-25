class FileInfo:
    def __init__(self, path, name, size, fingerprint, worker_id):
        self._path = path
        self._name = name
        self._size = size
        self._fingerprint = fingerprint
        self._worker_id = worker_id

    @property
    def fingerprint(self):
        return self._fingerprint

    @property
    def size(self):
        return self._size

    def __str__(self):
        return f"[{self._worker_id}] {self._name} ({self._size} bytes) - Hash: {self._fingerprint[:8]}..."

    def to_dict(self):
        return {
            "path": self._path, "name": self._name, "size": self._size,
            "fingerprint": self._fingerprint, "worker_id": self._worker_id
        }