from __future__ import annotations
import socket, threading, json, time

class JSONSocket:
    def __init__(self, conn: socket.socket, token: str):
        self.conn = conn
        self.token = token
        self.lock = threading.Lock()
        self.buf = b""

    def send(self, payload: dict):
        payload = dict(payload)
        payload["token"] = self.token
        data = (json.dumps(payload) + "\n").encode("utf-8")
        with self.lock:
            self.conn.sendall(data)

    def recv(self, timeout=0.5):
        self.conn.settimeout(timeout)
        try:
            chunk = self.conn.recv(4096)
            if not chunk:
                return None
            self.buf += chunk
            if b"\n" in self.buf:
                line, self.buf = self.buf.split(b"\n", 1)
                try:
                    obj = json.loads(line.decode("utf-8"))
                    return obj
                except Exception:
                    return None
        except socket.timeout:
            return None

class EventServer(threading.Thread):
    """Accepts client connections and relays events from host to the active client."""
    def __init__(self, bind_ip, port, token):
        super().__init__(daemon=True)
        self.bind_ip = bind_ip
        self.port = port
        self.token = token
        self.sock = None
        self.clients = {}  # name -> JSONSocket
        self.running = threading.Event()
        self.running.clear()

    def run(self):
        self.running.set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.bind_ip, self.port))
        self.sock.listen(5)
        while self.running.is_set():
            try:
                self.sock.settimeout(0.5)
                conn, addr = self.sock.accept()
                js = JSONSocket(conn, self.token)
                # First message must identify the client
                hello = js.recv(timeout=3.0)
                if not hello or hello.get("type") != "hello" or hello.get("token") != self.token:
                    conn.close()
                    continue
                name = hello.get("name") or f"{addr[0]}:{addr[1]}"
                self.clients[name] = js
            except socket.timeout:
                continue
            except Exception:
                continue

    def stop(self):
        self.running.clear()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

    def send_to(self, client_name: str, payload: dict):
        js = self.clients.get(client_name)
        if not js: return False
        try:
            js.send(payload)
            return True
        except Exception:
            self.clients.pop(client_name, None)
            return False

class EventClient(threading.Thread):
    """Connects to host and executes incoming events locally."""
    def __init__(self, server_ip, port, token, executor):
        super().__init__(daemon=True)
        self.server_ip = server_ip
        self.port = port
        self.token = token
        self.executor = executor  # object with .execute(event_dict)
        self.running = threading.Event()
        self.running.clear()
        self.sock = None
        self.js = None

    def run(self):
        self.running.set()
        while self.running.is_set():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(3.0)
                self.sock.connect((self.server_ip, self.port))
                self.js = JSONSocket(self.sock, self.token)
                self.js.send({"type": "hello", "name": socket.gethostname()})
                while self.running.is_set():
                    evt = self.js.recv(timeout=0.5)
                    if evt and evt.get("token") == self.token:
                        self.executor.execute(evt)
            except Exception:
                time.sleep(1.0)  # retry
                continue

    def stop(self):
        self.running.clear()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
