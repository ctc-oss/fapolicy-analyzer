import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from .system_trust_database_admin import SystemTrustDatabaseAdmin


class DatabaseAdminPage:
    def __init__(self):
        self.notebook = Gtk.Notebook()

        self.ancillaryTrustDbAdmin = AncillaryTrustDatabaseAdmin()
        self.systemTrustDbAdmin = SystemTrustDatabaseAdmin()
        self.systemTrustDbAdmin.file_added_to_ancillary_trust += (
            self.on_added_to_ancillary_trust
        )

        self.notebook.append_page(
            self.systemTrustDbAdmin.get_content(),
            Gtk.Label(label=strings.SYSTEM_TRUST_TAB_LABEL),
        )
        self.notebook.append_page(
            self.ancillaryTrustDbAdmin.get_content(),
            Gtk.Label(label=strings.ANCILLARY_TRUST_TAB_LABEL),
        )

        self.notebook.set_current_page(1)
        self.notebook.show_all()

    def get_content(self):
        return self.notebook

    def on_added_to_ancillary_trust(self, file):
        self.ancillaryTrustDbAdmin.add_trusted_files(file)
