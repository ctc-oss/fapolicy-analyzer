""" Implementation of the reducer """

from redux import Action, handle_actions

from .action import ACTION_DECREMENT, ACTION_INCREMENT


def handle_increment_action(state: int, action: Action) -> int:
    return state + 1


def handle_decrement_action(state: int, action: Action) -> int:
    return state - 1


COUNTER_REDUCER = handle_actions(
    {ACTION_INCREMENT: handle_increment_action, ACTION_DECREMENT: handle_decrement_action}, 0)
