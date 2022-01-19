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
from fapolicy_analyzer.util.format import f
from locale import gettext as _


class ConfirmChangeDialog(UIBuilderWidget):
    def __init__(self, parent=None, n_total=0, n_atdb=0):
        super().__init__()

        if parent:
            self.get_ref().set_transient_for(parent)

        textView = self.get_object("confirmInfo")
        textBuffer = textView.get_buffer()

        if n_atdb > 0:
            display_text = f(_("""{n_total} files will be untrusted.
 {n_total - n_atdb} files from the System Trust Database will be unaffected. Untrust selected files?"""))
        else:
            display_text = f(_("{n_total} files will be trusted. Trust selected files?"))

        textBuffer.set_text(display_text)
