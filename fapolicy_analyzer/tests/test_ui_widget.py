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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import gi
import pytest

from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget, UIConnectedWidget, UIWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


class concrete_UIBuilderWidget(UIBuilderWidget):
    pass


class concrete_UIConnectedWidget(UIConnectedWidget):
    pass


@pytest.fixture
def mockWidget():
    return MagicMock(spec=Gtk.Widget)


@pytest.fixture
def uiWidget(mockWidget):
    class concrete(UIWidget):
        pass

    return concrete(mockWidget)


@pytest.fixture
def mockBuilder(mocker):
    mock = MagicMock(get_object=MagicMock(), add_from_file=MagicMock())
    mocker.patch("fapolicy_analyzer.ui.ui_widget.Gtk.Builder", return_value=mock)
    return mock


@pytest.fixture
def mockResource(mocker):
    mock = mocker.patch(
        "fapolicy_analyzer.ui.ui_widget.get_resource", return_value="foo"
    )
    return mock


@pytest.fixture
def mockFeature():
    return MagicMock(subscribe=MagicMock())


def test_calls_widget_destroy(uiWidget, mockWidget):
    mockWidget.destroy = MagicMock()
    uiWidget.dispose()
    mockWidget.destroy.assert_called_once()


def test_calls_uiwidget_destroy(uiWidget):
    uiWidget._dispose = MagicMock()
    uiWidget.dispose()
    uiWidget._dispose.assert_called_once()


def test_loads_default_glade_file(mockBuilder, mockResource):
    concrete_UIBuilderWidget()
    mockResource.assert_called_once_with("test_ui_widget.glade")
    mockBuilder.add_from_string.assert_called_once_with("foo")
    mockBuilder.get_object.assert_called_once_with("testUiWidget")


def test_loads_named_glade_file(mockBuilder, mockResource):
    concrete_UIBuilderWidget("fooWidget")
    mockResource.assert_called_once_with("fooWidget.glade")
    mockBuilder.add_from_string.assert_called_once_with("foo")
    mockBuilder.get_object.assert_called_once_with("fooWidget")


def test_UIBuilderWidget_with_bad_glade_file(mocker):
    mock_error_logger = MagicMock()
    mocker.patch("fapolicy_analyzer.ui.ui_widget.get_resource", return_value=None)
    mocker.patch("fapolicy_analyzer.ui.ui_widget.logging", error=mock_error_logger)
    concrete_UIBuilderWidget("fooWidget")
    mock_error_logger.assert_called_once_with(
        "Resource fooWidget.glade is not available."
    )


@pytest.mark.usefixtures("mockBuilder", "mockResource")
def test_connects_feature(mockFeature):
    concrete_UIConnectedWidget(
        mockFeature,
        on_next="foo_next",
        on_error="foo_error",
        on_completed="foo_completed",
    )
    mockFeature.subscribe.assert_called_once_with(
        on_next="foo_next", on_error="foo_error", on_completed="foo_completed"
    )


@pytest.mark.usefixtures("mockBuilder", "mockResource")
def test_connects_features():
    mock_feature_1 = MagicMock(subscribe=MagicMock())
    mock_feature_2 = MagicMock(subscribe=MagicMock())
    concrete_UIConnectedWidget(
        features=[
            {
                mock_feature_1: {
                    "on_next": "mock1_next",
                    "on_error": "mock1_error",
                    "on_completed": "mock1_complete",
                }
            },
            {
                mock_feature_2: {
                    "on_next": "mock2_next",
                    "on_error": "mock2_error",
                    "on_completed": "mock2_complete",
                }
            },
        ]
    )
    mock_feature_1.subscribe.assert_called_once_with(
        on_next="mock1_next", on_error="mock1_error", on_completed="mock1_complete"
    )
    mock_feature_2.subscribe.assert_called_once_with(
        on_next="mock2_next", on_error="mock2_error", on_completed="mock2_complete"
    )


@pytest.mark.usefixtures("mockBuilder", "mockResource")
def test_disposes_subscription(mockFeature):
    mockDispose = MagicMock()
    mockFeature.subscribe.return_value = MagicMock(dispose=mockDispose)
    widget = concrete_UIConnectedWidget(mockFeature)
    widget.dispose()
    mockDispose.assert_called_once()


@pytest.mark.usefixtures("mockBuilder", "mockResource")
def test_disposes_subscriptions():
    mock_feature_1 = MagicMock(subscribe=MagicMock())
    mock_feature_2 = MagicMock(subscribe=MagicMock())
    mock_dispose_1 = MagicMock()
    mock_dispose_2 = MagicMock()
    mock_feature_1.subscribe.return_value = MagicMock(dispose=mock_dispose_1)
    mock_feature_2.subscribe.return_value = MagicMock(dispose=mock_dispose_2)
    widget = concrete_UIConnectedWidget(
        features=[{mock_feature_1: {}}, {mock_feature_2: {}}]
    )
    widget.dispose()
    mock_dispose_1.assert_called_once()
    mock_dispose_2.assert_called_once()


def test_UIConnectedWidget_with_bad_parameters():
    with pytest.raises(TypeError) as ex:
        concrete_UIConnectedWidget()
    assert "UIConnectedWidget.__init__() no feature parameters provided" in str(
        ex.value
    )
