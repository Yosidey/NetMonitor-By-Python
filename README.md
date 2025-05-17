# NetMonitor by Python

### English
NetMonitor is a lightweight open source tool to monitor your internet upload and download speeds in real-time. It runs silently in the system tray and optionally displays a floating text window on the screen with live speed updates.
#### Features:
- Real-time upload and download speed monitoring (KB/s)
- System tray icon with live speed display
- Floating text overlay with customizable position on screen, always visible over other applications.
- Easy to use and minimal system resource usage
- Cross-platform with Python (tested on Windows)
- Open source and free to use, modify, and distribute

### Spanish
NetMonitor es una herramienta ligera y de código abierto para monitorear la velocidad de subida y bajada de internet en tiempo real. Funciona silenciosamente en la bandeja del sistema y opcionalmente muestra un texto flotante en pantalla con actualizaciones en vivo de la velocidad.
#### Características:
- Monitoreo en tiempo real de velocidad de subida y bajada (KB/s)
- Icono en bandeja del sistema con visualización de velocidad actual
- Texto flotante personalizable en posición de pantalla, siempre visible sobre otras aplicaciones.
- Fácil de usar y bajo consumo de recursos
- Multiplataforma con Python (probado en Windows)
- Código abierto, libre para usar, modificar y distribuir


## Screenshots
#### Icon Monitor
![Icon Monitor](assets/Icon_Monitor.png)
#### Icon Monitor Panel
![Icon Monitor Panel](assets/Icon_Panel_Monitor.png)
#### Text Monitor
![Text Monitor](assets/Text_Monitor.png)
### Installation / Instalación
#### Requirements / Requisitos
- Python 3.7 or higher / Python 3.7 o superior
- pip (Python package manager)
- `psutil`
- `pystray`
- `Pillow`
- `tkinter`
- Windows OS (tested, other OS may require adjustments)



## 🧪 Development setup
1. Clone the repository:
``` git clone https://github.com/your_user/MonitorInternet.git ```
2. Enter the project
``` cd netmonitor ``` 
3. Install the dependencies with:
``` pip install -r requirements.txt```
4. Run the program:
``` python main.py ```

## ⚙️ Build executable 
1. To create a standalone executable (Windows):
```pyinstaller --onefile --add-data "assets/monitor_internet.ico;assets" --windowed --icon=assets/monitor_internet.ico main.py ```

## 🛠 Installer with Inno Setup
1. Build executable using PyInstaller (see above).
2. Use [Inno Setup](https://jrsoftware.org/isinfo.php) with this script (installer.iss):


## 📥 Descargas / Downloads

- 🔽 [**Descargar Ejecutable** (MonitorInternet.exe)](./dist/main.exe)
- 💿 [**Descargar Instalador** (Setup.exe)](./Output/NetMonitorSetup.exe)


## 🖥️ Usage
1. Run the installer or the .exe file.
2. You'll see the icon in the system tray.
3. Use the menu to show, hide, position, or move the hover text.