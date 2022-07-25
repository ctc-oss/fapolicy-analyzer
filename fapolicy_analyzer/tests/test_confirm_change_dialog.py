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

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from locale import gettext as _

from fapolicy_analyzer.util.format import f
from gi.repository import Gtk
from fapolicy_analyzer.ui.confirm_change_dialog import ConfirmChangeDialog


def _get_dialog_message(dialog):
    buff = dialog.get_buffer()
    start = buff.get_start_iter()
    end = buff.get_end_iter()
    return buff.get_text(start, end, False)


def test_creates_widget():
    widget = ConfirmChangeDialog(parent=Gtk.Window())
    assert type(widget) is ConfirmChangeDialog


def test_confirm_trust_dialog_message():
    n_files = 2
    widget = ConfirmChangeDialog(parent=Gtk.Window(), total=n_files, additions=n_files)
    dialog_string = _get_dialog_message(widget.get_object("confirmInfo"))
    assert_string = f(_("{n_files} files will be trusted. Do you wish to continue?"))
    assert dialog_string == assert_string


def test_confirm_untrust_dialog_message():
    n_files = 2
    widget = ConfirmChangeDialog(parent=Gtk.Window(), total=n_files, deletions=n_files)
    dialog_string = _get_dialog_message(widget.get_object("confirmInfo"))
    assert_string = f(_("{n_files} files will be untrusted. Do you wish to continue?"))
    assert dialog_string == assert_string


def test_confirm_untrust_mixed_dialog_message():
    n_files, n_ancillary = 2, 1
    widget = ConfirmChangeDialog(
        parent=Gtk.Window(), total=n_files, deletions=n_ancillary
    )
    buff = widget.get_object("confirmInfo").get_buffer()
    start = buff.get_start_iter()
    end = buff.get_end_iter()
    dialog_string = buff.get_text(start, end, False)
    assert_string = f(
        _(
            "{n_ancillary} file will be untrusted. {n_files - n_ancillary} file from the System "
            "Trust Database will be unaffected. Do you wish to continue?"
        )
    )
    assert dialog_string == assert_string
