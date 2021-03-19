import os
import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from abc import ABC


class UIWidget(ABC):
    def __init__(self):
        gladeFile = self.absolute_file_path(
            f"../../glade/{self.__module__.split('.')[-1]}.glade"
        )
        self.builder = Gtk.Builder()
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
