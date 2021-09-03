import pytest
from mocks import mock_System


@pytest.fixture(autouse=True)
def mock_system(mocker):
    mocker.patch("ui.ancillary_trust_database_admin.System", return_value=mock_System())
    mocker.patch("ui.system_trust_database_admin.System", return_value=mock_System())
