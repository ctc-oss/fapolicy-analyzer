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
""" Implementation of the reducer """

from redux import Action, handle_actions

from .action import ACTION_DECREMENT, ACTION_INCREMENT


def handle_increment_action(state: int, action: Action) -> int:
    return state + 1


def handle_decrement_action(state: int, action: Action) -> int:
    return state - 1


COUNTER_REDUCER = handle_actions(
    {ACTION_INCREMENT: handle_increment_action, ACTION_DECREMENT: handle_decrement_action}, 0)
