from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence


@dataclass
class UIAction:
    name: str
    tooltip: str
    icon: str
    signals: Mapping[str, Callable]
    sensitivity_func: Callable[..., bool] = lambda: True


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
    actions: Mapping[str, Sequence[UIAction]] = field(default_factory=dict)

    @staticmethod
    def merge_actions(
        actions1: Mapping[str, Sequence[UIAction]],
        actions2: Mapping[str, Sequence[UIAction]],
    ) -> Mapping[str, Sequence[UIAction]]:
        """
        Static util method to merge 2 sets of actions into a new set of actions
        """
        result = {k: [*v] for k, v in actions1.items()}  # copy actions 1
        for k, v in actions2.items():
            result[k] = [*result.get(k, []), *v]  # merge group from action 1 with 2
        return result
