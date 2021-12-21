# Copyright Concurrent Technologies Corporation 2021
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


class UIOperation(ABC):
    """
    An abstract base class implemented by any class providing an operation that can be
    initiated by the user on the system. (i.e. Deploying Changsets)
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.dispose()

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_icon(self) -> str:
        pass

    @abstractmethod
    def run(self):
        pass

    def dispose(self):
        pass
