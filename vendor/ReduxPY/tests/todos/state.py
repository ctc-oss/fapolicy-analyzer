from typing import Callable, Iterable, Iterator, NamedTuple


class TodoItem(NamedTuple):
    id: int
    text: str
    completed: bool
