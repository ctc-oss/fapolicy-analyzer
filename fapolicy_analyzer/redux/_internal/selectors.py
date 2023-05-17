# Copyright 2021 Dr. Carsten Leue
# Copyright Concurrent Technologies Corporation 2021
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
    Selector related helper functions
"""
from operator import is_
from typing import Callable, TypeVar

import rx.operators as op
from rx import Observable, pipe
from rx.subject import ReplaySubject

T1 = TypeVar("T1")
T2 = TypeVar("T2")
Mapper = Callable[[T1], T2]


def select(selector: Mapper[T1, T2]) -> Callable[[Observable], Observable]:
    """Reactive operator that applies a selector
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
