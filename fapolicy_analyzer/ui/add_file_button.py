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

import logging
import re
from os import path

import gi
from events import Events

from fapolicy_analyzer.ui import strings
from fapolicy_analyzer.ui.file_chooser_dialog import FileChooserDialog
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class AddFileButton(UIBuilderWidget, Events):
    __events__ = ["files_added"]

    def __init__(self):
        UIBuilderWidget.__init__(self)
        Events.__init__(self)
        self.dialog = self.get_object("fileChooserDialog")

    def addFileButton_clicked(self, *args):
        fcd = FileChooserDialog(
            title=strings.ADD_FILE_LABEL,
            parent=self.get_ref().get_toplevel(),
            action_button=Gtk.STOCK_ADD,
        )
        files = [f for f in fcd.get_filenames() if path.isfile(f)]

        # -- Filter to address fapolicyd embedded whitespace in path issue
        # fapolicyd issue 109:Files and Directories with spaces in the name
        #
        # Detect and remove file paths w/embedded spaces. Alert user w/dlg
        logging.info("Filtering out paths with embedded whitespace")
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
