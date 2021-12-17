# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import context  # noqa: F401
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui.deploy_confirm_dialog import DeployConfirmDialog


def test_creates_widget():
    widget = DeployConfirmDialog()
    assert type(widget.get_ref()) is Gtk.MessageDialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = DeployConfirmDialog(parent)
    assert widget.get_ref().get_transient_for() == parent


def test_closes_after_cancel_time(mocker):
    mocker.patch(
        "ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    widget = DeployConfirmDialog(parent=Gtk.Window(), cancel_time=1)
    result = widget.get_ref().run()
    assert result == Gtk.ResponseType.NO
