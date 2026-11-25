import struct
import pickle

def send_msg(sock, msg):
    """Sérialise et envoie un message avec sa taille (Framing)."""
    data = pickle.dumps(msg)
    # Envoie d'abord la taille (4 octets) puis les données
    sock.sendall(struct.pack('!I', len(data)) + data)

def recv_msg(sock):
    """Reçoit la taille puis les données, gère les déconnexions."""
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('!I', raw_msglen)[0]
    return pickle.loads(recvall(sock, msglen))

def recvall(sock, n):
    """Reçoit exactement n octets."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)