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

import gi
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage

import fapolicy_analyzer.ui.strings as strings
from fapolicy_analyzer.ui.ancillary_trust_database_admin import (
    AncillaryTrustDatabaseAdmin,
)
from fapolicy_analyzer.ui.system_trust_database_admin import SystemTrustDatabaseAdmin
from fapolicy_analyzer.ui.ui_widget import UIWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # isort: skip


class DatabaseAdminPage(UIWidget, UIPage):
    def __init__(self):
        self.notebook = Gtk.Notebook()
        UIWidget.__init__(self, self.notebook)
        actions = {
            "toggle": [
                UIAction(
                    name="Toggle",
                    tooltip="Toggle Displaying Trusted Entries",
                    icon="media-playlist-repeat",
                    signals={"clicked": self.on_trust_toggle_clicked},
                    sensitivity_func=self.trust_toggle_sensitivity,
                )
            ],
        }
        UIPage.__init__(self, actions)

        self.ancillaryTrustDbAdmin = AncillaryTrustDatabaseAdmin()
        self.systemTrustDbAdmin = SystemTrustDatabaseAdmin()
        self.systemTrustDbAdmin.file_added_to_ancillary_trust += (
            self.on_added_to_ancillary_trust
        )

        self.notebook.append_page(
            self.systemTrustDbAdmin.get_ref(),
            Gtk.Label(label=strings.SYSTEM_TRUST_TAB_LABEL),
        )
        self.notebook.append_page(
            self.ancillaryTrustDbAdmin.get_ref(),
            Gtk.Label(label=strings.ANCILLARY_TRUST_TAB_LABEL),
        )

        self.notebook.set_current_page(1)
        self.notebook.show_all()

    def on_added_to_ancillary_trust(self, *files):
        self.ancillaryTrustDbAdmin.add_trusted_files(*files)

    def on_trust_toggle_clicked(self, *args):
        self.systemTrustDbAdmin.trust_file_list.show_trusted = not self.systemTrustDbAdmin.trust_file_list.show_trusted
        self.systemTrustDbAdmin.trust_file_list.refresh()

    def trust_toggle_sensitivity(self):
        return self.systemTrustDbAdmin.trust_file_list.loading_sensitive

    def _dispose(self):
        self.ancillaryTrustDbAdmin.dispose()
        self.systemTrustDbAdmin.dispose()
