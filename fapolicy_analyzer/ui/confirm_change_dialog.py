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


class ConfirmChangeDialog(UIBuilderWidget):
    def __init__(self, parent=None, total=0, additions=0, deletions=0):
        def plural(count):
            return "s" if count > 1 else ""

        super().__init__()

        if parent:
            self.get_ref().set_transient_for(parent)

        textView = self.get_object("confirmInfo")
        textBuffer = textView.get_buffer()
        total_changes = additions + deletions

        untrusted = (
            f(_("{deletions} file{plural(deletions)} will be untrusted."))
            if deletions
            else ""
        )
        trusted = (
            f(_("{additions} file{plural(additions)} will be trusted."))
            if additions
            else ""
        )
        no_action = (
            f(
                _(
                    "{total - (total_changes)} file{plural(total - (total_changes))} "
                    "from the System Trust Database will be unaffected."
                )
            )
            if total > total_changes
            else ""
        )
        display_text = " ".join(
            [
                *[m for m in [untrusted, trusted, no_action] if m],
                _("Do you wish to continue?"),
            ]
        )

        textBuffer.set_text(display_text)
