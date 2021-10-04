from unittest.mock import Mock


def assert_not_any_call(self, *args, **kwargs):
    """
    Extends the unittest.Mock object by adding an assert_not_called_with method.
    This asserts the mock has not been called with the specified arguments.
    """
    try:
        self.assert_any_call(*args, **kwargs)
    except AssertionError:
        return
    raise AssertionError(
        "%s call found" % self._format_mock_call_signature(args, kwargs)
    )


Mock.assert_not_any_call = assert_not_any_call
