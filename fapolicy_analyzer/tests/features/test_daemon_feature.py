from unittest.mock import MagicMock
from fapolicy_analyzer.ui.features.daemon_feature import create_daemon_feature

def test_acquire_daemon_exception(mocker):
    mockHandle = mocker.patch("fapolicy_analyzer.ui.features.daemon_feature.Handle",
                 side_effect=Exception("Handle creation failed"))
    mockCallable = MagicMock()
    df = create_daemon_feature(mockCallable)
    mockHandle.assert_called()
