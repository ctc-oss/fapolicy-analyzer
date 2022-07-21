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

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from fapolicy_analyzer.ui.strings import LOADER_MESSAGE
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import GdkPixbuf  # isort: skip


class Loader(UIBuilderWidget):
    def __init__(self, message=LOADER_MESSAGE):
        super().__init__()
        with resources.path(
            "fapolicy_analyzer.resources", "filled_fading_balls.gif"
        ) as path:
            animation = GdkPixbuf.PixbufAnimation.new_from_file(path.as_posix())

        image = self.get_object("image")
        image.set_from_animation(animation)
        self.get_object("message").set_label(message)
