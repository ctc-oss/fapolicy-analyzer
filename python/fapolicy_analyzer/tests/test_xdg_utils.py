import pytest
import os
from util.xdg_utils import xdg_data_dir_prefix, \
    xdg_state_dir_prefix, \
    xdg_config_dir_prefix

def test_xdg_state_dir_prefix_wo_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get('HOME')
    strStateDefaultDir = strHomeDir + "/.local/state/"
    strExpected = strStateDefaultDir + "fapolicy-analyzer/" + strBasename

    del os.environ["XDG_STATE_HOME"]
    assert xdg_state_dir_prefix(strBasename) == strExpected

def test_xdg_state_dir_prefix_w_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/tmp/"
    strExpected = strEnvVar + "fapolicy-analyzer/" + strBasename

    monkeypatch.setenv("XDG_STATE_HOME", strEnvVar)
    assert xdg_state_dir_prefix(strBasename) == strExpected
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)

def test_xdg_data_dir_prefix_wo_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get('HOME')
    strStateDefaultDir = strHomeDir + "/.local/state/"
    strExpected = strStateDefaultDir + "fapolicy-analyzer/" + strBasename

    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    assert xdg_state_dir_prefix(strBasename) == strExpected

def test_xdg_data_dir_prefix_w_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/tmp/"
    strExpected = strEnvVar + "fapolicy-analyzer/" + strBasename

    monkeypatch.setenv("XDG_STATE_HOME", strEnvVar)
    assert xdg_state_dir_prefix(strBasename) == strExpected

def test_xdg_config_dir_prefix_wo_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strHomeDir = os.environ.get('HOME')
    strStateDefaultDir = strHomeDir + "/.local/state/"
    strExpected = strStateDefaultDir + "fapolicy-analyzer/" + strBasename

    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    assert xdg_state_dir_prefix(strBasename) == strExpected

def test_xdg_config_dir_prefix_w_env(monkeypatch):
    strBasename = "Arbitrary.txt"
    strEnvVar = "/tmp/"
    strExpected = strEnvVar + "fapolicy-analyzer/" + strBasename

    monkeypatch.setenv("XDG_STATE_HOME", strEnvVar)
    assert xdg_state_dir_prefix(strBasename) == strExpected
