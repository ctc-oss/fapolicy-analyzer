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
from ui.faprofiler import FaProfiler, FaProfSession


@pytest.fixture
def faProfSession():
    dictArgs = {"executeText": "/usr/bin/ls",
                "argText": "-ltr /tmp",
                "userText": "toma",
                "dirText": "/home/toma",
                "envText": "FAPD_LOGPATH=/tmp/tgt_profiler",
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
    pass


def test_get_profsession_timestamp(faProfSession):
    pass


def test_get_status(faProfSession):
    pass


# Testing FaProfiler
def test_faprofiler_init(faProfiler):
    pass


def test_start_prof_session(faProfiler, mocker):
    dictArgs = {"executeText": "/usr/bin/ls",
                "argText": "-ltr /tmp",
                "userText": "toma",
                "dirText": "/home/toma",
                "envText": "FAPD_LOGPATH=/tmp/tgt_profiler",
                }

    faProfiler.start_prof_session(dictArgs)


def test_terminate_prof_session(faProfiler, mocker):
    pass


def test_status_prof_session(faProfiler, mocker):
    pass


def test_get_profiling_timestamp(faProfiler, mocker):
    faProfiler.fapd_mgr = None
    assert not faProfiler.get_profiling_timestamp()
    faProfiler.fapd_mgr = MagicMock()
    faProfiler.get_profiling_timestamp()
    faProfiler.fapd_mgr.get_fapd_timestamp.assert_called()
