import context  # noqa: F401
from util.format import snake_to_camelcase, f


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
