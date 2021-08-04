import locale
import gi
import pkg_resources

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from abc import ABC
from importlib import resources
from util.format import snake_to_camelcase


DOMAIN = "fapolicy_analyzer"
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale_path = pkg_resources.resource_filename("fapolicy_analyzer", "locale")
locale.bindtextdomain(DOMAIN, locale_path)
locale.textdomain(DOMAIN)


class UIWidget(ABC):
    def __init__(self, name=None):
        def gladeFile():
            filename = f"{name}.glade"
            with resources.path("fapolicy_analyzer.glade", filename) as path:
                return path.as_posix()

        name = name or self.__module__.split(".")[-1]
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(DOMAIN)
        self.builder.add_from_file(gladeFile())
        self.builder.connect_signals(self)
        self.ref = self.get_object(snake_to_camelcase(name))

    def get_object(self, name):
        return self.builder.get_object(name)

    def get_ref(self):
        return self.ref
