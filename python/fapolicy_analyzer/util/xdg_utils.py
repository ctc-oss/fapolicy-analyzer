import os
import logging


def _xdg_dir_prefix(key):
    _home = os.path.expanduser("~")
    dictEnvVar2Default = {
        "XDG_DATA_HOME": os.path.join(_home, ".local", "share"),
        "XDG_STATE_HOME": os.path.join(_home, ".local", "state"),
    }
    xdg_home = os.environ.get(key, dictEnvVar2Default[key])
    app_tmp_dir = os.path.join(xdg_home, "fapolicy-analyzer/")

    try:
        # Create if needed
        if not os.path.exists(app_tmp_dir):
            print(" Creating '{}' ".format(app_tmp_dir))
            os.makedirs(app_tmp_dir, 0o700)
    except Exception as e:
        print(
            "Warning: Xdg directory creation of '{}' failed."
            "Using /tmp/".format(app_tmp_dir),
            e,
        )
        app_tmp_dir = "/tmp/"

    return app_tmp_dir


def xdg_state_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_STATE_HOME
    directory, creates the directory if needed.
    """
    strAbsolutePath = _xdg_dir_prefix("XDG_STATE_HOME") + strBaseName
    logging.debug("Xdg absolute path: {}".format(strAbsolutePath))
    return strAbsolutePath


def xdg_data_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_DATA_HOME
    directory, creates the directory if needed.
    """
    strAbsolutePath = _xdg_dir_prefix("XDG_DATA_HOME") + strBaseName
    logging.debug("Xdg absolute path: {}".format(strAbsolutePath))
    return strAbsolutePath


def xdg_config_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_CONFIG_HOME
    directory, and verifies that it is readable by the effective user.
    """
    # Use the XDG_CONFIG_HOME env var, or $(HOME)/.config/
    _home = os.path.expanduser("~")
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.join(_home, ".config"))
    return os.path.join(xdg_config_home, "fapolicy-analyzer/", strBaseName)
