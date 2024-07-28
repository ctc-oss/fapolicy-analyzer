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

import fapolicy_analyzer
from fapolicy_analyzer.util.format import f, snake_to_camelcase

import pytest
import context  # noqa: F401


def test_snake_to_camelcase():
    assert snake_to_camelcase("foo_baz_test") == "fooBazTest"


def test_snake_to_camelcase_empty_string():
    assert snake_to_camelcase("") == ""


def test_snake_to_camelcase_none():
    assert snake_to_camelcase(None) is None


def test_snake_to_camelcase_leading_underscore():
    assert snake_to_camelcase("_foo") == "_foo"


def test_f():
    insert = "foo"
    assert f(f"insert is {insert}") == "insert is foo"


def test_f_none():
    assert f(None) is None

@pytest.mark.parametrize("py_ver, f_in, eval_out",[((3,9), "foo", "insert is foo"),
                                                  ((3,12), "bar", "insert is bar"),
                                                  ((3,13), "baz", "insert is baz")])
def test_f_supported_py_vers(py_ver, f_in, eval_out, mocker):
    insert = f_in
    mockEval = mocker.patch('builtins.eval', return_value=f"insert is {insert}")
    mockSysVer = mocker.patch.object(fapolicy_analyzer.util.format, "sys")
    mockSysVer.version_info = py_ver

    assert f(None) is None
    assert f(f"insert is {insert}") == eval_out

    # Check if keyword args were in eval()'s call
    assert mockEval.called
    tupleEvalArgs = mockEval.call_args

    if py_ver < (3, 13):
        # Py <3.13 only uses positional args, Kwargs dict should be empty
        assert not tupleEvalArgs.kwargs

    else:
        # Py 3.13 call uses kw args in our code
        assert tupleEvalArgs.kwargs
        assert "locals" in tupleEvalArgs.kwargs
        assert "globals" in tupleEvalArgs.kwargs
