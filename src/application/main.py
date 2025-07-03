import typer
import logging
import sys
import shutil
import pathlib
from tufup.client import Client
from . import config

logger = logging.getLogger(__name__)


def progress_hook(bytes_downloaded: int, bytes_expected: int):
    progress_percent = bytes_downloaded / bytes_expected * 100
    print(f"\r{progress_percent:.1f}%", end="")
    if progress_percent >= 100:
        print("")


def callback():
    # The app must ensure dirs exist
    for dir_path in [
        config.INSTALL_DIR,
        config.METADATA_DIR,
        config.TARGET_DIR,
    ]:
        if not dir_path.exists():
            logger.info(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)

    # The app must be shipped with a trusted "root.json" metadata file,
    # which is created using the tufup.repo tools. The app must ensure
    # this file can be found in the specified metadata_dir. The root metadata
    # file lists all trusted keys and TUF roles.
    if not config.TRUSTED_ROOT_DST.exists():
        typer.echo(
            f"Trusted root metadata file not found in cache: {config.TRUSTED_ROOT_DST}. "
        )
        if not config.TRUSTED_ROOT_SRC.exists():
            sys.exit(f"Trusted root metadata file not found: {config.TRUSTED_ROOT_SRC}")
        shutil.copy(src=config.TRUSTED_ROOT_SRC, dst=config.TRUSTED_ROOT_DST)
        typer.echo("Trusted root metadata copied to cache.")

    client = Client(
        app_name=config.APP_NAME,
        app_install_dir=config.INSTALL_DIR,
        current_version=config.APP_VERSION,
        metadata_dir=config.METADATA_DIR,
        metadata_base_url=config.METADATA_BASE_URL,
        target_dir=config.TARGET_DIR,
        target_base_url=config.TARGET_BASE_URL,
        refresh_required=False,
    )

    # Perform update
    new_update = client.check_for_updates()
    if new_update:
        # [optional] use custom metadata, if available
        if new_update.custom:
            # for example, show list of changes (see repo_add_bundle.py for definition)
            typer.echo("Changes in this update:")
            for item in new_update.custom.get("changes", []):
                typer.echo(f"\t- {item}")
        # Apply the update
        client.download_and_apply_update(
            skip_confirmation=True,
            # progress_hook=progress_hook,
            purge_dst_dir=True,
            exclude_from_purge=None,
            log_file_name="install.log",
        )


app = typer.Typer(
    name=config.APP_NAME,
    no_args_is_help=True,
    callback=callback,
)


@app.command(
    name="version",
    help="Display the version of application.",
)
def version_():
    """
    Display the version of application.
    """

    typer.echo(f"Application Version {config.APP_VERSION}")


@app.command(
    name="info",
    help="Display the basic information of application.",
)
def info() -> None:
    """
    Display the basic information of application.
    """
    typer.echo(f"Application Version: {config.APP_VERSION}")
    typer.echo(f"Python Version: {sys.version}")
    typer.echo(f"Platform: {sys.platform}")


if __name__ == "__main__":
    app()
