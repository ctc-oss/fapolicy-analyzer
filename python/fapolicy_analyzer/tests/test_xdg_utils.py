import os
from fapolicy_analyzer.util.xdg_utils import (
    xdg_data_dir_prefix,
    xdg_state_dir_prefix,
    xdg_config_dir_prefix,
)


def test_xdg_state_dir_prefix_wo_env():
    if "XDG_STATE_HOME" in os.environ:
        del os.environ["XDG_STATE_HOME"]

    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strStateDefaultDir = strHomeDir + "/.local/state/"
    strExpected = strStateDefaultDir + "fapolicy-analyzer/" + strBasename

    assert xdg_state_dir_prefix(strBasename) == strExpected


def test_xdg_state_dir_prefix_w_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/tmp/"
    strExpected = strEnvVar + "fapolicy-analyzer/" + strBasename

    monkeypatch.setenv("XDG_STATE_HOME", strEnvVar)
    strGenerated = xdg_state_dir_prefix(strBasename)
    assert strGenerated == strExpected
    assert os.path.exists(os.path.dirname(strGenerated))

    # Clean-up
    os.rmdir(os.path.dirname(strGenerated))
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)


def test_xdg_state_dir_prefix_w_exception(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/usr/lib"  # Unwritable system dir
    strExpected = "/tmp/" + strBasename

    # Mock the environment to use a directory that can not be created
    monkeypatch.setenv("XDG_STATE_HOME", strEnvVar)
    assert xdg_state_dir_prefix(strBasename) == strExpected
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)


def test_xdg_data_dir_prefix_wo_env():
    if "XDG_DATA_HOME" in os.environ:
        del os.environ["XDG_DATA_HOME"]

    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strDataDefaultDir = strHomeDir + "/.local/share/"
    strExpected = strDataDefaultDir + "fapolicy-analyzer/" + strBasename

    assert xdg_data_dir_prefix(strBasename) == strExpected


def test_xdg_data_dir_prefix_w_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/tmp/"
    strExpected = strEnvVar + "fapolicy-analyzer/" + strBasename

    monkeypatch.setenv("XDG_DATA_HOME", strEnvVar)
    strGenerated = xdg_data_dir_prefix(strBasename)
    assert strGenerated == strExpected
    assert os.path.exists(os.path.dirname(strGenerated))

    # Clean-up
    os.rmdir(os.path.dirname(strGenerated))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)


def test_xdg_data_dir_prefix_w_exception(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/usr/lib"  # Unwritable system dir
    strExpected = "/tmp/" + strBasename

    # Mock the environment to use a directory that can not be created
    monkeypatch.setenv("XDG_DATA_HOME", strEnvVar)
    assert xdg_data_dir_prefix(strBasename) == strExpected
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)


def test_xdg_config_dir_prefix_wo_env():
    if "XDG_CONFIG_HOME" in os.environ:
        del os.environ["XDG_CONFIG_HOME"]

    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get("HOME")
    strConfigDefaultDir = strHomeDir + "/.config/"
    strExpected = strConfigDefaultDir + "fapolicy-analyzer/" + strBasename

    assert xdg_config_dir_prefix(strBasename) == strExpected


def test_xdg_config_dir_prefix_w_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/tmp/"
    strExpected = strEnvVar + "fapolicy-analyzer/" + strBasename

    monkeypatch.setenv("XDG_CONFIG_HOME", strEnvVar)
    assert xdg_config_dir_prefix(strBasename) == strExpected
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
