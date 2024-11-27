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
from abc import ABC, ABCMeta
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Sequence

import gi
from rx.core.typing import Observable

from fapolicy_analyzer.ui import DOMAIN, get_resource
from fapolicy_analyzer.util.format import snake_to_camelcase

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


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
        self._builder = Gtk.Builder()
        self._builder.set_translation_domain(DOMAIN)

        name = name or self.__module__.split(".")[-1]
        glade = get_resource(f"{name}.glade")

        if not glade:
            logging.error(f"Resource {name}.glade is not available.")
        else:
            self._builder.add_from_string(glade)

        self._builder.connect_signals(self)
        print(name)
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
        feature: Optional[Observable] = None,
        on_next: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_completed: Optional[Callable] = None,
        features: Sequence[Dict[Observable, Dict[str, Callable]]] = [],
    ):
        if not feature and not features:
            raise TypeError(
                "UIConnectedWidget.__init__() no feature parameters provided"
            )

        UIBuilderWidget.__init__(self)

        single = (
            {
                feature: {
                    "on_next": on_next,
                    "on_error": on_error,
                    "on_completed": on_completed,
                }
            }
            if feature
            else {}
        )
        self.__features = [single, *features]
        self.__subscriptions = None

    def __post_init__(
        self,
        *args,
        **kwargs,
    ):
        self.__subscriptions = [
            feature.subscribe(
                on_next=handlers.get("on_next"),
                on_error=handlers.get("on_error"),
                on_completed=handlers.get("on_completed"),
            )
            for feature_details in self.__features
            for feature, handlers in feature_details.items()
        ]

    def _dispose(self):
        if self.__subscriptions:
            for subscription in self.__subscriptions:
                logging.debug(
                    "disposing of subscription for class {}".format(
                        self.__class__.__name__
                    )
                )
                subscription.dispose()
