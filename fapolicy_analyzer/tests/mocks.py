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

from time import time
from unittest.mock import MagicMock


def mock_trust():
    return MagicMock(
        status="trusted",
        path="/tmp/foo",
        actual=MagicMock(last_modified=int(time())),
    )


def mock_users():
    mockUser1 = MagicMock(id=1)
    mockUser1.name = "fooUser"
    mockUser2 = MagicMock(id=2)
    mockUser2.name = "otherUser"
    return [mockUser1, mockUser2]


def mock_groups():
    mockGroup1 = MagicMock(id=100)
    mockGroup1.name = "fooGroup"
    mockGroup2 = MagicMock(id=101)
    mockGroup2.name = "otherGroup"
    return [mockGroup1, mockGroup2]


def mock_events():
    return [
        MagicMock(
            uid=1,
            gid=100,
            subject=MagicMock(file="fooSubject", trust="ST", access="A"),
            object=MagicMock(file="fooObject", trust="ST", access="A", mode="R"),
        ),
        MagicMock(
            uid=1,
            gid=100,
            subject=MagicMock(file="barSubject", trust="AT", access="A"),
            object=MagicMock(file="barObject", trust="AT", access="A", mode="R"),
        ),
        MagicMock(
            uid=2,
            gid=101,
            subject=MagicMock(file="otherSubject", trust="ST", access="A"),
            object=MagicMock(file="otherObject", trust="ST", access="A", mode="R"),
        ),
    ]


def mock_log():
    return MagicMock(
        subjects=lambda: [e.subject.file for e in mock_events()],
        by_subject=lambda f: [e for e in mock_events() if e.subject.file == f],
        by_user=lambda id: [e for e in mock_events() if e.uid == id],
        by_group=lambda id: [e for e in mock_events() if e.gid == id],
    )


class mock_System:
    def ancillary_trust(self):
        return [mock_trust()]

    def system_trust(self):
        return [mock_trust()]

    def deploy(self):
        pass

    def apply_changeset(self, changeset):
        pass

    def users(self):
        return mock_users()

    def groups(self):
        return mock_groups()

    def events(self, file):
        return mock_log()
