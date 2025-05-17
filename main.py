import psutil
import threading
import time
from pystray import Icon, MenuItem, Menu
from PIL import Image
import tkinter as tk

class MonitorInternet:
    def __init__(self):
        self.upload_speed = 0
        self.download_speed = 0
        self.running = True
        self.texto_var = None
        self.root = None
        self.texto_visible = False
        self.icon = None
        self.posicion_texto = "arriba_centro"
        self.modo_arrastre = False
        self.offset_x = 0
        self.offset_y = 0

    def create_image(self):
        return Image.open("assets/monitor_internet.ico")

    def monitor(self):
        old = psutil.net_io_counters()
        while self.running:
            time.sleep(1)
            new = psutil.net_io_counters()
            self.upload_speed = (new.bytes_sent - old.bytes_sent) / 1024
            self.download_speed = (new.bytes_recv - old.bytes_recv) / 1024
            old = new

            if self.icon:
                self.icon.title = f"Subida: {self.upload_speed:.2f} KB/s | Bajada: {self.download_speed:.2f} KB/s"
                self.icon.update_menu()

            if self.root and self.texto_var:
                self.root.after(0, lambda: self.texto_var.set(f"⬆ {self.upload_speed:.0f} KB/s ⬇ {self.download_speed:.0f} KB/s"))

            print(f"Subida: {self.upload_speed:.2f} KB/s | Bajada: {self.download_speed:.2f} KB/s")

    def position_text(self):
        if self.modo_arrastre:
            return  # No posicionar si el modo arrastre está activo
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        position = {
            "arriba_izquierda": (5, 5),
            "arriba_centro": ((sw - w) // 2, 5),
            "arriba_derecha": (sw - w - 5, 5),
            "centro": ((sw - w) // 2, (sh - h) // 2),
            "abajo_izquierda": (5, sh - h - 40),
            "abajo_centro": ((sw - w) // 2, sh - h - 40),
            "abajo_derecha": (sw - w - 5, sh - h - 40),
        }

        x, y = position.get(self.posicion_texto, ((sw - w) // 2, 5))
        self.root.geometry(f"+{x}+{y}")

    def change_position(self, icon_, item):
        self.posicion_texto = item.text
        if self.root:
            self.root.after(0, self.position_text)
        icon_.update_menu()

    def toggle_arrastre(self, icon_, item):
        self.modo_arrastre = not self.modo_arrastre
        if self.root:
            if self.modo_arrastre:
                self.root.bind("<Button-1>", self.iniciar_arrastre)
                self.root.bind("<B1-Motion>", self.arrastrar)
            else:
                self.root.unbind("<Button-1>")
                self.root.unbind("<B1-Motion>")
                self.position_text()
        icon_.update_menu()

    def iniciar_arrastre(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def arrastrar(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def create_menu(self):
        menu_positions = Menu(
            MenuItem("arriba_izquierda", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            MenuItem("arriba_centro", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            MenuItem("arriba_derecha", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            MenuItem("centro", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            MenuItem("abajo_izquierda", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            MenuItem("abajo_centro", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            MenuItem("abajo_derecha", self.change_position, checked=lambda item: self.posicion_texto == item.text, radio=True),
            Menu.SEPARATOR,
            MenuItem(lambda item: f"Modo arrastre: {'activado' if self.modo_arrastre else 'desactivado'}", self.toggle_arrastre, checked=lambda item: self.modo_arrastre)
        )

        return Menu(
            MenuItem(lambda _: f"Subida: {self.upload_speed:.1f} KB/s", lambda _: None, enabled=False),
            MenuItem(lambda _: f"Bajada: {self.download_speed:.1f} KB/s", lambda _: None, enabled=False),
            Menu.SEPARATOR,
            MenuItem(lambda _: f"Estado del texto: {'Visible' if self.texto_visible else 'Oculto'}", lambda _: None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Mostrar texto", self.show_text, enabled=lambda item: not self.texto_visible),
            MenuItem("Ocultar texto", self.hide_text, enabled=lambda item: self.texto_visible),
            Menu.SEPARATOR,
            MenuItem("Posición texto", menu_positions),
            Menu.SEPARATOR,
            MenuItem("Salir", self.quit_program)
        )

    def show_text(self, icon_=None, item=None):
        if self.root:
            self.root.after(0, self.root.deiconify)
            self.texto_visible = True
            if icon_:
                icon_.update_menu()

    def hide_text(self, icon_=None, item=None):
        if self.root:
            self.root.after(0, self.root.withdraw)
            self.texto_visible = False
            if icon_:
                icon_.update_menu()

    def quit_program(self, icon_, item):
        self.running = False
        if self.root:
            self.root.after(0, self.root.destroy)
        icon_.stop()

    def init_view(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.configure(bg="black")

        self.texto_var = tk.StringVar()
        self.texto_var.set("⬆ 0 KB/s ⬇ 0 KB/s")

        label = tk.Label(self.root, textvariable=self.texto_var, fg="lime", bg="black", font=("Segoe UI", 10))
        label.pack(padx=5, pady=2)

        self.position_text()
        self.root.withdraw()
        self.texto_visible = False

        threading.Thread(target=self.monitor, daemon=True).start()
        self.root.mainloop()

    def run(self):
        self.icon = Icon("Monitor Internet", icon=self.create_image(), menu=self.create_menu())
        threading.Thread(target=self.icon.run, daemon=True).start()
        self.init_view()

if __name__ == "__main__":
    app = MonitorInternet()
    app.run()
