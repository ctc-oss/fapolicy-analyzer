import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from time import sleep
from threading import Thread


def refresh_gui(delay=0.1):
    while Gtk.events_pending():
        Gtk.main_iteration_do(blocking=False)
    sleep(delay)
    if Gtk.events_pending():
        refresh_gui()


def delayed_gui_action(action, delay=0.1, *args):
    def wrapper():
        sleep(delay)
        action(*args)

    thread = Thread(target=wrapper)
    thread.daemon = True
    thread.start()
