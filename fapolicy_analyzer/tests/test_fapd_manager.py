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
import time
from datetime import datetime as DT
from unittest.mock import MagicMock
from ui.fapd_manager import FapdManager, FapdMode, ServiceStatus


@pytest.fixture
def fapdManager():
    return FapdManager()


def test_get_profiling_timestamp(fapdManager):
    timeNow = DT.fromtimestamp(time.time())
    strTNow = timeNow.strftime("%Y%m%d_%H%M%S_%f")
    fapdManager._fapd_profiling_timestamp = strTNow
    assert fapdManager.get_profiling_timestamp() == strTNow


def test_profiling_stdout_access(fapdManager, mocker):
    strStdout = "/A/totally/contrived/path.stdout"
    fapdManager.set_profiling_stdout(strStdout)
    assert(fapdManager.fapd_profiling_stdout == strStdout)
    assert(fapdManager.get_profiling_stdout() == strStdout)


def test_profiling_stdout_stderr_env_var(monkeypatch):
    strLogName = "/tmp/profiling_log"
    monkeypatch.setenv("FAPD_LOGPATH", strLogName)
    fapd_mgr = FapdManager()
    assert fapd_mgr.fapd_profiling_stdout == f"{strLogName}.stdout"
    assert fapd_mgr.get_profiling_stdout() == f"{strLogName}.stdout"
    assert fapd_mgr.fapd_profiling_stderr == f"{strLogName}.stderr"
    assert fapd_mgr.get_profiling_stderr() == f"{strLogName}.stderr"


def test_profiling_stderr_access(fapdManager, mocker):
    strStderr = "/Another/totally/contrived/path.stderr"
    fapdManager.set_profiling_stderr(strStderr)
    assert(fapdManager.fapd_profiling_stderr == strStderr)
    assert(fapdManager.get_profiling_stderr() == strStderr)


def test_stop_disabled(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager.set_mode(FapdMode.DISABLED)
    fapdManager.stop()
    assert fapdManager.get_mode() == FapdMode.DISABLED
    assert not fapdManager.start()


def test_start_disabled(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager.set_mode(FapdMode.DISABLED)
    assert not fapdManager.start()
    assert fapdManager.get_mode() == FapdMode.DISABLED


def test_stop_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_status = ServiceStatus.TRUE
    fapdManager.set_mode(FapdMode.ONLINE)
    fapdManager.stop()
    mockFapdHandle.stop.assert_called()
    assert fapdManager.get_mode() == FapdMode.ONLINE


def test_start_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_status = ServiceStatus.FALSE
    fapdManager.set_mode(FapdMode.ONLINE)
    fapdManager.start()
    mockFapdHandle.start.assert_called()
    assert fapdManager.get_mode() == FapdMode.ONLINE


def test_stop_profiling(fapdManager, mocker):
    fapdManager.procProfile = MagicMock()
    fapdManager.procProfile.poll.side_effect = [True, False]
    fapdManager.set_mode(FapdMode.PROFILING)
    fapdManager.stop()
    fapdManager.procProfile.terminate.assert_called()
    fapdManager.procProfile.poll.assert_called()
    assert fapdManager.get_mode() == FapdMode.PROFILING


def test_start_profiling(fapdManager, mocker):
    mockProcess = MagicMock()
    mockSubproc = mocker.patch("fapolicy_analyzer.ui.fapd_manager.subprocess.Popen",
                               return_value=mockProcess)
    fapdManager.set_mode(FapdMode.PROFILING)
    fapdManager.start()
    mockSubproc.assert_called()
    assert fapdManager.get_mode() == FapdMode.PROFILING


def test_status(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager._fapd_ref.is_active.side_effect = [False, True, False]
    bStatus = fapdManager.status_online()
    assert bStatus == ServiceStatus.FALSE
    bStatus = fapdManager.status_online()
    assert bStatus == ServiceStatus.TRUE
    bStatus = fapdManager.status_online()
    assert bStatus == ServiceStatus.FALSE
