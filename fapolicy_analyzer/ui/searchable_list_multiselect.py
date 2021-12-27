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

gi.require_version("Gtk", "3.0")
from events import Events
from gi.repository import Gtk
from .searchable_list import SearchableList

from .ui_widget import UIBuilderWidget
from .loader import Loader

class SearchableListMultiselect(SearchableList):

    def __init__(
        self,
        **kwargs
    ):
    
        super().__init__(selection_type='multi', **kwargs)


