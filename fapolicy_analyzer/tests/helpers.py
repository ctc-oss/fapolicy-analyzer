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
