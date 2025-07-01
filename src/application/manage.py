import typer
import logging
import sys
from pathlib import Path

from tufup.repo import Repository

from application.config import (
    APP_NAME,
    APP_VERSION,
    SERVER_KEYS_DIR,
    SERVER_REPO_DIR,
)

from tufup.repo import DEFAULT_KEY_MAP
import os
import pyinstaller_versionfile

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# For development

# Key settings
KEY_NAME = os.getenv("KEY_NAME", "application_key")
PRIVATE_KEY_PATH = SERVER_KEYS_DIR / KEY_NAME
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

    typer.echo(f"Application Version {APP_VERSION}")


@app.command(
    name="info",
    help="Display the basic information of application.",
)
def info():
    """
    Display the basic information of application.
    """

    typer.echo(f"Application Name: {APP_NAME}")
    typer.echo(f"Version: {APP_VERSION}")


@app.command(
    name="version-file",
    help="Generate a version file for the application.",
)
def version_file():
    """
    Generate a version file for the application.
    This is used by PyInstaller to embed the version in the binary.
    """

    pyinstaller_versionfile.create_versionfile(
        output_file="version.txt",
        version=APP_VERSION,
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
        app_version_attr="application.__about__.__version__",
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


@app.command(
    name="repo-add-bundle",
    help="Add a new app bundle to the repository.",
)
def repo_add_bundle(bundle_dist_dir: Path = typer.Option()):
    """Create archive from latest bundle and add to repository."""
    try:
        bundle_dirs = [path for path in bundle_dist_dir.iterdir() if path.is_dir()]
    except FileNotFoundError:
        sys.exit(f"Directory not found: {bundle_dist_dir}\nDid you run pyinstaller?")
    if len(bundle_dirs) != 1:
        sys.exit(f"Expected one bundle, found {len(bundle_dirs)}.")
    bundle_dir = bundle_dirs[0]
    typer.echo(f"Adding bundle: {bundle_dir}")

    # Create repository instance from config file (assuming the repository
    # has already been initialized)
    repo = Repository.from_config()

    # Add new app bundle to repository (automatically reads application.__version__)
    repo.add_bundle(new_bundle_dir=bundle_dir, skip_patch=True)
    repo.publish_changes(private_key_dirs=[SERVER_KEYS_DIR])

    typer.echo("Done.")


if __name__ == "__main__":
    app()
