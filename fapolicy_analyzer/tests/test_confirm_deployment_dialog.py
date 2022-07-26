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
from fapolicy_analyzer.ui.changeset_wrapper import TrustChangeset
from fapolicy_analyzer.ui.confirm_deployment_dialog import ConfirmDeploymentDialog
from fapolicy_analyzer.ui.strings import (
    CHANGESET_ACTION_ADD_TRUST,
    CHANGESET_ACTION_DEL_TRUST,
)

from helpers import delayed_gui_action

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


def test_creates_widget():
    widget = ConfirmDeploymentDialog([], None, None, parent=Gtk.Window())
    assert type(widget) is ConfirmDeploymentDialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = ConfirmDeploymentDialog([], None, None, parent=parent).get_ref()
    assert widget.get_transient_for() == parent


def test_dialog_actions_responses(mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    dialog = ConfirmDeploymentDialog([], None, None, parent=Gtk.Window()).get_ref()
    for expected in [Gtk.ResponseType.YES, Gtk.ResponseType.NO]:
        button = dialog.get_widget_for_response(expected)
        delayed_gui_action(button.clicked, delay=1)
        response = dialog.run()
        assert response == expected


def test_load_path_action_list():
    changeset = TrustChangeset()
    changeset.add("/tmp/add.txt")
    changeset.delete("/tmp/del.txt")
    widget = ConfirmDeploymentDialog([changeset], None, None, Gtk.Window())
    view = widget.get_object("changesTreeView")
    rows = [x for x in view.get_model()]
    assert (CHANGESET_ACTION_ADD_TRUST, "/tmp/add.txt") in [(r[0], r[1]) for r in rows]
    assert (CHANGESET_ACTION_DEL_TRUST, "/tmp/del.txt") in [(r[0], r[1]) for r in rows]
