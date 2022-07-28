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

import context  # noqa: F401 # isort: skip
import gi
import pytest
from fapolicy_analyzer.ui.analyzer_selection_dialog import (
    ANALYZER_SELECTION,
    AnalyzerSelectionDialog,
)

from helpers import delayed_gui_action

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk, Gdk  # isort: skip


@pytest.fixture
def widget():
    return AnalyzerSelectionDialog(Gtk.Window())


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Dialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = AnalyzerSelectionDialog(parent)
    assert widget.get_ref().get_transient_for() == parent


def test_trust_database_admin_selection(widget):
    trustAdminBtn = widget.get_object("adminTrustDatabasesBtn")
    delayed_gui_action(trustAdminBtn.clicked)
    result = widget.get_selection()
    assert result == ANALYZER_SELECTION.TRUST_DATABASE_ADMIN


def test_analyze_from_audit(widget):
    widget.get_object("auditLogTxt").set_text("foo")
    delayed_gui_action(widget.get_object("analyzeAuditBtn").clicked)
    result = widget.get_selection()
    assert result == ANALYZER_SELECTION.ANALYZE_FROM_AUDIT
    assert widget.get_data() == "foo"


def test_set_audit_file_from_dialog(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.analyzer_selection_dialog.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.analyzer_selection_dialog.Gtk.FileChooserDialog.get_filename",
        return_value="foo",
    )
    mocker.patch(
        "fapolicy_analyzer.ui.analyzer_selection_dialog.path.isfile", return_value=True
    )
    auditLogTxt = widget.get_object("auditLogTxt")
    auditLogTxt.emit("icon_press", Gtk.EntryIconPosition.SECONDARY, Gdk.Event())
    assert auditLogTxt.get_text() == "foo"


def test_does_nothing_on_primary_icon(widget):
    auditLogTxt = widget.get_object("auditLogTxt")
    auditLogTxt.set_text("foo")
    assert auditLogTxt.get_text() == "foo"
    auditLogTxt.emit("icon_press", Gtk.EntryIconPosition.PRIMARY, Gdk.Event())
    assert auditLogTxt.get_text() == "foo"
