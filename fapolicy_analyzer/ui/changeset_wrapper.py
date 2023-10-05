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
import json
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar

import fapolicy_analyzer
from fapolicy_analyzer import System

T = TypeVar("T", Dict[str, str], str)


def changeset_dict_to_json(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


class Changeset(ABC, Generic[T]):
    @abstractmethod
    def apply_to_system(self, system: System) -> System:
        """Apply this changeset to the given system"""

    @abstractmethod
    def serialize(self) -> T:
        """Serialize this changeset to a serializable object"""

    @staticmethod
    @abstractmethod
    def deserialize(d: str) -> T:
        """Deserialize this changeset from serialized data"""

    @staticmethod
    def load(dd: dict) -> "Changeset":
        if not dd:
            raise TypeError("Invalid changeset type to deserialize")

        if "type" not in dd:
            raise TypeError("Changeset does not indicate type")

        t = dd["type"]
        d = dd["data"]

        if t == "trust":
            return TrustChangeset.deserialize(d)
        elif t == "rules":
            return RuleChangeset.deserialize(d)
        elif t == "config":
            return ConfigChangeset.deserialize(d)
        else:
            raise TypeError(f"Invalid changeset type {t}")


class ConfigChangeset(Changeset[str]):
    def __init__(self):
        self.__wrapped = fapolicy_analyzer.ConfigChangeset()

    def parse(self, change: str):
        self.__wrapped.parse(change)

    def apply_to_system(self, system: System) -> System:
        return system.apply_config_changes(self.__wrapped)

    def serialize(self) -> dict[str, str]:
        return {
            "type": "config",
            "data": self.__wrapped.text(),
        }

    @staticmethod
    def deserialize(d: str) -> "ConfigChangeset":
        ccs = ConfigChangeset()
        ccs.parse(d)
        return ccs


class RuleChangeset(Changeset[str]):
    def __init__(self):
        self.__wrapped = fapolicy_analyzer.RuleChangeset()

    def parse(self, change: str):
        self.__wrapped.parse(change)

    def rules(self):
        return self.__wrapped.rules()

    def apply_to_system(self, system: System) -> System:
        return system.apply_rule_changes(self.__wrapped)

    def serialize(self) -> dict[str, str]:
        return {"type": "rules", "data": self.__wrapped.text()}

    @staticmethod
    def deserialize(d: str) -> "RuleChangeset":
        rcs = RuleChangeset()
        rcs.parse(d)
        return rcs


class TrustChangeset(Changeset[Dict[str, str]]):
    def __init__(self):
        self.__wrapped = fapolicy_analyzer.Changeset()

    def add(self, change: str):
        self.__wrapped.add_trust(change)

    def delete(self, change: str):
        self.__wrapped.del_trust(change)

    def action_map(self) -> dict:
        return self.__wrapped.get_path_action_map()

    def apply_to_system(self, system: System) -> System:
        return system.apply_changeset(self.__wrapped)

    def serialize(self) -> Dict[str, str]:
        return {
            "type": "trust",
            "data": changeset_dict_to_json(self.__wrapped.get_path_action_map()),
        }

    @staticmethod
    def deserialize(d) -> "TrustChangeset":
        tcs = TrustChangeset()
        # s = '{"/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del","/data_space/Integration.json": "Add",}'
        # json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 103 (char 102)
        if isinstance(d, str):
            d = json.loads(d)
        for path, action in d.items():
            if action == "Add":
                tcs.add(path)
            elif action == "Del":
                tcs.delete(path)

        return tcs
