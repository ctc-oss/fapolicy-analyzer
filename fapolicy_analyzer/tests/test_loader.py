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

import context  # noqa: F401 # isort: skip
import gi
import pytest
from fapolicy_analyzer.ui.loader import Loader
from fapolicy_analyzer.ui.strings import LOADER_MESSAGE

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture
def widget():
    return Loader()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box
    assert widget.get_object("message").get_label() == LOADER_MESSAGE


def test_displays_custom_message():
    widget = Loader("Hello")
    assert widget.get_object("message").get_label() == "Hello"


def test_displays_animation(widget):
    assert widget.get_object("image").get_visible()


def test_hides_animation_if_cannot_load(mocker):
    mocker.patch("fapolicy_analyzer.ui.resources.path", return_value="bad path")
    widget = Loader()
    assert not widget.get_object("image").get_visible()
