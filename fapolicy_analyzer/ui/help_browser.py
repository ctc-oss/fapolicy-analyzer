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


from os import path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gio, Gtk, WebKit2


class HelpBrowser(Gtk.Window):
    def __init__(self, *args, uri: str = None, allow_navigation: bool = True, **kwargs):
        super().__init__(
            Gtk.WindowType.TOPLEVEL,
            *args,
            window_position=Gtk.WindowPosition.CENTER,
            title="Fapolicy Analyzer Help",
            **kwargs
        )
        self.__register_help_scheme()
        self.add(self.__build_content(allow_navigation))
        self.set_size_request(800, 600)
        self.show_all()

        if uri:
            self.load_uri(uri)

    def __build_content(self, allow_navigation) -> Gtk.VBox:
        content = Gtk.VBox()
        scrolled_window = Gtk.ScrolledWindow()
        self.webview = WebKit2.WebView()
        scrolled_window.add(self.webview)

        if allow_navigation:
            self.webview.connect("load_changed", self.__handle_load_changed)
            self.go_back = Gtk.Button.new_from_icon_name(
                "go-previous", Gtk.IconSize.BUTTON
            )
            self.go_back.connect("clicked", lambda x: self.webview.go_back())
            self.go_forward = Gtk.Button.new_from_icon_name(
                "go-next", Gtk.IconSize.BUTTON
            )
            self.go_forward.connect("clicked", lambda x: self.webview.go_forward())

            button_bar = Gtk.HBox()
            button_bar.pack_start(self.go_back, False, False, 0)
            button_bar.pack_start(self.go_forward, False, False, 0)

            content.pack_start(button_bar, False, False, 0)

        content.pack_start(scrolled_window, True, True, 0)
        return content

    def __register_help_scheme(self):
        context = WebKit2.WebContext.get_default()
        context.register_uri_scheme("help", self.__handle_help_scheme)

    def __handle_help_scheme(self, request: WebKit2.URISchemeRequest, *args):
        def open_stream(base, rel_path):
            full_path = path.join(base, rel_path)
            if path.isdir(full_path):
                full_path = path.join(full_path, "index.html")
            if path.isfile(full_path):
                return Gio.File.new_for_path(full_path).read()
            return None

        global_dir = "/usr/share/help/C"
        local_dir = path.join(path.expanduser("~"), ".local/share/help/C")
        rel_path = request.get_path()

        stream = open_stream(global_dir, rel_path)
        if not stream:
            stream = open_stream(local_dir, rel_path)
        if not stream:
            stream = Gio.File.new_tmp().read()

        request.finish(stream, -1, None)

    def __handle_load_changed(self, *args):
        self.go_back.set_sensitive(self.webview.can_go_back())
        self.go_forward.set_sensitive(self.webview.can_go_forward())

    def load_uri(self, uri: str):
        self.webview.load_uri(uri)
