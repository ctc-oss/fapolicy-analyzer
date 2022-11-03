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


import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2


class HelpBrowser(Gtk.Window):
    def __init__(self, uri="", *args, **kwargs):
        super().__init__(*args, **kwargs)

        content = Gtk.VBox()
        scrolled_window = Gtk.ScrolledWindow()
        webview = WebKit2.WebView()
        webview.load_uri("file:///usr/share/help/C/fapolicy-analyzer/User-Guide.html")
        scrolled_window.add(webview)

        go_back = Gtk.Button("Back")
        go_back.connect("clicked", lambda x: webview.go_back())
        go_forward = Gtk.Button("Forward")
        go_forward.connect("clicked", lambda x: webview.go_forward())

        button_bar = Gtk.HBox()
        button_bar.pack_start(go_back, False, False, 0)
        button_bar.pack_start(go_forward, False, False, 0)

        content.pack_start(button_bar, False, False, 0)
        content.pack_start(scrolled_window, True, True, 0)

        self.add(content)
        self.set_size_request(800, 800)
        self.show_all()
