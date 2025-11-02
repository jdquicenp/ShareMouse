from __future__ import annotations
import os, sys, json, threading
from PySide6 import QtCore, QtWidgets, QtGui

class ClientRow(QtWidgets.QWidget):
    def __init__(self, name="", ip="", port=49999, position="right"):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.name = QtWidgets.QLineEdit(name); self.name.setPlaceholderText("Nombre")
        self.ip = QtWidgets.QLineEdit(ip); self.ip.setPlaceholderText("IP / host")
        self.port = QtWidgets.QSpinBox(); self.port.setRange(1,65535); self.port.setValue(port)
        self.pos = QtWidgets.QComboBox(); self.pos.addItems(["left","right","up","down"]); self.pos.setCurrentText(position)
        self.remove_btn = QtWidgets.QPushButton("Eliminar")
        for w in (self.name, self.ip, self.port, self.pos, self.remove_btn):
            layout.addWidget(w)

class MainWindow(QtWidgets.QMainWindow):
    startHost = QtCore.Signal()
    stopHost = QtCore.Signal()
    startClient = QtCore.Signal()
    stopClient = QtCore.Signal()

    def __init__(self, appcfg):
        super().__init__()
        self.setWindowTitle("OneShare Input (MVP)")
        self.resize(860, 520)
        self.appcfg = appcfg
        self._build_ui()

    def _build_ui(self):
        w = QtWidgets.QWidget(); self.setCentralWidget(w)
        root = QtWidgets.QVBoxLayout(w)

        # Role & Token
        boxTop = QtWidgets.QGroupBox("Ajustes generales")
        top = QtWidgets.QFormLayout(boxTop)
        self.role = QtWidgets.QComboBox(); self.role.addItems(["host","client"]); self.role.setCurrentText(self.appcfg.get("role","host"))
        self.token = QtWidgets.QLineEdit(self.appcfg.get("token","CHANGE_ME")); self.token.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.host_ip = QtWidgets.QLineEdit(self.appcfg.get("host_bind","0.0.0.0"))
        self.host_port = QtWidgets.QSpinBox(); self.host_port.setRange(1,65535); self.host_port.setValue(self.appcfg.get("host_port",49999))
        self.server_ip = QtWidgets.QLineEdit(self.appcfg.get("server_ip",""))
        self.server_port = QtWidgets.QSpinBox(); self.server_port.setRange(1,65535); self.server_port.setValue(self.appcfg.get("server_port",49999))

        top.addRow("Rol:", self.role)
        top.addRow("Token:", self.token)
        top.addRow("Host bind (Host):", self.host_ip)
        top.addRow("Host puerto:", self.host_port)
        top.addRow("IP del Host (Client):", self.server_ip)
        top.addRow("Puerto del Host:", self.server_port)

        root.addWidget(boxTop)

        # Clients list (only visible for host)
        self.clientsBox = QtWidgets.QGroupBox("Clientes (solo Host)")
        cl = QtWidgets.QVBoxLayout(self.clientsBox)
        self.clientsArea = QtWidgets.QVBoxLayout(); cl.addLayout(self.clientsArea)
        self.addClientBtn = QtWidgets.QPushButton("Agregar cliente")
        cl.addWidget(self.addClientBtn, alignment=QtCore.Qt.AlignLeft)
        root.addWidget(self.clientsBox)

        self.client_rows = []
        for c in self.appcfg.get("clients",[]):
            row = ClientRow(c.get("name",""), c.get("ip",""), c.get("port",49999), c.get("position","right"))
            self._add_client_row(row)

        self.addClientBtn.clicked.connect(lambda: self._add_client_row(ClientRow()))

        # Start/Stop buttons
        btns = QtWidgets.QHBoxLayout()
        self.btnStart = QtWidgets.QPushButton("Iniciar")
        self.btnStop = QtWidgets.QPushButton("Detener")
        self.btnSave = QtWidgets.QPushButton("Guardar")
        btns.addWidget(self.btnSave); btns.addStretch(1); btns.addWidget(self.btnStart); btns.addWidget(self.btnStop)
        root.addLayout(btns)

        self.role.currentTextChanged.connect(self._update_visibility)
        self._update_visibility()

    def _add_client_row(self, row: ClientRow):
        self.client_rows.append(row)
        self.clientsArea.addWidget(row)
        row.remove_btn.clicked.connect(lambda: self._remove_client_row(row))

    def _remove_client_row(self, row: ClientRow):
        row.setParent(None)
        self.client_rows.remove(row)

    def _update_visibility(self):
        is_host = (self.role.currentText() == "host")
        self.clientsBox.setVisible(is_host)

    def read_config_from_ui(self):
        data = dict(self.appcfg.data)
        data["role"] = self.role.currentText()
        data["token"] = self.token.text()
        data["host_bind"] = self.host_ip.text()
        data["host_port"] = int(self.host_port.value())
        data["server_ip"] = self.server_ip.text()
        data["server_port"] = int(self.server_port.value())
        if self.clientsBox.isVisible():
            clients = []
            for r in self.client_rows:
                clients.append({"name": r.name.text(), "ip": r.ip.text(), "port": int(r.port.value()), "position": r.pos.currentText()})
            data["clients"] = clients
        return data
