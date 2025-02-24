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

import logging
from os import path
from typing import Optional
from urllib.parse import ParseResult, urlparse, urlunparse

import gi

gi.require_version("Gtk", "3.0")
try:
    gi.require_version("WebKit2", "4.0")
except Exception:
    gi.require_version("WebKit2", "4.1")

from gi.repository import Gtk, WebKit2


class HelpBrowser(Gtk.Window):
    def __init__(
        self, *args, uri: Optional[str] = None, allow_navigation: bool = True, **kwargs
    ):
        super().__init__(
            type=Gtk.WindowType.TOPLEVEL,
            *args,
            window_position=Gtk.WindowPosition.CENTER,
            title="Fapolicy Analyzer Help",
            **kwargs,
        )
        self.add(self.__build_content(allow_navigation))
        self.set_size_request(800, 600)
        self.show_all()

        if uri:
            self.load_uri(uri)

    def __build_content(self, allow_navigation) -> Gtk.VBox:
        content = Gtk.VBox()
        scrolled_window = Gtk.ScrolledWindow()

        context = WebKit2.WebContext()
        self.webview = WebKit2.WebView.new_with_context(context)
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

    def __handle_load_changed(self, *args):
        self.go_back.set_sensitive(self.webview.can_go_back())
        self.go_forward.set_sensitive(self.webview.can_go_forward())

    def __handle_help_scheme(self, uri_parts: ParseResult):
        def uri_to_file_path(base: str):
            _file = path.join(base, uri_parts.path)
            if path.exists(_file):
                return _file
            return None

        _file = None
        base_dirs = [
            "/usr/share/help/C",
            path.join(path.expanduser("~"), ".local/share/help/C"),
        ]
        for base in base_dirs:
            _file = uri_to_file_path(base)
            if _file:
                break

        if not _file:
            logging.warning(f"Cannot load URI {urlunparse(uri_parts)}")
            self.webview.load_html("No help documentation found!")
            return

        # uncomment for displaying the webview developer tools for debugging
        # self.webview.get_settings().set_enable_developer_extras(True)
        # self.webview.get_inspector().show()

        self.webview.get_settings().set_allow_file_access_from_file_urls(True)
        self.webview.load_uri(f"file://{_file}")

    def load_uri(self, uri: str):
        uri_parts = urlparse(uri)
        if uri_parts.scheme == "help":
            self.__handle_help_scheme(uri_parts)
        else:
            self.webview.load_uri(uri)
