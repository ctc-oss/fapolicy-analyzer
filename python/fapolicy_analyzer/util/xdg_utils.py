import os


def xdg_state_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_STATE_HOME
    directory, creates the directory if needed, and verifies that it is writable
    by the effective user
    """
    # Use the XDG_STATE_HOME env var, or $(HOME)/.local/state/
    _home = os.path.expanduser('~')
    xdg_state_home = os.environ.get('XDG_STATE_HOME',
                                    os.path.join(_home, '.local', 'state'))
    app_tmp_dir = os.path.join(xdg_state_home, "fapolicy-analyzer/")

    try:
        # Create if needed, and verify writable dir
        if not os.path.exists(app_tmp_dir):
            print(" Creating '{}' ".format(app_tmp_dir))
            os.makedirs(app_tmp_dir, 0o700)
    except Exception as e:
        print("Warning: Xdg directory creation of '{}' failed."
              "Using /tmp/".format(app_tmp_dir), e)
        app_tmp_dir = "/tmp/"

    return app_tmp_dir + strBaseName


def xdg_data_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_DATA_HOME
    directory, creates the directory if needed, and verifies that it is writable
    by the effective user
    """
    # Use the XDG_DATA_HOME env var, or $(HOME)/.local/share/
    _home = os.path.expanduser('~')
    xdg_data_home = os.environ.get('XDG_DATA_HOME',
                                   os.path.join(_home, '.local', 'share'))
    app_tmp_dir = os.path.join(xdg_data_home, "fapolicy-analyzer/")
    try:
        # Create if needed, and verify writable dir
        if not os.path.exists(app_tmp_dir):
            print(" Creating '{}' ".format(app_tmp_dir))
            os.makedirs(app_tmp_dir, 0o700)
    except Exception as e:
        print("Warning: Xdg directory creation of '{}' failed."
              "Using /tmp/".format(app_tmp_dir), e)
        app_tmp_dir = "/tmp/"

    return app_tmp_dir + strBaseName


def xdg_config_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_CONFIG_HOME
    directory, and verifies that it is readable by the effective user.
    """
    # Use the XDG_CONFIG_HOME env var, or $(HOME)/.config/
    _home = os.path.expanduser('~')
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME',
                                     os.path.join(_home, '.config'))
    app_tmp_dir = os.path.join(xdg_config_home, "fapolicy-analyzer/")
    return app_tmp_dir + strBaseName
