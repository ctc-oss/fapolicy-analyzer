import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TrustFileDetails:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/trust_file_details.glade")
        self.builder.connect_signals(self)

    def get_content(self):
        return self.builder.get_object("trustFileDetails")

    def set_In_Database_View(self, text):
        self.builder.get_object("inDatabaseView").get_buffer().set_text(text)
