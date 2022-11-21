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

import datetime
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget


class TimeSelectDialog(UIBuilderWidget):

    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)

        current_time = datetime.datetime.now()
        time_delta = datetime.timedelta(hours=1)
        start_time = current_time - time_delta

        self.get_object("stopMinute").set_value(current_time.minute)
        self.get_object("stopHour").set_value(current_time.hour)
        self.get_object("stopDay").get_buffer().set_text(str(current_time.day), len(str(current_time.day)))
        self.get_object("stopMonth").set_active_id(str(current_time.month))
        self.get_object("stopYear").get_buffer().set_text(str(current_time.year), len(str(current_time.year)))

        self.get_object("startMinute").set_value(start_time.minute)
        self.get_object("startHour").set_value(start_time.hour)
        self.get_object("startDay").get_buffer().set_text(str(start_time.day), len(str(start_time.day)))
        self.get_object("startMonth").set_active_id(str(start_time.month))
        self.get_object("startYear").get_buffer().set_text(str(start_time.year), len(str(start_time.year)))

    def on_ignoreStartTime_toggled(self, *args):
        self.get_object("startMinute").set_sensitive(not self.get_object("startMinute").get_sensitive())
        self.get_object("startHour").set_sensitive(not self.get_object("startHour").get_sensitive())
        self.get_object("startDay").set_sensitive(not self.get_object("startDay").get_sensitive())
        self.get_object("startMonth").set_sensitive(not self.get_object("startMonth").get_sensitive())
        self.get_object("startYear").set_sensitive(not self.get_object("startYear").get_sensitive())

    def on_ignoreStopTime_toggled(self, *args):
        self.get_object("stopMinute").set_sensitive(not self.get_object("stopMinute").get_sensitive())
        self.get_object("stopHour").set_sensitive(not self.get_object("stopHour").get_sensitive())
        self.get_object("stopDay").set_sensitive(not self.get_object("stopDay").get_sensitive())
        self.get_object("stopMonth").set_sensitive(not self.get_object("stopMonth").get_sensitive())
        self.get_object("stopYear").set_sensitive(not self.get_object("stopYear").get_sensitive())

    def get_time(self, sos="start"):
        time_dict = {sos + "Minute": self.get_object(sos + "Minute").get_value_as_int(),
                     sos + "Hour": self.get_object(sos + "Hour").get_value_as_int(),
                     sos + "Day": self.get_object(sos + "Day").get_buffer().get_text(),
                     sos + "Month": int(self.get_object(sos + "Month").get_active_id()),
                     sos + "Year": self.get_object(sos + "Year").get_buffer().get_text(),
                     }
        try:
            time_dict[sos + "Day"] = int(time_dict[sos + "Day"])
        except TypeError:
            error_text = f"{sos.capitalize()} day field could not be converted to an integer"
            self.get_object("errorMessage").get_buffer().set_text(error_text, len(error_text))

        try:
            time_dict[sos + "Year"] = int(time_dict[sos + "Year"])
        except TypeError:
            error_text = f"{sos.capitalize()} year field could not be converted to an integer"
            self.get_object("errorMessage").get_buffer().set_text(error_text, len(error_text))

        try:
            date = datetime.datetime(year=time_dict[sos + "Year"],
                                     month=time_dict[sos + "Month"],
                                     day=time_dict[sos + "Day"],
                                     hour=time_dict[sos + "Hour"],
                                     minute=time_dict[sos + "Minute"],
                                     )

        except ValueError:
            error_text = "Could not convert provided information into "
            self.get_object("errorMessage").get_buffer().set_text(error_text, len(error_text))
            date = None

        return date
