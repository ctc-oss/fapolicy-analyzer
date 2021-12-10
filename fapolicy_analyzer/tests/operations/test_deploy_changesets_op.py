import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock, patch

import gi
import pytest
from callee import InstanceOf
from callee.attributes import Attrs
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    CLEAR_CHANGESETS,
    DEPLOY_ANCILLARY_TRUST,
    RESTORE_SYSTEM_CHECKPOINT,
    SET_SYSTEM_CHECKPOINT,
    NotificationType,
)
from fapolicy_analyzer.ui.operations.deploy_changesets_op import DeployChangesetsOp
from fapolicy_analyzer.ui.store import init_store
from fapolicy_analyzer.ui.strings import (
    DEPLOY_ANCILLARY_ERROR_MSG,
    DEPLOY_ANCILLARY_SUCCESSFUL_MSG,
)
from mocks import mock_System, mock_trust
from redux import Action
from rx.subject import Subject

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.operations.deploy_changesets_op.dispatch")


@pytest.fixture
def operation(mock_dispatch):
    init_store(mock_System())
    yield (op := DeployChangesetsOp(Gtk.Window()))
    op.dispose()


@pytest.fixture
def confirm_dialog(confirm_resp, mocker):
    mock_confirm_dialog = MagicMock(
        run=MagicMock(return_value=confirm_resp),
        hide=MagicMock(),
        get_save_state=MagicMock(return_value=False),
    )
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.ConfirmInfoDialog",
        return_value=mock_confirm_dialog,
    )

    return mock_confirm_dialog


@pytest.fixture
def revert_dialog(revert_resp, mocker):
    mock_revert_dialog = MagicMock(
        run=MagicMock(return_value=revert_resp), hide=MagicMock()
    )
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.DeployConfirmDialog.get_ref",
        return_value=mock_revert_dialog,
    )
    return mock_revert_dialog


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
@pytest.mark.usefixtures("revert_dialog")
def test_on_confirm_deployment(operation, confirm_dialog, mock_dispatch):
    operation.deploy([])
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=DEPLOY_ANCILLARY_TRUST)
    )
    confirm_dialog.run.assert_called()
    confirm_dialog.hide.assert_called()


@pytest.mark.usefixtures("confirm_dialog")
@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
def test_deploy_w_exception(mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    with DeployChangesetsOp(Gtk.Window()) as operation:
        system_features_mock.on_next(
            {
                "changesets": [],
                "ancillary_trust": MagicMock(
                    trust=[mock_trust()], error=None, loading=False
                ),
            }
        )
        operation.deploy([])
        system_features_mock.on_next(
            {"changesets": [], "ancillary_trust": MagicMock(error="foo")}
        )
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=DEPLOY_ANCILLARY_ERROR_MSG),
        )
    )


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.NO])
def test_on_neg_confirm_deployment(confirm_dialog, mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    with DeployChangesetsOp(Gtk.Window()) as operation:
        system_features_mock.on_next(
            {
                "changesets": [],
                "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
            }
        )
        operation.deploy([])
    confirm_dialog.run.assert_called()
    confirm_dialog.hide.assert_called()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action) & Attrs(type=DEPLOY_ANCILLARY_TRUST)
    )


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.NO])
@pytest.mark.usefixtures("confirm_dialog", "revert_dialog")
def test_on_revert_deployment(mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    with DeployChangesetsOp(Gtk.Window()) as operation:
        system_features_mock.on_next(
            {
                "changesets": [],
                "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
            }
        )
        operation.deploy([])
        system_features_mock.on_next(
            {
                "changesets": [],
                "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
            }
        )
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.SUCCESS, text=DEPLOY_ANCILLARY_SUCCESSFUL_MSG
            ),
        )
    )
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=RESTORE_SYSTEM_CHECKPOINT)
    )
    # mock_dispatch.assert_not_any_call(
    #     InstanceOf(Action) & Attrs(type=SET_SYSTEM_CHECKPOINT)
    # )
    # mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=CLEAR_CHANGESETS))


@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
@pytest.mark.parametrize("revert_resp", [Gtk.ResponseType.YES])
@pytest.mark.usefixtures("confirm_dialog", "revert_dialog")
def test_on_neg_revert_deployment(mock_dispatch, mocker):
    system_features_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.get_system_feature",
        return_value=system_features_mock,
    )
    init_store(mock_System())
    with DeployChangesetsOp(Gtk.Window()) as operation:
        system_features_mock.on_next(
            {
                "changesets": [],
                "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
            }
        )
        operation.deploy([])
        system_features_mock.on_next(
            {
                "changesets": [],
                "ancillary_trust": MagicMock(trust=[mock_trust()], error=None),
            }
        )
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.SUCCESS, text=DEPLOY_ANCILLARY_SUCCESSFUL_MSG
            ),
        )
    )
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=SET_SYSTEM_CHECKPOINT)
    )
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=CLEAR_CHANGESETS))


@pytest.mark.usefixtures("confirm_dialog")
@pytest.mark.parametrize("confirm_resp", [Gtk.ResponseType.YES])
def test_handle_deploy_exception(operation):
    with patch("fapolicy_analyzer.System") as mock:
        mock.deploy = MagicMock(
            return_value=None, side_effect=Exception("mocked error")
        )
        operation.system = mock
        with pytest.raises(Exception) as excinfo:
            operation.deploy([])
            assert excinfo.value.message == "mocked error"


@pytest.mark.usefixtures("mock_dispatch")
def test_saves_state(operation, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.ConfirmInfoDialog",
        return_value=MagicMock(
            run=MagicMock(return_value=Gtk.ResponseType.YES),
            get_save_state=MagicMock(return_value=True),
        ),
    )
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op._FapdArchiveFileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op._FapdArchiveFileChooserDialog.get_filename",
        return_value="fooFile",
    )
    mockSnapshot = mocker.patch(
        "fapolicy_analyzer.ui.operations.deploy_changesets_op.fapd_dbase_snapshot"
    )
    operation.deploy([])
    mockSnapshot.assert_called_once_with("fooFile")
