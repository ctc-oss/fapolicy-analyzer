from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, Dict, Sequence


@dataclass
class UIAction:
    name: str
    tooltip: str
    icon: str
    signals: Dict[str, Callable]


@dataclass
class UIPage(ABC):
    """
    Abstract Base Class for a main content pages in the UI
    """

    """
    A dictionary of UI actions that can be performed on the Page. The key is a string
    defining the grouping name of the actions and the value is a list of UIActions for
    the group.
    """
    actions: Dict[str, Sequence[UIAction]] = field(default_factory=dict)
