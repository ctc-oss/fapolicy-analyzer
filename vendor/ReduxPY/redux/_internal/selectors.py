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
    Selector related helper functions
"""
from operator import is_
from typing import Callable, TypeVar

import rx.operators as op
from rx import Observable, pipe
from rx.subject import ReplaySubject

T1 = TypeVar('T1')
T2 = TypeVar('T2')
Mapper = Callable[[T1], T2]


def select(selector: Mapper[T1, T2]
           ) -> Callable[[Observable], Observable]:
    """ Reactive operator that applies a selector
        and shares the result across multiple subscribers

        Args:
            selector: the selector function

        Returns:
            The reactive operator
    """
    return pipe(
        op.map(selector),
        op.distinct_until_changed(comparer=is_),
        op.multicast(subject=ReplaySubject(1)),
        op.ref_count(),
    )
