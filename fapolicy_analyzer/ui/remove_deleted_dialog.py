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

from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget


class RemoveDeletedDialog(UIBuilderWidget):
    def __init__(self, deleted=[], parent=None):
        def plural(count):
            return ("s", "are") if count > 1 else ("", "is")

        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)

        textView = self.get_object("removeInfo")
        textBuffer = textView.get_buffer()

        n_deleted = len(deleted)
        displayText = f"{n_deleted} file{plural(n_deleted)[0]} cannot be found on disc"
        textBuffer.set_text(displayText)
