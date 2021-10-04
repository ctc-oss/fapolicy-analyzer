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
            uid=2,
            gid=101,
            subject=MagicMock(file="otherSubject", trust="ST", access="A"),
            object=MagicMock(file="otherObject", trust="ST", access="A", mode="R"),
        ),
    ]


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

    def events_from(self, file):
        return mock_events
