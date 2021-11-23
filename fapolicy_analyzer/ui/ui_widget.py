import locale
import logging

import gi
import pkg_resources

gi.require_version("Gtk", "3.0")
from abc import ABC, ABCMeta
from dataclasses import dataclass
from importlib import resources
from typing import Callable

from fapolicy_analyzer.util.format import snake_to_camelcase
from gi.repository import Gtk
from rx.core.typing import Observable

DOMAIN = "fapolicy_analyzer"
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale_path = pkg_resources.resource_filename("fapolicy_analyzer", "locale")
locale.bindtextdomain(DOMAIN, locale_path)
locale.textdomain(DOMAIN)


class _PostInitCaller(type):
    """
    Meta class used to run the __post_init__ method after normal __init__ is run.
    This allows for initialization code to run that would require the class to be
    full initialized first.
    """

    def __call__(cls, *args, **kwargs):
        logging.debug(f"{__class__.__name__}.__call__({args}, {kwargs})")
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__(*args, **kwargs)
        return obj


class _combinedMeta(_PostInitCaller, ABCMeta):
    """
    Meta class used to combine the _PostInitCaller meta class with ABCMeta
    for Abract Base Classes
    """


class UIWidget(ABC):
    """
    Abstract Base Class for any UI Widget.
    """

    def __init__(self, ref):
        self._ref = ref

    def get_ref(self):
        return self._ref

    def dispose(self):
        if self._ref and isinstance(self._ref, Gtk.Widget):
            logging.debug(
                "distroying widget from class {}".format(self.__class__.__name__)
            )
            self._ref.destroy()
        self._dispose()

    def _dispose(self):
        """Implemented by inheriting classes to allow for extra clean code to be run."""


class UIBuilderWidget(UIWidget, ABC):
    """
    Abstract Base Class for any UI Widget that uses a glade file to load it structure.
    This class expects the glade file to be have the same file name as the widgets
    python file but with a .glade extension, and for the glade file to be located under
    the fapolicy_analyzer/glade directory.
    """

    def __init__(self, name=None):
        def gladeFile():
            filename = f"{name}.glade"
            with resources.path("fapolicy_analyzer.glade", filename) as path:
                return path.as_posix()

        name = name or self.__module__.split(".")[-1]
        self._builder = Gtk.Builder()
        self._builder.set_translation_domain(DOMAIN)
        self._builder.add_from_file(gladeFile())
        self._builder.connect_signals(self)
        UIWidget.__init__(self, self.get_object(snake_to_camelcase(name)))

    def get_object(self, name):
        return self._builder.get_object(name)


@dataclass
class UIConnectedWidget(UIBuilderWidget, metaclass=_combinedMeta):
    """
    Abstract base class for any glade based UI widgets that are connected
    to redux to retrieve state.
    """

    def __init__(
        self,
        feature: Observable,
        on_next: Callable = None,
        on_error: Callable = None,
        on_completed: Callable = None,
    ):
        UIBuilderWidget.__init__(self)
        self._feature = feature
        self._on_next = on_next
        self._on_error = on_error
        self._on_completed = on_completed
        self._subscription = None

    def __post_init__(
        self,
        feature: Observable = None,
        on_next: Callable = None,
        on_error: Callable = None,
        on_completed: Callable = None,
    ):
        self._subscription = self._feature.subscribe(
            on_next=self._on_next,
            on_error=self._on_error,
            on_completed=self._on_completed,
        )

    def _dispose(self):
        if self._subscription:
            logging.debug(
                "disposing of subscription for class {}".format(self.__class__.__name__)
            )
            self._subscription.dispose()
