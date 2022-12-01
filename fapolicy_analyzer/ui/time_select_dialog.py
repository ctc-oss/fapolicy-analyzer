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

from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget


class TimeSelectDialog(UIBuilderWidget):

    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)

    def set_time_unit(self, unit_id):
        self.get_object("timeComboBox").set_active_id(unit_id)

    def set_time_number(self, time_number):
        buff = self.get_object("timeEntryField").get_buffer()
        buff.set_text(str(time_number), len(str(time_number)))

    def get_time_unit(self):
        return self.get_object("timeComboBox").get_active_id()

    def get_time_number(self):
        return int(self.get_object("timeEntryField").get_buffer().get_text())

    def get_unit_str(self):
        unit_id = self.get_time_unit()
        if unit_id == "1":
            display_unit = "Minute"
        elif unit_id == "2":
            display_unit = "Hour"
        elif unit_id == "3":
            display_unit = "Day"
        return display_unit

    def get_seconds(self):
        unit_id = self.get_time_unit()
        time_val = self.get_time_number()
        if unit_id == "1":
            seconds = time_val * 60
        elif unit_id == "2":
            seconds = time_val * 3600
        elif unit_id == "3":
            seconds = time_val * 86400
        return seconds
