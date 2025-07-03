# Tufup (TUF-updater) Example

This repository shows how to use the [tufup] package for automated application updates.

This is done by means of a dummy cli-application, called `application`, that uses `tufup` in combination with `pyapp`.

## Questions

If you have any questions, please make sure to check the [existing discussions][discussions] and [existing issues][issues] first. (Also check [`tufup` discussions][tufup-discussions] and [`tufup` issues][tufup-issues].)

New *questions* can be asked in the [Q&A][discussions-qa] or on [stackoverflow], and *bugs* related to `tufup-example-pyapp` can be reported [through the issues page][issues-new].

## Getting started

For basic terminology, see documentation for [TUF (The Update Framework)][tuf].

We start out with a dummy application that has already integrated the `tufup.client`. See `src/application/__init__.py` for details.

The dummy application is bundled using [pyinstaller], but `tufup` works with any type of "application bundle" (i.e. just a directory with content representing the application).

The example includes a basic PyInstaller `.spec` file that ensures the `tufup` root metadata file (`root.json`) is included in the application bundle.

The dummy *application* specifies where all `tufup`-related files will be stored. This is illustrated in `settings.py`.

The following basic steps are covered:

1. Initialize a repository.
1. Initial release.
   1. Build the application, including trusted root metadata from the repository.
   1. Create an archive for the application and register it in the repo.
1. Second release.
   1. Build the new release.
   1. Create an archive for the new release, create a patch, and register both in the repo.
1. Serve the repository on a local test server.
1. Run the "installed" application, so it can perform an automatic update.

> For quick testing, these steps have been automated in the `mise.toml` file. Just run `mise run update-cycle` to perform the entire update cycle, including repository setup, application build, and update.

A detailed description of the steps, both for the repository-side and for the client-side, can be found in the following sections.

### Repo side

Some example scripts are provided for initializing a tufup repository and for adding new versions, see `repo_*.py`.

Alternatively, `tufup` offers a command line interface (CLI) for repository actions. Type `tufup -h` on the command line for more information.

Here's how to set up the example tufup repository, starting from a clean repo, i.e. no `tmp/application` dir is present in the repo root (as defined by `DEV_DIR` in `settings.py`):

Note: If you use the CLI, see `repo_settings.py` for sensible values.

1. Run `mise run repo:init` (CLI: `tufup init`)
1. Run `mise run build:pyinstaller` (note that our `main.spec` ensures that the latest `root.json` metadata file is included in the bundle)
1. Run `uv run tufup targets add $APP_VERSION $PYINSTALLER_DIST_DIR $SERVER_KEYS_DIR --skip-patch`
1. Modify the app, and/or increment `APP_VERSION` in `application/settings.py`
1. Run the `mise run build:pyinstaller` again
1. Modify the app, and/or increment `APP_VERSION` in `application/settings.py`

Note: When adding a bundle, `tufup` creates a patch by default, which can take quite some time.

If you want to skip patch creation, either set `skip_patch=True` in the `Repository.add_bundle()` call, or add the  `-s` option to the CLI command: `tufup targets add -s 2.0 ...`.

Now we should have a `tmp/application` dir with the following structure:

```text
tmp/application
├ build
├ dist
├ keystore
└ repository
  ├ metadata
  └ targets 
```

In the `targets` dir we find two app archives (1.0 and 2.0) and a corresponding patch file.

We can serve the repository on localhost as follows (relative to project root):

```shell
mise run repo:serve
```

That's it for the repo-side.

### Client side

On the same system (for convenience):

1. To simulate the initial installation on a client device, we do a manual extraction of the archive version 1.0 from the `repository/targets` dir into the `INSTALL_DIR`, specified in `application/settings.py`.

   #### On Windows

   In the default example the `INSTALL_DIR` would be the `C:\users\<username>\AppData\Local\Programs\application` directory. You can use `tar -xf application-1.0.tar.gz` in PowerShell to extract the bundle.

   #### On macOS

   To install the bundle on macOS to the default location, you can use `mkdir -p ~/Applications/application && tar -xf tmp/application/repository/targets/application-1.0.tar.gz -C ~/Applications/application`.

2. [optional] To try a patch update, copy the archive version 1.0 into the `TARGET_DIR` (this would normally be done by an installer).
3. Assuming the repo files are being served on localhost, as described above, we can now run the newly extracted executable, `main.exe` or `main`, depending on platform, directly from the `INSTALL_DIR`, and it will perform an update.
4. Metadata and targets are stored in the `UPDATE_CACHE_DIR`.

BEWARE: The steps above refer to the `INSTALL_DIR` for the `FROZEN` state, typically `C:\users\<username>\AppData\Local\Programs\application` on Windows.

In development, when running the `application` example directly from source, i.e. `FROZEN=False`, the `INSTALL_DIR` is different from the actual install dir that would be used in production.

### Troubleshooting

When playing around with this example-app, it is easy to wind up in an inconsistent state, e.g. due to stale metadata files. This may result in tuf role verification errors, for example. If this is the case, it is often easiest to start from a clean slate for both repo and client:

1. For the client-side, remove `UPDATE_CACHE_DIR` and `INSTALL_DIR`
2. For the repo-side, remove `DEV_DIR` (i.e. the `tmp/application` dir described above)
3. Remove `.tufup_repo_config`
4. Follow the steps above to set up the repo-side and client-side

Alternatively, you could run the `test_update_cycle.ps1` script, which also removes stale example files from the default directories.

[stackoverflow]: https://stackoverflow.com/questions/ask
[pyinstaller]: https://pyinstaller.org/en/stable/
[tuf]: https://theupdateframework.io/
[tufup]: https://github.com/dennisvang/tufup
[tufup-discussions]: https://github.com/dennisvang/tufup/discussions
[tufup-issues]: https://github.com/dennisvang/tufup/issues
[discussions]: https://github.com/hasansezertasan/tufup-example-pyapp/discussions
[issues]: https://github.com/hasansezertasan/tufup-example-pyapp/issues?q=is%3Aissue
[issues-new]: https://github.com/hasansezertasan/tufup-example-pyapp/issues/new
[discussions-qa]: https://github.com/hasansezertasan/tufup-example-pyapp/discussions/new?category=q-a
