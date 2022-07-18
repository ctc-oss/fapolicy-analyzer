# Copyright Concurrent Technologies Corporation 2022
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

from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union

import fapolicy_analyzer
from fapolicy_analyzer import System

T = TypeVar("T", Dict[str, str], str)


class Changeset(ABC, Generic[T]):
    @abstractmethod
    def apply_to_system(self, system: System) -> System:
        """Apply this changeset to the given system"""

    @abstractmethod
    def serialize(self) -> T:
        """Serialize this changeset to a serializable object"""

    @classmethod
    def deserialize(cls, data: Union[Dict[str, str], str]) -> "Changeset":
        if isinstance(data, dict):
            tcs = TrustChangeset()
            for path, action in data.items():
                if action == "Add":
                    tcs.add(path)
                elif action == "Del":
                    tcs.delete(path)
            return tcs
        elif isinstance(data, str):
            rcs = RuleChangeset()
            rcs.set(data)
            return rcs

        raise TypeError("Invalid changeset type to deserialize")


class RuleChangeset(Changeset[str]):
    def __init__(self):
        self.__wrapped = fapolicy_analyzer.RuleChangeset()

    def set(self, change: str):
        self.__wrapped.set(change)

    def apply_to_system(self, system: System) -> System:
        return system.apply_rule_changes(self.__wrapped)

    def serialize(self) -> str:
        return self.__wrapped.text()


class TrustChangeset(Changeset[Dict[str, str]]):
    def __init__(self):
        self.__wrapped = fapolicy_analyzer.Changeset()

    def add(self, change: str):
        self.__wrapped.add_trust(change)

    def delete(self, change: str):
        self.__wrapped.del_trust(change)

    def apply_to_system(self, system: System) -> System:
        return system.apply_changeset(self.__wrapped)

    def serialize(self) -> Dict[str, str]:
        return self.__wrapped.get_path_action_map()
