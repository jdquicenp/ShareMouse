from __future__ import annotations
import json, os, threading

DEFAULT_CONFIG = {
    "role": "host",  # "host" or "client"
    "token": "CHANGE_ME",
    "host_bind": "0.0.0.0",
    "host_port": 49999,
    "server_ip": "",  # used on clients
    "server_port": 49999,
    "clients": [
        # {"name": "Oficina", "ip": "192.168.1.20", "port": 49999, "position": "right"}
    ]
}

class AppConfig:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.data.update(d)
            except Exception:
                pass

    def save(self):
        with self._lock:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
