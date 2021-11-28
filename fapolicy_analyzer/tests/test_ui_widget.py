import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from gi.repository import Gtk
from ui.ui_widget import UIBuilderWidget, UIConnectedWidget, UIWidget


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
    mocker.patch("ui.ui_widget.Gtk.Builder", return_value=mock)
    return mock


@pytest.fixture
def mockResource(mocker):
    mock = mocker.patch("ui.ui_widget.resources.path")
    mock.return_value.__enter__.return_value.as_posix.return_value = "foo"
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
    mockResource.assert_called_once_with(
        "fapolicy_analyzer.glade", "test_ui_widget.glade"
    )
    mockBuilder.add_from_file.assert_called_once_with("foo")
    mockBuilder.get_object.assert_called_once_with("testUiWidget")


def test_loads_named_glade_file(mockBuilder, mockResource):
    concrete_UIBuilderWidget("fooWidget")
    mockResource.assert_called_once_with("fapolicy_analyzer.glade", "fooWidget.glade")
    mockBuilder.add_from_file.assert_called_once_with("foo")
    mockBuilder.get_object.assert_called_once_with("fooWidget")


@pytest.mark.usefixtures("mockBuilder", "mockResource")
def test_runs_post_init(mockFeature):
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
def test_disposes_subscription(mockFeature):
    mockDispose = MagicMock()
    mockFeature.subscribe.return_value = MagicMock(dispose=mockDispose)
    widget = concrete_UIConnectedWidget(mockFeature)
    widget.dispose()
    mockDispose.assert_called_once()
