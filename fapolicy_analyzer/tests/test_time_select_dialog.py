# Copyright Concurrent Technologies Corporation 2022
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
import pytest

from fapolicy_analyzer.ui.time_select_dialog import (
    TimeSelectDialog,
)
gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk


@pytest.fixture
def widget():
    return TimeSelectDialog(Gtk.Window())


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Dialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = TimeSelectDialog(parent)
    assert widget.get_ref().get_transient_for() == parent
    
    
def test_start_time_sensitive_toggle(widget):
    widget.get_object("ignoreStartTime").set_active(True)
    assert widget.get_object("startMinute").get_sensitive() == False
    assert widget.get_object("stopMinute").get_sensitive() == True
    

def test_stop_time_sensitive_toggle(widget):
    widget.get_object("ignoreStopTime").set_active(True)
    assert widget.get_object("startMinute").get_sensitive() == True
    assert widget.get_object("stopMinute").get_sensitive() == False
    
def test_both_sensitive_toggle(widget):
    widget.get_object("ignoreStopTime").set_active(True)
    widget.get_object("ignoreStartTime").set_active(True)
    assert widget.get_object("startMinute").get_sensitive() == False
    assert widget.get_object("stopMinute").get_sensitive() == False
