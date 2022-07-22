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
import re
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from events import Events
from os import path
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget


class AddFileButton(UIBuilderWidget, Events):
    __events__ = ["files_added"]

    def __init__(self):
        UIBuilderWidget.__init__(self)
        Events.__init__(self)
        self.dialog = self.get_object("fileChooserDialog")

    def addFileButton_clicked(self, *args):
        fcd = Gtk.FileChooserDialog(
            title=strings.ADD_FILE_LABEL,
            transient_for=self.get_ref().get_toplevel(),
            action=Gtk.FileChooserAction.OPEN,
        )
        fcd.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_ADD,
            Gtk.ResponseType.OK,
        )
        fcd.set_select_multiple(True)
        response = fcd.run()
        fcd.hide()
        if response == Gtk.ResponseType.OK:
            files = [f for f in fcd.get_filenames() if path.isfile(f)]

            # -- Filter to address fapolicyd embeded whitspace in path issue
            # fapolicyd issue 109:Files and Directories with spaces in the name
            #
            # Detect and remove file paths w/embedded spaces. Alert user w/dlg
            print("Filtering out paths with embedded whitespace")
            listAccepted = [e for e in files if not re.search(r"\s", e)]
            listRejected = [e for e in files if re.search(r"\s", e)]
            if listRejected:
                dlgWhitespaceInfo = Gtk.MessageDialog(
                    transient_for=self.get_ref().get_toplevel(),
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=strings.WHITESPACE_WARNING_DIALOG_TITLE,
                )

                # Convert list of paths to a single string
                strListRejected = "\n".join(listRejected)

                dlgWhitespaceInfo.format_secondary_text(
                    strings.WHITESPACE_WARNING_DIALOG_TEXT + strListRejected
                )
                dlgWhitespaceInfo.run()
                dlgWhitespaceInfo.destroy()
            files = listAccepted
            #     Remove this filter block if fapolicyd bug #TBD is fixed
            # ----------------------------------------------------------------

            if files:
                self.files_added(files)
        fcd.destroy()
