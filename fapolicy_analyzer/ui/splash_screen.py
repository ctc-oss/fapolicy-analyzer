import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib
from .main_window import MainWindow
from .store import get_system_feature
from .ui_widget import UIWidget


class SplashScreen(UIWidget):
    def __init__(self):
        super().__init__()
        self.progressBar = self.get_object("progressBar")
        self.window = self.get_ref()
        self.window.show_all()

        self.subscription = get_system_feature().subscribe(on_next=self.on_next_system)
        self.timeout_id = GLib.timeout_add(100, self.on_timeout, None)
        self.progressBar.pulse()

    def on_next_system(self, system):
        if system.get("initialized", False):
            self.subscription.dispose()
            self.window.destroy()
            MainWindow()

    def on_timeout(self, *args):
        self.progressBar.pulse()
        return True
