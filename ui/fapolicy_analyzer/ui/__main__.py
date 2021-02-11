import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from main_window import MainWindow


if __name__ == "__main__":
    main = MainWindow()
    Gtk.main()
