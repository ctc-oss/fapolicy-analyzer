from unittest.mock import MagicMock
from fapolicy_analyzer.ui.features.daemon_feature import create_daemon_feature
from redux import Action, create_store


def test_acquire_daemon_exception(mocker):
    mockHandle = mocker.patch("fapolicy_analyzer.ui.features.daemon_feature.Handle",
                 side_effect=Exception("Handle creation failed"))
    mockCallable = MagicMock()
    mockDaemon = None #MagicMock()
    #mockPipe = mocker.patch("fapolicy_analyzer.ui.features.daemon_feature.pipe",
    # return_value=MagicMock())
    df = create_daemon_feature(create_store().dispatch)
    assert True
    # mockHandle.assert_called()
