# OneShare Input (MVP)

Comparte un solo teclado y mouse entre varias computadoras (Windows 10 y macOS 11+). 
Permite definir la **ubicación relativa de las pantallas** (izquierda/derecha/arriba/abajo) para saber hacia dónde
pasar el control cuando el cursor cruza el borde.

> **Nota:** Este es un MVP pensado para demostración/POC. No reemplaza a soluciones maduras como Barrier / Input Leap.
> Requiere permisos de accesibilidad en macOS y puede pedir privilegios de administrador para inyección de eventos.

## Características (MVP)
- Rol **Host** (equipo con teclado/mouse físicos) y **Client** (equipo remoto que recibe eventos).
- Mapa simple de pantallas: puedes ubicar un cliente a la **izquierda** o **derecha** (y básico para arriba/abajo).
- Cuando el cursor en el Host cruza un borde, el control pasa al Client; los eventos se envían por red.
- Encriptación ligera de canal mediante **token compartido** (no TLS; para redes confiables en MVP).
- Interfaz con **PySide6** para configurar nodos, probar conexión y arrancar/pausar.

## Requisitos
- Python 3.10+ recomendado.
- Dependencias: `pip install -r requirements.txt`

```
PySide6>=6.6
pynput>=1.7.7
pyautogui>=0.9.54
pyperclip>=1.9.0
screeninfo>=0.8.1
```

> En macOS puede requerir: `xcode-select --install` y dar permisos en **Preferencias del Sistema → Seguridad y privacidad → Accesibilidad**.

## Uso rápido
1. En **todas** las máquinas, copia esta carpeta y ejecuta:
   ```bash
   pip install -r requirements.txt
   python -m app.main
   ```
2. En cada máquina, abre **OneShare Input**. En **Ajustes**:
   - Define un **Token compartido** (el mismo en todas).
   - Elige **Rol: Host** en el equipo con el teclado/mouse. En los demás, **Rol: Client**.
   - En **Clientes** del Host agrega cada equipo remoto con su **IP** y **posición relativa** (izquierda/derecha/arriba/abajo).
3. Pulsa **Guardar**. Luego **Iniciar** en todas. En el Host, mueve el ratón hacia el borde configurado.

## Empaquetado (instaladores)
### Windows 10+
Requiere `pyinstaller`:
```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name OneShareInput --icon app/icon.ico app/main.py
```
El ejecutable quedará en `dist/OneShareInput/OneShareInput.exe`.

### macOS 11+ (Intel/ARM)
PyInstaller también soporta .app básico:
```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name OneShareInput --icon app/icon.icns app/main.py
```
El bundle estará en `dist/OneShareInput.app`. Para distribuir fuera de tu Mac, consulta firmas y notarización de Apple.

> **Permisos macOS:** la primera ejecución pedirá acceso a Accesibilidad y Grabación de Pantalla para inyectar/capturar eventos.

## Limitaciones del MVP
- Latencia optimizada para LAN, no cifra con TLS (solo token); usa red confiable.
- Mapa de pantallas simple (bordes). Multi‑display por equipo soportado de forma básica (usa bordes del escritorio virtual).
- No implementa file‑drag entre equipos ni sincronización de portapapeles avanzada (sí copia simple).

## Licencia
MIT. Úsalo bajo tu propio riesgo.


## Instaladores
### Windows (NSIS)
1) Ejecuta `build\windows\build_exe.bat`.
2) Instala NSIS y ejecuta `build\windows\make_installer.bat` → genera `OneShareInput-Setup-0.1.0.exe`.

### macOS (DMG)
1) Corre `build/macos/build_app.sh`.
2) Luego `build/macos/make_dmg.sh` → genera `dist/OneShareInput-0.1.0.dmg`.
