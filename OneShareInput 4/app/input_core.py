from __future__ import annotations
import threading, time
from pynput import mouse, keyboard
import pyautogui
from screeninfo import get_monitors

class LocalDesktop:
    def __init__(self):
        self.monitors = get_monitors()
        # bounds of virtual desktop
        self.left = min(m.x for m in self.monitors)
        self.top = min(m.y for m in self.monitors)
        self.right = max(m.x + m.width for m in self.monitors)
        self.bottom = max(m.y + m.height for m in self.monitors)
        self.width = self.right - self.left
        self.height = self.bottom - self.top

class EventExecutor:
    """Executes incoming events (client side)."""
    def __init__(self):
        self.k = keyboard.Controller()
        self.m = mouse.Controller()

    def execute(self, evt: dict):
        t = evt.get("type")
        d = evt.get("data", {})
        if t == "mouse_move":
            self.m.position = (d.get("x", 0), d.get("y", 0))
        elif t == "mouse_click":
            btn = mouse.Button.left if d.get("button") == "left" else mouse.Button.right
            if d.get("pressed"):
                self.m.press(btn)
            else:
                self.m.release(btn)
        elif t == "mouse_scroll":
            self.m.scroll(d.get("dx",0), d.get("dy",0))
        elif t == "key_event":
            # d = {"key": "a", "pressed": True}
            ch = d.get("key")
            if not ch: return
            key_obj = getattr(keyboard.Key, ch, None)
            if key_obj is None and len(ch) == 1:
                key_obj = ch
            if not key_obj: return
            if d.get("pressed"):
                self.k.press(key_obj)
            else:
                self.k.release(key_obj)

class HostController(threading.Thread):
    """Captures local events and decides whether to route to local or a remote client based on edges."""
    def __init__(self, server, layout_clients):
        super().__init__(daemon=True)
        self.server = server            # EventServer
        self.layout_clients = layout_clients  # [{"name","ip","port","position"}]
        self.active_remote = None       # name of client currently owning cursor
        self.desktop = LocalDesktop()
        self.m = mouse.Controller()
        self.k = keyboard.Controller()
        self._running = threading.Event()
        self._running.clear()

    def run(self):
        self._running.set()
        m_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        k_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        m_listener.start(); k_listener.start()
        while self._running.is_set():
            time.sleep(0.1)

    def stop(self):
        self._running.clear()

    def border_hit(self, pos):
        x,y = pos
        tol = 1  # pixel
        if x <= self.desktop.left + tol:
            return "left"
        if x >= self.desktop.right - tol:
            return "right"
        if y <= self.desktop.top + tol:
            return "up"
        if y >= self.desktop.bottom - tol:
            return "down"
        return None

    def pick_client_for_border(self, border):
        # simple mapping: first client matching position
        for c in self.layout_clients:
            if c.get("position") == {"left":"left","right":"right","up":"up","down":"down"}[border]:
                name = c.get("name") or f"{c.get('ip')}:{c.get('port')}"
                return name
        return None

    # ------------- listeners -------------
    def on_move(self, x, y):
        border = self.border_hit((x,y))
        if border and not self.active_remote:
            target = self.pick_client_for_border(border)
            if target:
                self.active_remote = target
                # pin cursor to edge to avoid leaving screen
                if border == "left":
                    self.m.position = (self.desktop.left+1, y)
                elif border == "right":
                    self.m.position = (self.desktop.right-1, y)
                elif border == "up":
                    self.m.position = (x, self.desktop.top+1)
                elif border == "down":
                    self.m.position = (x, self.desktop.bottom-1)
                return  # do not send move locally
        if self.active_remote:
            # while remote active, send to remote. Esc brings cursor back.
            self.server.send_to(self.active_remote, {"type":"mouse_move","data":{"x":x,"y":y}})

    def on_click(self, x, y, button, pressed):
        if self.active_remote:
            btn = "left" if str(button).endswith("left") else "right"
            self.server.send_to(self.active_remote, {"type":"mouse_click","data":{"button":btn,"pressed":pressed}})

    def on_scroll(self, x, y, dx, dy):
        if self.active_remote:
            self.server.send_to(self.active_remote, {"type":"mouse_scroll","data":{"dx":dx,"dy":dy}})

    def on_press(self, key):
        if self.active_remote:
            if key == keyboard.Key.esc:
                # return control locally
                self.active_remote = None
                return
            name = None
            try:
                name = key.name if hasattr(key, "name") else key.char
            except Exception:
                pass
            if not name: return
            self.server.send_to(self.active_remote, {"type":"key_event","data":{"key":name,"pressed":True}})

    def on_release(self, key):
        if self.active_remote:
            name = None
            try:
                name = key.name if hasattr(key, "name") else key.char
            except Exception:
                pass
            if not name: return
            self.server.send_to(self.active_remote, {"type":"key_event","data":{"key":name,"pressed":False}})
