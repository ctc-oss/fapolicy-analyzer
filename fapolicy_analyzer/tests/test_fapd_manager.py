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
from ui.fapd_manager import FapdManager, FapdMode, ServiceStatus


@pytest.fixture
def fapdManager():
    return FapdManager()


# Testing fapd daemon interfacing
def test_profiling_stdout_access(fapdManager, mocker):
    strStdout = "/A/totally/contrived/path.stdout"
    fapdManager.set_profiling_stdout(strStdout)
    assert(fapdManager.fapd_profiling_stdout == strStdout)
    assert(fapdManager.get_profiling_stdout() == strStdout)


def test_profiling_stderr_access(fapdManager, mocker):
    strStderr = "/Another/totally/contrived/path.stderr"
    fapdManager.set_profiling_stderr(strStderr)
    assert(fapdManager.fapd_profiling_stderr == strStderr)
    assert(fapdManager.get_profiling_stderr() == strStderr)


def test_stop_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager.set_mode(FapdMode.ONLINE)
    fapdManager.stop()
    mockFapdHandle.stop.assert_called()


def test_start_online(fapdManager, mocker):
    mockFapdHandle = MagicMock()
    fapdManager._fapd_ref = mockFapdHandle
    fapdManager.set_mode(FapdMode.ONLINE)
    fapdManager.start()


def test_stop_profiling(fapdManager, mocker):
    fapdManager.procProfile = MagicMock()
    mockPoll = mocker.patch("fapolicy_analyzer.ui.fapd_manager.subprocess.Popen.poll", return_value=False)
    fapdManager.set_mode(FapdMode.PROFILING)
    fapdManager.stop()
    #fapdManager.procProfile.terminate.assert_called()
    mockPoll.assert_called()


def test_start_profiling(fapdManager, mocker):
    mockProcess = MagicMock()
    mockSubproc = mocker.patch("fapolicy_analyzer.ui.fapd_manager.subprocess.Popen",
                               return_value=mockProcess)
    fapdManager.set_mode(FapdMode.PROFILING)
    fapdManager.start()
    mockSubproc.assert_called()


def test_status(fapdManager):
    tupleStatus = fapdManager.status()
    assert(tupleStatus == (ServiceStatus.UNKNOWN, FapdMode.DISABLED))
