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

from locale import gettext as _

from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget
from fapolicy_analyzer.util.format import f


class RemoveDeletedDialog(UIBuilderWidget):
    def __init__(self, deleted=[], parent=None):
        def plural(count):
            return ("s", "are") if count > 1 else ("", "is")

        super().__init__()
        self.get_ref().set_transient_for(parent or self.get_ref().get_parent_window())

        display_text = f(
            _("{len(deleted)} file{plural(len(deleted))[0]} cannot be found on disk")
        )
        self.get_ref().set_property("text", display_text)
