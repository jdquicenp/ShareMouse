from __future__ import annotations
import os, sys, json, threading
from PySide6 import QtWidgets, QtGui
from app.config import AppConfig
from app.gui import MainWindow
from app.network import EventServer, EventClient
from app.input_core import HostController, EventExecutor

def app_config_path():
    base = os.path.join(os.path.expanduser("~"), ".oneshare_input")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "config.json")

def main():
    cfg = AppConfig(app_config_path())

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(cfg)

    server_ref = {"server": None}
    host_ref = {"host": None}
    client_ref = {"client": None}

    def start_clicked():
        data = win.read_config_from_ui()
        cfg.data.update(data); cfg.save()

        if data["role"] == "host":
            # start server and host controller
            if server_ref["server"] is None:
                server = EventServer(data["host_bind"], data["host_port"], data["token"])
                server.start()
                server_ref["server"] = server
            if host_ref["host"] is None:
                host = HostController(server_ref["server"], data.get("clients",[]))
                host.start()
                host_ref["host"] = host
        else:
            if client_ref["client"] is None:
                executor = EventExecutor()
                client = EventClient(data["server_ip"], data["server_port"], data["token"], executor)
                client.start()
                client_ref["client"] = client

        QtWidgets.QMessageBox.information(win, "OneShare", "Servicios iniciados.")

    def stop_clicked():
        if host_ref["host"]:
            host_ref["host"].stop()
            host_ref["host"] = None
        if server_ref["server"]:
            server_ref["server"].stop()
            server_ref["server"] = None
        if client_ref["client"]:
            client_ref["client"].stop()
            client_ref["client"] = None
        QtWidgets.QMessageBox.information(win, "OneShare", "Servicios detenidos.")

    def save_clicked():
        data = win.read_config_from_ui()
        cfg.data.update(data); cfg.save()
        QtWidgets.QMessageBox.information(win, "OneShare", "Configuración guardada.")

    win.btnStart.clicked.connect(start_clicked)
    win.btnStop.clicked.connect(stop_clicked)
    win.btnSave.clicked.connect(save_clicked)

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
