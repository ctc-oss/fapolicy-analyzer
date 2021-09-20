from unittest.mock import MagicMock


class mock_System:
    mock_trust = MagicMock(status="trusted", path="/tmp/foo")

    def ancillary_trust(self):
        return [self.mock_trust]

    def system_trust(self):
        return [self.mock_trust]

    def deploy(self):
        pass

    def apply_changeset(self, changeset):
        pass
