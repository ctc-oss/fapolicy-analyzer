import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from trust_database_admin import TrustDatabaseAdmin, Trust_Database_Type


class TrustDatabasePage:
    def __init__(self):
        self.notebook = Gtk.Notebook()
        systemTrustTab = TrustDatabaseAdmin(Trust_Database_Type.SYSTEM)
        self.notebook.append_page(
            systemTrustTab.get_content(), Gtk.Label(label="System Trust Database")
        )
        ancillaryTrustTab = TrustDatabaseAdmin(Trust_Database_Type.ANCILLARY)
        self.notebook.append_page(
            ancillaryTrustTab.get_content(), Gtk.Label(label="Ancillary Trust Database")
        )
        self.notebook.show_all()

    def get_content(self):
        return self.notebook
