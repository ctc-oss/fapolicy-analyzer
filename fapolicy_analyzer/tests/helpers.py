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

import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from time import sleep
from threading import Thread


def refresh_gui(delay=0.1, max_retries=1):
    while Gtk.events_pending():
        Gtk.main_iteration_do(blocking=False)
    sleep(delay)
    if Gtk.events_pending() and max_retries:
        refresh_gui(max_retries=max_retries - 1)
    elif Gtk.events_pending:
        logging.warning("helpers::refresh_gui::Exceeded max_retries")


def delayed_gui_action(action, delay=0.1, *args):
    def wrapper():
        sleep(delay)
        action(*args)

    thread = Thread(target=wrapper)
    thread.daemon = True
    thread.start()
