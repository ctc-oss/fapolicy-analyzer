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

import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from mocks import mock_System
from ui.database_admin_page import DatabaseAdminPage
from ui.store import init_store


@pytest.fixture
def widget(mocker):
    mocker.patch(
        "ui.database_admin_page.AncillaryTrustDatabaseAdmin.get_ref",
        return_value=Gtk.Box(),
    )
    mocker.patch(
        "ui.database_admin_page.AncillaryTrustDatabaseAdmin._AncillaryTrustDatabaseAdmin__load_trust"
    )
    mocker.patch(
        "ui.database_admin_page.SystemTrustDatabaseAdmin.get_ref",
        return_value=Gtk.Box(),
    )
    mocker.patch(
        "ui.database_admin_page.SystemTrustDatabaseAdmin._SystemTrustDatabaseAdmin__load_trust"
    )
    init_store(mock_System())
    return DatabaseAdminPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Notebook


def test_appends_system_db_admin_tab(widget):
    content = widget.get_ref()
    page = content.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert content.get_tab_label_text(page) == "System Trust Database"


def test_appends_ancillary_db_admin_tab(widget):
    content = widget.get_ref()
    page = content.get_nth_page(1)
    assert type(page) is Gtk.Box
    assert content.get_tab_label_text(page) == "Ancillary Trust Database"


def test_handles_system_trust_file_add(widget, mocker):
    mocker.patch.object(widget.ancillaryTrustDbAdmin, "add_trusted_files")
    widget.systemTrustDbAdmin.file_added_to_ancillary_trust("foo")
    widget.ancillaryTrustDbAdmin.add_trusted_files.assert_called_with("foo")
