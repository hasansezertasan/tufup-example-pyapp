import typer
import logging
from pathlib import Path
from importlib.metadata import version

from tufup.repo import Repository
from tufup.repo import (
    DEFAULT_REPO_DIR_NAME,
    DEFAULT_KEYS_DIR_NAME,
)
from application.config import (
    APP_NAME,
    CONFIG_DIR,
)

from tufup.repo import DEFAULT_KEY_MAP
import os

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Key settings
ROOT_DIR = Path.cwd()
TEMP_DIR = ROOT_DIR / "tmp"
KEY_NAME = os.getenv("KEY_NAME", "application_key")
SERVER_DIR = TEMP_DIR / "server"
SERVER_KEYS_DIR = SERVER_DIR / DEFAULT_KEYS_DIR_NAME
SERVER_REPO_DIR = SERVER_DIR / DEFAULT_REPO_DIR_NAME
KEY_MAP = {role_name: [KEY_NAME] for role_name in DEFAULT_KEY_MAP.keys()}
ENCRYPTED_KEYS: list = []
THRESHOLDS: dict = dict(root=1, targets=1, snapshot=1, timestamp=1)
EXPIRATION_DAYS: dict = dict(root=365, targets=7, snapshot=7, timestamp=1)

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="Awesome Application Manager",
    no_args_is_help=True,
)


@app.command(
    name="version",
    help="Display the version of application.",
)
def version_():
    """
    Display the version of application.
    """
    typer.echo(f"Application Version {version('application')}")


@app.command(
    name="info",
    help="Display the basic information of application.",
)
def info():
    """
    Display the basic information of application.
    """

    typer.echo(f"Application Name: {APP_NAME}")
    typer.echo(f"Version: {version('application')}")


@app.command(
    name="config",
    help="Create the config file if it does not exist and display it's path.",
)
def config():
    """
    Create the config file if it does not exist and display it's path.
    """
    if not CONFIG_DIR.exists():
        sample_CONFIG_DIR = Path().cwd() / "sample.config.json"
        CONFIG_DIR.write_text(sample_CONFIG_DIR.read_text())

    typer.echo(f"`{CONFIG_DIR}`")


@app.command(
    name="version-file",
    help="Generate a version file for the application.",
)
def version_file():
    """
    Generate a version file for the application.
    This is used by PyInstaller to embed the version in the binary.
    """
    import pyinstaller_versionfile

    pyinstaller_versionfile.create_versionfile(
        output_file="version.txt",
        version=version("application"),
        company_name="My Imaginary Company",
        file_description="Application",
        internal_name="Application",
        legal_copyright="© My Imaginary Company. All rights reserved.",
        original_filename="application.exe",
        product_name="Application",
        translations=[0, 1200],
    )


@app.command(
    name="repo-init",
    help="Initialize the repository for the application.",
)
def repo_init():
    # Create repository instance
    repo = Repository(
        app_name=APP_NAME,
        # app_version_attr="application._version.__version__",
        repo_dir=SERVER_REPO_DIR,
        keys_dir=SERVER_KEYS_DIR,
        key_map=KEY_MAP,
        expiration_days=EXPIRATION_DAYS,
        encrypted_keys=ENCRYPTED_KEYS,
        thresholds=THRESHOLDS,
    )

    # Save configuration (JSON file)
    repo.save_config()

    # Initialize repository (creates keys and root metadata, if necessary)
    repo.initialize()

    typer.echo(f"Initialized repository: {SERVER_REPO_DIR}")


if __name__ == "__main__":
    app()
