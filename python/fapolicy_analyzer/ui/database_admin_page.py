import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from fapolicy_analyzer import System
from .ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from .system_trust_database_admin import SystemTrustDatabaseAdmin


class DatabaseAdminPage:
    def __init__(self):
        system = System()
        self.notebook = Gtk.Notebook()
        self.notebook.append_page(
            SystemTrustDatabaseAdmin(system).get_content(),
            Gtk.Label(label="System Trust Database"),
        )
        self.notebook.append_page(
            AncillaryTrustDatabaseAdmin(system).get_content(),
            Gtk.Label(label="Ancillary Trust Database"),
        )
        self.notebook.show_all()

    def get_content(self):
        return self.notebook
