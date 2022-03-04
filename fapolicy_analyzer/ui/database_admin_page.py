# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import fapolicy_analyzer.ui.strings as strings
import gi
from fapolicy_analyzer.ui.ui_page import UIPage

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .ancillary_trust_database_admin import AncillaryTrustDatabaseAdmin
from .system_trust_database_admin import SystemTrustDatabaseAdmin
from .ui_widget import UIWidget


class DatabaseAdminPage(UIWidget, UIPage):
    def __init__(self):
        notebook = Gtk.Notebook()
        UIWidget.__init__(self, notebook)
        UIPage.__init__(self)

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

    def on_added_to_ancillary_trust(self, *files):
        self.ancillaryTrustDbAdmin.add_trusted_files(*files)

    def _dispose(self):
        self.ancillaryTrustDbAdmin.dispose()
        self.systemTrustDbAdmin.dispose()
