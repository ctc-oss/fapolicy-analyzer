# Copyright Concurrent Technologies Corporation 2023
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
from fapolicy_analyzer.ui.rules.rules_difference_dialog import RulesDifferenceDialog
from unittest.mock import MagicMock

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


def test_creates_widget(mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_difference_dialog.rules_difference",
        return_value="",
    )
    widget = RulesDifferenceDialog(MagicMock(), MagicMock(), parent=Gtk.Window())
    assert type(widget) is RulesDifferenceDialog
