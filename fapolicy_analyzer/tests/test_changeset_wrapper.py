# Copyright Concurrent Technologies Corporation 2022
#
# This aogram is free software: you can redistribute it and/or modify
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

from unittest.mock import MagicMock

import pytest
from fapolicy_analyzer.ui.changeset_wrapper import (
    Changeset,
    RuleChangeset,
    TrustChangeset,
    changeset_dict_to_json,
    ConfigChangeset,
)


def test_deserialize_RuleChangeset():
    expected = {"type": "rules", "data": "rules"}
    actual = Changeset.load(expected)
    assert type(actual) == RuleChangeset
    assert actual.serialize() == expected


@pytest.mark.parametrize("action", ["Add", "Del"])
def test_deserialize_TrustChangeset(action):
    expected = {"type": "trust", "data": changeset_dict_to_json({"addition": action})}
    actual = Changeset.load(expected)
    assert type(actual) == TrustChangeset
    assert actual.serialize() == expected


def test_deserialize_ConfigChangeset():
    expected = {"type": "config", "data": "config"}
    actual = Changeset.load(expected)
    assert type(actual) == ConfigChangeset
    assert actual.serialize() == expected


def test_bad_deserialize():
    with pytest.raises(TypeError) as ex_info:
        Changeset.load(None)
    assert str(ex_info.value) == "Invalid changeset type to deserialize"


def test_RuleChangeset_apply():
    mock_system_apply = MagicMock()
    sut = RuleChangeset()
    sut.apply_to_system(MagicMock(apply_rule_changes=mock_system_apply))
    mock_system_apply.assert_called_with(sut._RuleChangeset__wrapped)


def test_RuleChangeset_parse(mocker):
    mock = mocker.patch(
        "fapolicy_analyzer.ui.changeset_wrapper.fapolicy_analyzer.RuleChangeset"
    )
    sut = RuleChangeset()
    sut.parse("foo")
    mock().parse.assert_called_with("foo")


def test_RuleChangeset_rules(mocker):
    mock = mocker.patch(
        "fapolicy_analyzer.ui.changeset_wrapper.fapolicy_analyzer.RuleChangeset"
    )
    sut = RuleChangeset()
    sut.rules()
    mock().rules.assert_called()


def test_RuleChangeset_serialize():
    sut = RuleChangeset()
    sut.parse("foo")
    assert sut.serialize() == {"type": "rules", "data": "foo"}


def test_TrustChangeset_apply():
    mock_system_apply = MagicMock()
    sut = TrustChangeset()
    sut.apply_to_system(MagicMock(apply_changeset=mock_system_apply))
    mock_system_apply.assert_called_with(sut._TrustChangeset__wrapped)


def test_TrustChangeset_add(mocker):
    mock = mocker.patch(
        "fapolicy_analyzer.ui.changeset_wrapper.fapolicy_analyzer.Changeset"
    )
    sut = TrustChangeset()
    sut.add("foo")
    mock().add_trust.assert_called_with("foo")


def test_TrustChangeset_delete(mocker):
    mock = mocker.patch(
        "fapolicy_analyzer.ui.changeset_wrapper.fapolicy_analyzer.Changeset"
    )
    sut = TrustChangeset()
    sut.delete("foo")
    mock().del_trust.assert_called_with("foo")


def test_TrustChangeset_serialize():
    sut = TrustChangeset()
    sut.add("addition")
    sut.delete("deletion")
    assert sut.serialize() == {
        "type": "trust",
        "data": changeset_dict_to_json({"addition": "Add", "deletion": "Del"}),
    }


def test_ConfigChangeset_apply():
    mock_system_apply = MagicMock()
    sut = ConfigChangeset()
    sut.apply_to_system(MagicMock(apply_config_changes=mock_system_apply))
    mock_system_apply.assert_called_with(sut._ConfigChangeset__wrapped)


def test_ConfigChangeset_parse(mocker):
    mock = mocker.patch(
        "fapolicy_analyzer.ui.changeset_wrapper.fapolicy_analyzer.ConfigChangeset"
    )
    sut = ConfigChangeset()
    sut.parse("foo")
    mock().parse.assert_called_with("foo")


def test_ConfigChangeset_serialize():
    sut = ConfigChangeset()
    sut.parse("foo")
    assert sut.serialize() == {"type": "config", "data": "foo"}
