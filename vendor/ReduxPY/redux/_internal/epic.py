# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
"""
    Implements epic specific functions
"""

from functools import partial
from inspect import getfullargspec
from logging import getLogger
from typing import Iterable, cast

from rx import Observable, merge
from rx.core.typing import Mapper

from .types import Epic

logger = getLogger(__name__)


def _wrapped_epic(epic: Mapper[Observable, Observable],
                  action_: Observable, _: Observable) -> Observable:
    return epic(action_)


def normalize_epic(epic: Epic) -> Epic:
    """Creates a callback for an epic that expects two arguments

    Args:
        epic: the epic

    Returns:
        the normalized epic
    """
    count = len(getfullargspec(epic)[0])
    assert count in (1, 2)
    return epic if count == 2 else cast(Epic, partial(_wrapped_epic, epic))


def _run_epic(action_: Observable, state_: Observable, epic: Epic) -> Observable:
    return epic(action_, state_)


def run_epic(action_: Observable, state_: Observable) -> Mapper[Epic, Observable]:
    """ Runs a single epic agains the given action and state observables

        Args:
            action_: the action observable
            state_: the state observable

        Returns:
            A callback function that will run the given epic on the observables
    """

    assert isinstance(action_, Observable)
    assert isinstance(state_, Observable)

    return partial(_run_epic, action_, state_)


def _combine_epics(
    norm_epics: Iterable[Epic],
    action_: Observable, state_: Observable
) -> Observable:
    """ Merges the epics into one

        Args:
            action_: the action observable
            state_: the state observable

        Returns:
            the merged epic
    """
    return merge(*map(run_epic(action_, state_), norm_epics))


def combine_epics(*epics: Iterable[Epic]) -> Epic:
    """ Combines a sequence of epics into one single epic by merging them

        Args:
            epics: the epics to merge

        Returns:
            The merged epic
    """
    return partial(_combine_epics, tuple(map(normalize_epic, epics)))
