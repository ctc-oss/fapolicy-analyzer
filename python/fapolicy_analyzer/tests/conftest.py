import pytest
from mocks import mock_System


@pytest.fixture(autouse=True)
def widget(mocker):
    mocker.patch("ui.database_admin_page.System", return_value=mock_System())
