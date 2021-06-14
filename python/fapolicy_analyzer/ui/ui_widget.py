import locale
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from abc import ABC
from importlib import resources


DOMAIN = "fapolicy_analyzer"
locale.setlocale(locale.LC_ALL, locale.getlocale())
with resources.path("fapolicy_analyzer", "locale") as path:
    locale.bindtextdomain(DOMAIN, path)
locale.textdomain(DOMAIN)


class UIWidget(ABC):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(DOMAIN)
        self.builder.add_from_file(self.__gladeFile())
        self.builder.connect_signals(self)

    def __gladeFile(self):
        filename = f"{self.__module__.split('.')[-1]}.glade"
        with resources.path("fapolicy_analyzer.glade", filename) as path:
            return path.as_posix()

    def get_object(self, name):
        return self.builder.get_object(name)
