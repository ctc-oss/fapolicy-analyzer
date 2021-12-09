from redux import Reducer, combine_reducers

from .todo_reducer import todos
from .visibility_reducer import visibility_filter

todo_reducer: Reducer = combine_reducers({
    'todos': todos,
    'visibility_filter': visibility_filter
})
