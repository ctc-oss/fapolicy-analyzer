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

import pytest
from unittest.mock import MagicMock
from fapolicy_analyzer.ui.fapd_manager import FapdManager, FapdMode, ServiceStatus


@pytest.fixture
def fapdManager():
    return FapdManager(True)


def test_profiling_stdout_stderr_env_var(monkeypatch):
    strLogName = "/tmp/profiling_log"
    monkeypatch.setenv("FAPD_LOGPATH", strLogName)
    fapd_mgr = FapdManager()
    assert fapd_mgr.fapd_profiling_stdout == f"{strLogName}.stdout"
    assert fapd_mgr.fapd_profiling_stderr == f"{strLogName}.stderr"


def test_stop_disabled(fapdManager, mocker):
    fapdManager.mode = FapdMode.DISABLED
    fapdManager._stop()
    assert fapdManager.mode == FapdMode.DISABLED
    assert not fapdManager._stop()


def test_start_disabled(fapdManager, mocker):
    fapdManager.mode = FapdMode.DISABLED
    assert not fapdManager._start()
    assert fapdManager.mode == FapdMode.DISABLED


def test_stop_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_status = ServiceStatus.TRUE
    fapdManager.mode = FapdMode.ONLINE
    fapdManager.stop()
    mockFapdHandle.stop.assert_called()
    assert fapdManager.mode == FapdMode.ONLINE


def test_start_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_status = ServiceStatus.FALSE
    fapdManager._fapd_profiling_status = False
    fapdManager.mode = FapdMode.ONLINE
    fapdManager.start()
    mockFapdHandle.start.assert_called()
    assert fapdManager.mode == FapdMode.ONLINE


def test_stop_profiling(fapdManager, mocker):
    mockPopen = MagicMock()
    fapdManager.procProfile = mockPopen
    fapdManager.mode = FapdMode.PROFILING
    fapdManager.procProfile.poll.side_effect = [True, False]
    fapdManager.stop(FapdMode.PROFILING)
    mockPopen.terminate.assert_called()
    mockPopen.wait.assert_called()
    assert fapdManager.mode == FapdMode.PROFILING


def test_stop_profiling_via_systemd(fapdManager, mocker):
    mockFapdProfHandle = MagicMock()
    fapdManager._fapd_profiling_ref = mockFapdProfHandle
    mocker.patch("fapolicy_analyzer.ui.fapd_manager.os.path.exists", return_value=True)
    fapdManager._fapd_status = ServiceStatus.TRUE
    fapdManager.mode = FapdMode.PROFILING
    fapdManager.stop(FapdMode.PROFILING)
    mockFapdProfHandle.stop.assert_called()


def test_start_profiling(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_status = ServiceStatus.TRUE
    fapdManager._fapd_ref.is_active.return_value = True
    mockProcess = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.fapd_manager.subprocess.Popen", return_value=mockProcess
    )
    fapdManager.mode = FapdMode.ONLINE
    fapdManager.start(FapdMode.PROFILING)
    mockFapdHandle.stop.assert_called()
    assert fapdManager.mode == FapdMode.PROFILING


def test_start_profiling_via_systemd(fapdManager, mocker):
    mockFapdProfHandle = MagicMock()
    fapdManager._fapd_profiling_ref = mockFapdProfHandle
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_status = ServiceStatus.TRUE
    fapdManager._fapd_ref.is_active.return_value = True
    mocker.patch("fapolicy_analyzer.ui.fapd_manager.os.path.exists", return_value=True)
    fapdManager.mode = FapdMode.ONLINE
    fapdManager.start(FapdMode.PROFILING)
    mockFapdHandle.stop.assert_called()
    mockFapdProfHandle.start.assert_called()
    assert fapdManager.mode == FapdMode.PROFILING


def test_status_disabled(fapdManager, mocker):
    fapdManager.mode = FapdMode.DISABLED
    bStatus = fapdManager._status()
    assert bStatus == ServiceStatus.UNKNOWN


def test_status_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_ref.is_active.side_effect = [False, True, False]
    fapdManager.mode = FapdMode.ONLINE
    bStatus = fapdManager._status()
    assert bStatus == ServiceStatus.FALSE
    bStatus = fapdManager._status()
    assert bStatus == ServiceStatus.TRUE
    bStatus = fapdManager._status()
    assert bStatus == ServiceStatus.FALSE
    fapdManager._fapd_ref.is_active.side_effect = IOError
    fapdManager._status()


def test_status_profiling_fapd(fapdManager, mocker):
    fapdManager.mode = FapdMode.PROFILING
    fapdManager.procProfile = None
    bStatus = fapdManager._status()
    assert bStatus == ServiceStatus.FALSE
    fapdManager.procProfile = MagicMock()
    bStatus = fapdManager._status()
    assert bStatus == ServiceStatus.TRUE
