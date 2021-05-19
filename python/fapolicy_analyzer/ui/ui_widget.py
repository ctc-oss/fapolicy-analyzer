import os
import sys
import locale
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from abc import ABC

domain = "fapolicy_analyzer"
locale_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../locale")
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale.bindtextdomain(domain, locale_path)
locale.textdomain(domain)
# translate = gettext.translation("", localedir, fallback=True)


class UIWidget(ABC):
    def __init__(self):
        gladeFile = self.absolute_file_path(
            f"../../glade/{self.__module__.split('.')[-1]}.glade"
        )
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(domain)
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)

    def absolute_file_path(self, relativePath):
        """
        Creates an absolute file path using the relative path from the implementing class
        """
        return os.path.abspath(
            os.path.join(
                os.path.dirname(sys.modules[self.__module__].__file__), relativePath
            )
        )

    def get_object(self, name):
        return self.builder.get_object(name)
