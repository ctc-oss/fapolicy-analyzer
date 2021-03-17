import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from abc import ABC


class UIWidget(ABC):
    def __init__(self):
        gladeFile = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../glade/",
                f"{self.__module__.split('.')[-1]}.glade",
            )
        )
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)
