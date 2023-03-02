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

from typing import List, Tuple

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class FileChooserDialog(Gtk.FileChooserDialog):
    """
    Overrides the Gtk.FileChooserDialog class to create a reusable dialog. The get_filename and get_filenames
    methods are overridden to encapsulate the displaying and hiding of the dialog.
    """

    def __init__(
        self,
        title: str,
        parent: Gtk.Window,
        action: Gtk.FileChooserAction = Gtk.FileChooserAction.OPEN,
        action_button: str = Gtk.STOCK_OPEN,
        do_overwrite_confirmation: bool = False,
        filters: List[Tuple[str, str]] = [],
    ):
        super().__init__(
            title=title,
            transient_for=parent,
            action=action,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                action_button,
                Gtk.ResponseType.OK,
            ),
        )
        # self.add_buttons(
        #     Gtk.STOCK_CANCEL,
        #     Gtk.ResponseType.CANCEL,
        #     action_button,
        #     Gtk.ResponseType.OK,
        # )
        self.set_do_overwrite_confirmation(do_overwrite_confirmation)
        self.__add_filters(*filters)

        # self.show_all()

    def __add_filters(self, *filters: Tuple[str, str]):
        for f in filters:
            name, pattern = f
            fileFilterTgz = Gtk.FileFilter()
            fileFilterTgz.set_name(name)
            fileFilterTgz.add_pattern(pattern)
            self.add_filter(fileFilterTgz)

    def __run_and_hide(self) -> Gtk.ResponseType:
        response = self.run()
        self.hide()
        return response

    def get_filename(self):
        """
        Overrides the Gtk.FileChooserDialog.get_filename function. Will display the dialog and return the selected
        filename if the response type is OK. Otherwise None is returned.
        """
        response = self.__run_and_hide()
        return super().get_filename() if response == Gtk.ResponseType.OK else None

    def get_filenames(self):
        """
        Overrides the Gtk.FileChooserDialog.get_filenames function. Will display the dialog and return the selected
        filenames as a list if the response type is OK. Otherwise an empty list is returned. This forces the
        select_multiple property of the dialog to be True.
        """
        self.set_select_multiple(True)
        response = self.__run_and_hide()
        return super().get_filenames() if response == Gtk.ResponseType.OK else []
