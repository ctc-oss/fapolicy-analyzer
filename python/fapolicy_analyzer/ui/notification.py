import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from importlib import resources
from threading import Timer
from .ui_widget import UIWidget
from .state_manager import stateManager, NotificationType


class Notification(UIWidget):
    def __init__(self, timer_duration=10):
        super().__init__()
        stateManager.system_notification_added += self.on_system_notification_added
        self.revealer = self.builder.get_object("notification")
        self.message = self.builder.get_object("message")
        self.container = self.builder.get_object("container")
        self.closeBtn = self.builder.get_object("closeBtn")
        self.timerDuration = timer_duration
        self.timer = None

        styleProvider = Gtk.CssProvider()
        with resources.path("fapolicy_analyzer.css", "notification.css") as path:
            styleProvider.load_from_file(Gio.File.new_for_path(path.as_posix()))

        self.style = self.container.get_style_context()
        self.style.add_provider(styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.closeBtn.get_style_context().add_provider(
            styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def __start_timer(self):
        self.timer = Timer(self.timerDuration, self.closeBtn.clicked)
        self.timer.start()

    def __stop_timer(self):
        self.timer.cancel()
        self.timer = None

    def get_content(self):
        return self.revealer

    def on_system_notification_added(self, notification):
        if notification and notification.count:
            message = notification[0]
            notificationType = notification[1]
            self.style.add_class(notificationType.value)
            self.message.set_label(message)
            self.revealer.set_reveal_child(True)

            if notificationType not in [NotificationType.ERROR, NotificationType.WARN]:
                self.__start_timer()

    def on_closeBtn_clicked(self, *args):
        if self.timer:
            self.__stop_timer()
        self.revealer.set_reveal_child(False)
        stateManager.remove_system_notification()
