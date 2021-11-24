import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from .system_trust_database_admin import SystemTrustDatabaseAdmin
from .ui_widget import UIWidget


class DatabaseAdminPage(UIWidget):
    def __init__(self):
        notebook = Gtk.Notebook()
        super().__init__(notebook)

        self.ancillaryTrustDbAdmin = AncillaryTrustDatabaseAdmin()
        self.systemTrustDbAdmin = SystemTrustDatabaseAdmin()
        self.systemTrustDbAdmin.file_added_to_ancillary_trust += (
            self.on_added_to_ancillary_trust
        )

        notebook.append_page(
            self.systemTrustDbAdmin.get_ref(),
            Gtk.Label(label=strings.SYSTEM_TRUST_TAB_LABEL),
        )
        notebook.append_page(
            self.ancillaryTrustDbAdmin.get_ref(),
            Gtk.Label(label=strings.ANCILLARY_TRUST_TAB_LABEL),
        )

        notebook.set_current_page(1)
        notebook.show_all()

    def on_added_to_ancillary_trust(self, file):
        self.ancillaryTrustDbAdmin.add_trusted_files(file)

    def _dispose(self):
        self.ancillaryTrustDbAdmin.dispose()
        self.systemTrustDbAdmin.dispose()
