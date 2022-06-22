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
import os
from unittest.mock import MagicMock
from ui.faprofiler import FaProfiler, FaProfSession, ProfSessionStatus


@pytest.fixture
def faProfSession():
    dictArgs = {"executeText": "/usr/bin/ls",
                "argText": "-ltr /tmp",
                "userText": os.getenv("USER"),
                "dirText": os.getenv("HOME"),
                "envText": 'FAPD_LOGPATH=/tmp/tgt_profiler, XX="xx"',
                }
    return FaProfSession(dictArgs)


@pytest.fixture
def faProfiler():
    return FaProfiler()


# Testing FaProfSession
def test_faprofsession_init(faProfSession, mocker):
    assert not faProfSession.tgtStdout
    assert not faProfSession.tgtStderr


def test_startTarget(faProfSession, mocker):
    mockPopen = MagicMock()
    mocker.patch("ui.faprofiler.subprocess.Popen",
                 return_value=mockPopen)
    mockPopen.returncode = 0
    assert not faProfSession.procTarget
    faProfSession.startTarget(0)
    mockPopen.wait.assert_called()
    assert faProfSession.procTarget.returncode == 0
    faProfSession.startTarget(0, block_until_termination=False)

    # Although we aren't waiting on the process, it is short-lived and finished
    assert faProfSession.procTarget.returncode == 0

    # Emulate a file open() exception
    mocker.patch("ui.faprofiler.open", side_effect=Exception())
    faProfSession.startTarget(1)
    assert faProfSession.fdTgtStdout is None
    assert faProfSession.fdTgtStderr is None

    # Emulate a getpwnam() exception
    mocker.patch("ui.faprofiler.pwd.getpwnam", side_effect=Exception())
    faProfSession.startTarget(1)
    assert faProfSession.fdTgtStdout is None
    assert faProfSession.fdTgtStderr is None


def test_stopTarget(faProfSession, mocker):
    mockPopen = MagicMock()
    mockPopen.returncode = 0
    faProfSession.procTarget = mockPopen
    faProfSession.stopTarget()
    mockPopen.terminate.assert_called()
    mockPopen.wait.assert_called()
    assert faProfSession.procTarget.returncode == 0


def test_get_profsession_timestamp(faProfSession):
    faProfSession.faprofiler = MagicMock()
    faProfSession.get_profiling_timestamp()
    faProfSession.faprofiler.get_profiling_timestamp.assert_called()


def test_get_status(faProfSession, mocker):
    faProfSession.procTarget = None
    assert faProfSession.get_status() == ProfSessionStatus.QUEUED
    faProfSession.procTarget = MagicMock()
    faProfSession.procTarget.poll = MagicMock(side_effect=[None, 0])
    assert faProfSession.get_status() == ProfSessionStatus.INPROGRESS
    assert faProfSession.get_status() == ProfSessionStatus.COMPLETED


# Testing FaProfiler
def test_start_prof_session(faProfiler, mocker):
    faProfiler.fapd_mgr = MagicMock()
    dictArgs = {"executeText": "/usr/bin/ls",
                "argText": "-ltr /tmp",
                "userText": os.getenv("USER"),
                "dirText": os.getenv("HOME"),
                "envText": "FAPD_LOGPATH=/tmp/tgt_profiler,XYZ=123",
                }

    key = faProfiler.start_prof_session(dictArgs)
    assert faProfiler.instance != 0
    assert key in faProfiler.dictFaProfSession


def test_stop_prof_session(faProfiler, mocker):
    faProfiler.fapd_mgr = MagicMock()
    dictArgs = {"executeText": "/usr/bin/ls",
                "argText": "-ltr /tmp",
                "userText": os.getenv("USER"),
                "dirText": os.getenv("HOME"),
                "envText": "FAPD_LOGPATH=/tmp/tgt_profiler,XYZ=123",
                }

    session_name = faProfiler.start_prof_session(dictArgs)
    assert faProfiler.instance != 0
    faProfiler.stop_prof_session(session_name)
    assert faProfiler.instance == 0
    session_name = faProfiler.start_prof_session(dictArgs)
    faProfiler.stop_prof_session()
    assert faProfiler.instance == 0
    assert not faProfiler.dictFaProfSession


def test_status_prof_session(faProfiler, mocker):
    pass


def test_get_profiling_timestamp(faProfiler, mocker):
    faProfiler.fapd_mgr = None
    assert not faProfiler.get_profiling_timestamp()
    faProfiler.fapd_mgr = MagicMock()
    faProfiler.fapd_mgr._fapd_profiling_timestamp = "20220501_231624_890930"
    assert faProfiler.get_profiling_timestamp() == "20220501_231624_890930"
