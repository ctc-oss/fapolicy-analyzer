import pytest
from mocks import mock_System


@pytest.fixture(autouse=True)
def widget(mocker):
    mocker.patch("ui.ancillary_trust_database_admin.System", return_value=mock_System())
    mocker.patch("ui.system_trust_database_admin.System", return_value=mock_System())
    mocker.patch("ui.policy_rules_admin_page.System", return_value=mock_System())
