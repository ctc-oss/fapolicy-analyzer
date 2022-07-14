from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union

import fapolicy_analyzer
from fapolicy_analyzer import System

T = TypeVar("T", Dict[str, str], str)


class Changeset(ABC, Generic[T]):
    @abstractmethod
    def apply_to_system(self, system: System) -> System:
        pass

    @abstractmethod
    def serialize(self) -> T:
        pass

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
