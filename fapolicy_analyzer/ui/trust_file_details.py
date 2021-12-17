# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
from .ui_widget import UIBuilderWidget


class TrustFileDetails(UIBuilderWidget):
    def clear(self):
        self.set_in_database_view("")
        self.set_on_file_system_view("")
        self.set_trust_status("")

    def set_in_database_view(self, text):
        self.get_object("inDatabaseView").get_buffer().set_text(text)

    def set_on_file_system_view(self, text):
        self.get_object("onFileSystemView").get_buffer().set_text(text)

    def set_trust_status(self, text):
        self.get_object("fileTrustStatusView").get_buffer().set_text(text)
