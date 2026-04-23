import configparser
import os
import platform


def _get_config_dir() -> str:
    """Return the platform-appropriate config directory for Mongoose."""
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "mongoose")
    elif system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/mongoose")
    else:
        # Linux / other Unix
        xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        return os.path.join(xdg, "mongoose")


def get_config_path() -> str:
    return os.path.join(_get_config_dir(), "config.conf")


_DEFAULTS = {
    "me": {
        "lastname": "Lastname",
        "class": "4.X",
    },
    "export": {
        "point_style": "dot",
        "hiddenlines_style": "normal",
    },
}


def load_config() -> configparser.ConfigParser:
    """Load config from the platform config path. Create defaults if missing."""
    config = configparser.ConfigParser()
    # Apply built-in defaults
    for section, values in _DEFAULTS.items():
        config[section] = values

    config_path = get_config_path()
    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")
    else:
        # Try falling back to project-local config.conf
        local_conf = os.path.join(os.path.dirname(__file__), "config.conf")
        if os.path.exists(local_conf):
            config.read(local_conf, encoding="utf-8")
        # Save to the platform path so it exists for future use
        save_config(config)

    return config


def save_config(config: configparser.ConfigParser) -> None:
    """Save config to the platform config path."""
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)
