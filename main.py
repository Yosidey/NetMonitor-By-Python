import os
import sys
import psutil
import threading
import time
from pystray import Icon, MenuItem, Menu
from PIL import Image
import tkinter as tk
import json


class InternetMonitor:
    CONFIG_PATH = "config.json"
    def __init__(self):
        self.unit = "KB/s"
        self.upload_speed = 0
        self.download_speed = 0
        self.running = True
        self.text_var = None
        self.root = None
        self.text_visible = False
        self.icon = None
        self.text_position = "bottom_right"
        self.drag_mode = False
        self.offset_x = 0
        self.offset_y = 0
        self.load_config()

    # Get path to the startup shortcut
    def get_startup_shortcut_path(self):
        startup_folder = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup")
        return os.path.join(startup_folder, "InternetMonitor.lnk")

    # Check if auto start is enabled
    def is_auto_start_enabled(self):
        return os.path.exists(self.get_startup_shortcut_path())

    # Enable auto start by creating shortcut
    def enable_auto_start(self):
    
        from win32com.client import Dispatch

        target = sys.executable
        script = os.path.abspath(__file__)
        arguments = f'"{script}"' if script.endswith(".py") else ""

        shortcut_path = self.get_startup_shortcut_path()
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = os.path.dirname(script)
        shortcut.IconLocation = script
        shortcut.save()

    # Disable auto start by removing shortcut
    def disable_auto_start(self):
        shortcut_path = self.get_startup_shortcut_path()
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    def load_config(self):
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, "r") as f:
                    config = json.load(f)
                    self.drag_mode = config.get("drag_mode", False)
                    self.text_position = config.get("position", "bottom_right")
                    self.unit = config.get("unit", "KB/s")
                    if config.get("auto_start", False) and not self.is_auto_start_enabled():
                        self.enable_auto_start()
                    elif not config.get("auto_start", True) and self.is_auto_start_enabled():
                        self.disable_auto_start()
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            # Default if config doesn't exist
            self.text_position = "bottom_right"

    def save_config(self):
        config = {
            "drag_mode": self.drag_mode,
            "auto_start": self.is_auto_start_enabled(),
            "position": self.text_position,
            "unit": self.unit,
        }
        try:
            with open(self.CONFIG_PATH, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    # Load icon image
    def create_image(self):
        return Image.open("assets/monitor_internet.ico")

    def format_speed(self, speed_bytes):
        # speed_kb = speed in KB/s
        if self.unit == "MB/s":
            return speed_bytes / (1024 * 1024)  # Convert to MB/s
        return speed_bytes / 1024
    # Main monitoring logic
    def monitor(self):
        old = psutil.net_io_counters()
        while self.running:
            time.sleep(1)
            new = psutil.net_io_counters()
            upload_bytes = new.bytes_sent - old.bytes_sent
            download_bytes = new.bytes_recv - old.bytes_recv
            old = new

            self.upload_speed = self.format_speed(upload_bytes)
            self.download_speed = self.format_speed(download_bytes)

            unit = self.unit

            if self.icon:
                self.icon.title = f"Upload: {self.upload_speed:.2f} {self.unit}  | Download: {self.download_speed:.2f} {self.unit}"
                self.icon.update_menu()

            if self.root and self.text_var:
                self.root.after(0, lambda: self.text_var.set(
                    f"⬆ {self.upload_speed:.0f} {self.unit} ⬇ {self.download_speed:.0f} {self.unit}"))

           # print(f"Upload: {self.upload_speed:.2f} {self.unit} | Download: {self.download_speed:.2f} {self.unit}")

    # Position the floating text on the screen
    def position_text(self):
        if self.drag_mode:
            return
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        positions = {
            "top_left": (5, 8),
            "top_center": ((sw - w) // 2, 8),
            "top_right": (sw - w - 5, 8),
            "center": ((sw - w) // 2, (sh - h) // 2),
            "bottom_left": (5, sh - h - 42),
            "bottom_center": ((sw - w) // 2, sh - h - 42),
            "bottom_right": (sw - w - 5, sh - h - 42),
        }

        x, y = positions.get(self.text_position, ((sw - w) // 2, 5))
        self.root.geometry(f"+{x}+{y}")

    def change_unit(self, icon_, item):
        self.unit = item.text
        self.save_config()
        icon_.update_menu()
    # Change floating text position
    def change_position(self, icon_, item):
        self.text_position = item.text
        if self.root:
            self.root.after(0, self.position_text)
        self.save_config()
        icon_.update_menu()

    # Toggle drag mode for the floating window
    def toggle_drag(self, icon_, item):
        self.drag_mode = not self.drag_mode
        if self.root:
            if self.drag_mode:
                self.root.bind("<Button-1>", self.start_drag)
                self.root.bind("<B1-Motion>", self.drag)
            else:
                self.root.unbind("<Button-1>")
                self.root.unbind("<B1-Motion>")
                self.position_text()
        self.save_config()
        icon_.update_menu()

    def start_drag(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    # Toggle auto start
    def toggle_auto_start(self, icon_, item):
        if self.is_auto_start_enabled():
            self.disable_auto_start()
        else:
            self.enable_auto_start()
        self.save_config()
        icon_.update_menu()

    # Create the system tray menu
    def create_menu(self):
        menu_units = Menu(
            MenuItem("KB/s", self.change_unit, checked=lambda item: self.unit == item.text, radio=True),
            MenuItem("MB/s", self.change_unit, checked=lambda item: self.unit == item.text, radio=True),
        )
        position_menu = Menu(
            MenuItem("top_left", self.change_position, checked=lambda item: self.text_position == item.text,
                     radio=True),
            MenuItem("top_center", self.change_position, checked=lambda item: self.text_position == item.text,
                     radio=True),
            MenuItem("top_right", self.change_position, checked=lambda item: self.text_position == item.text,
                     radio=True),
            MenuItem("center", self.change_position, checked=lambda item: self.text_position == item.text, radio=True),
            MenuItem("bottom_left", self.change_position, checked=lambda item: self.text_position == item.text,
                     radio=True),
            MenuItem("bottom_center", self.change_position, checked=lambda item: self.text_position == item.text,
                     radio=True),
            MenuItem("bottom_right", self.change_position, checked=lambda item: self.text_position == item.text,
                     radio=True),
            Menu.SEPARATOR,
            MenuItem(lambda item: f"Drag Mode: {'Enabled' if self.drag_mode else 'Disabled'}",
                     self.toggle_drag, checked=lambda item: self.drag_mode),
            Menu.SEPARATOR
        )

        return Menu(
            MenuItem(lambda _: f"Upload: {self.upload_speed:.1f} {self.unit}", lambda _: None, enabled=False),
            MenuItem(lambda _: f"Download: {self.download_speed:.1f} {self.unit}", lambda _: None, enabled=False),
            Menu.SEPARATOR,
            MenuItem(lambda _: f"Text Status: {'Visible' if self.text_visible else 'Hidden'}", lambda _: None,
                     enabled=False),
            Menu.SEPARATOR,
            MenuItem("Show Text", self.show_text, enabled=lambda item: not self.text_visible),
            MenuItem("Hide Text", self.hide_text, enabled=lambda item: self.text_visible),
            Menu.SEPARATOR,
            MenuItem("Unit", menu_units),
            Menu.SEPARATOR,
            MenuItem("Text Position", position_menu),

            MenuItem(lambda item: f"Auto Start: {'Enabled' if self.is_auto_start_enabled() else 'Disabled'}",
                     self.toggle_auto_start, checked=lambda item: self.is_auto_start_enabled()),
            Menu.SEPARATOR,
            MenuItem("Exit", self.quit_program)
        )

    # Show floating text window
    def show_text(self, icon_=None, item=None):
        if self.root:
            self.root.after(0, self.root.deiconify)
            self.text_visible = True
            if icon_:
                icon_.update_menu()

    # Hide floating text window
    def hide_text(self, icon_=None, item=None):
        if self.root:
            self.root.after(0, self.root.withdraw)
            self.text_visible = False
            if icon_:
                icon_.update_menu()

    # Quit the program safely
    def quit_program(self, icon_, item):
        self.running = False
        if self.root:
            self.root.after(0, self.root.destroy)
        icon_.stop()

    # Initialize the floating window
    def init_view(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.configure(bg="black")

        self.text_var = tk.StringVar()
        self.text_var.set("⬆ 0 KB/s ⬇ 0 KB/s")

        label = tk.Label(self.root, textvariable=self.text_var, fg="lime", bg="black", font=("Segoe UI", 10))
        label.pack(padx=5, pady=2)

        self.position_text()
        self.root.withdraw()
        self.text_visible = False

        threading.Thread(target=self.monitor, daemon=True).start()
        self.root.mainloop()

    # Main entry point
    def run(self):
        self.icon = Icon("Internet Monitor", icon=self.create_image(), menu=self.create_menu())
        threading.Thread(target=self.icon.run, daemon=True).start()
        self.init_view()


if __name__ == "__main__":
    app = InternetMonitor()
    app.run()
