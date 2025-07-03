import logging
import pathlib
import os
import sys
from importlib.metadata import version

from platformdirs import PlatformDirs
from tufup.repo import (
    DEFAULT_META_DIR_NAME,
    DEFAULT_TARGETS_DIR_NAME,
)
from pydantic import HttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


logger = logging.getLogger(__name__)

dirs = PlatformDirs("application", "hasansezertasan", ensure_exists=True)
"""Platform-specific directories for the application.

Provides paths to directories for storing configuration files, logs, and other data.
The directories are created if they do not exist.

## Mappings

| Platform         | Short            | Long                                       | Platformdirs Shorthand |
| ---------------- | ---------------- | ------------------------------------------ | ---------------------  |
| Windows (10, 11) | `%APPDATA%`.     | `C:\\Users\hasansezertasan\AppData\Roaming`| `.roaming`             |
| Windows (10, 11) | `%LOCALAPPDATA%` | `C:\\Users\hasansezertasan\AppData\Local`  | `.local`               |
| Windows (10)     | `%PROGRAMDATA%`  | `C:\\ProgramData`                          | `.common`              |
| Windows (10, 11) | `%PROGRAMFILES%` | `C:\\Program Files`                        | `.system`              |
| MacOS            |                  | `~/Library/Application Support`            | `.system`              |
| MacOS            |                  | `~/Applications`                           | `.common`              |


On Windows 10, a typical location for app data would be `%PROGRAMDATA%\\application` (per-machine), or `%LOCALAPPDATA%\\application` (per-user).
Typical app installation locations are `%PROGRAMFILES%\\application` (per-machine) or `%LOCALAPPDATA%\Programs\\application` (per-user).

Also see:

- https://docs.microsoft.com/en-us/windows/win32/msi/installation-context
- https://github.com/dennisvang/tufup-example/blob/master/src/myapp/settings.py
- https://github.com/tox-dev/platformdirs

Example:
    ```python
    print(dirs.user_data_path)
    print(dirs.user_data_path.mkdir(parents=True, exist_ok=True))
    ```

"""

CONFIG_DIR: pathlib.Path = dirs.user_data_path / "config.json"
"""Path to the configuration file."""


class Settings(BaseSettings):
    """Application settings loaded from configuration files and environment variables."""

    metadata_base_url: HttpUrl = Field(
        ...,
        title="Metadata server base URL",
    )
    target_base_url: HttpUrl = Field(
        ...,
        title="Target server base URL",
    )

    model_config = SettingsConfigDict(json_file=CONFIG_DIR)

    @classmethod
    def settings_customise_sources(
        cls,  # noqa: F841
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize the settings sources used to load the settings."""
        return (JsonConfigSettingsSource(settings_cls),)


# App info
APP_NAME = "application"
"""Name of the application."""
APP_VERSION = version(APP_NAME)
"""Version of the application."""
DEBUG = os.getenv("APP_DEBUG", "false").lower() in ("true", "1", "yes")
"""Enable debug mode for development. Set APP_DEBUG environment variable to enable."""

# Update Server URLs
METADATA_BASE_URL = "http://localhost:8000/metadata/"
TARGET_BASE_URL = "http://localhost:8000/targets/"


# Are we running in a PyInstaller bundle?
# https://pyinstaller.org/en/stable/runtime-information.html
FROZEN = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
"""True if the application is running in a PyInstaller bundle."""
ROOT_DIR = (
    pathlib.Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else pathlib.Path.cwd()
)
"""Root directory of the application."""
EXECUTABLE_DIR = pathlib.Path(sys.executable).parent if FROZEN else ROOT_DIR
"""
Directory where the executable is located.

`pathlib.Path(sys.executable)` gives the path to the executable, all the time!
Pyinstaller datas are not reachable by this way, use pathlib.Path(sys._MEIPASS) instead
"""


# App directories
DATA_DIR = dirs.user_data_path
INSTALL_DIR = pathlib.Path(sys.executable).parent if FROZEN else ROOT_DIR
UPDATE_CACHE_DIR = DATA_DIR / "update_cache"
METADATA_DIR = UPDATE_CACHE_DIR / DEFAULT_META_DIR_NAME
TARGET_DIR = UPDATE_CACHE_DIR / DEFAULT_TARGETS_DIR_NAME
TRUSTED_ROOT_SRC = ROOT_DIR / "root.json"
TRUSTED_ROOT_DST = METADATA_DIR / "root.json"
