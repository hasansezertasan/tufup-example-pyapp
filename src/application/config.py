import logging
import os
import pathlib
import sys
from importlib.metadata import version

from platformdirs import PlatformDirs
from tufup.utils.platform_specific import ON_MAC, ON_WINDOWS
from tufup.repo import (
    DEFAULT_REPO_DIR_NAME,
    DEFAULT_KEYS_DIR_NAME,
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

| Platform         | Short            | Long                                      | Platformdirs Shorthand |
| ---------------- | ---------------- | ----------------------------------------- | ---------------------  |
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

config_path: pathlib.Path = dirs.user_data_path / "config.json"
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

    model_config = SettingsConfigDict(json_file=config_path)

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


ROOT_DIR = pathlib.Path.cwd()
"""Root directory of the application."""

# Are we running in a PyInstaller bundle?
# https://pyinstaller.org/en/stable/runtime-information.html
FROZEN = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
"""True if the application is running in a PyInstaller bundle."""

# App directories
if DEBUG:
    TEMP_DIR = ROOT_DIR / "tmp"
    DATA_DIR = TEMP_DIR / "Library"
    PROGRAMS_DIR = TEMP_DIR / "Applications"
elif ON_WINDOWS:
    DATA_DIR = dirs.user_data_path
    PROGRAMS_DIR = DATA_DIR / "Programs"
elif ON_MAC:
    DATA_DIR = pathlib.Path.home() / "Library"
    PROGRAMS_DIR = pathlib.Path.home() / "Applications"
else:
    raise NotImplementedError("Unsupported platform")

INSTALL_DIR = PROGRAMS_DIR / APP_NAME
UPDATE_CACHE_DIR = DATA_DIR / APP_NAME / "update_cache"
METADATA_DIR = UPDATE_CACHE_DIR / DEFAULT_META_DIR_NAME
TARGET_DIR = UPDATE_CACHE_DIR / DEFAULT_TARGETS_DIR_NAME
TRUSTED_ROOT_SRC = ROOT_DIR / "root.json"
TRUSTED_ROOT_DST = METADATA_DIR / "root.json"

# For development
if DEBUG:
    TEMP_DIR = ROOT_DIR / "tmp"
    SERVER_DIR = TEMP_DIR / "server"
    SERVER_KEYS_DIR = SERVER_DIR / DEFAULT_KEYS_DIR_NAME
    """Directory where the keys are stored. This should be offline and secure."""
    SERVER_REPO_DIR = SERVER_DIR / DEFAULT_REPO_DIR_NAME
    """Directory where the repository metadata is stored. This can be online."""
    SERVER_METADATA_DIR = SERVER_REPO_DIR / DEFAULT_META_DIR_NAME
    SERVER_TARGET_DIR = SERVER_REPO_DIR / DEFAULT_TARGETS_DIR_NAME
    TRUSTED_ROOT_SRC = SERVER_METADATA_DIR / "root.json"
