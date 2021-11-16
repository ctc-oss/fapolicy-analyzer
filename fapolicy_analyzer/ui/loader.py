import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf
from importlib import resources
from .strings import LOADER_MESSAGE
from .ui_widget import UIBuilderWidget


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
