import gi
import fapolicy_analyzer as fa
from fapolicy_analyzer import util

# from https://python-gtk-3-tutorial.readthedocs.io/en/latest/builder.html

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()

    def onButtonPressed(self, button):
        s = util.example_trust_entry()
        e = fa.parse_trust_entry(s)
        print(f"{e.path} {e.size} {e.hash}")


builder = Gtk.Builder()
builder.add_from_file("../glade/button.glade")
builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()

Gtk.main()
