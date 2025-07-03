# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE

datas = [("tmp/server/repository/metadata/root.json", ".")]
# We are copying metadata for the 'application' package so that we can single source application version and other metadata.
datas += copy_metadata('application')


a = Analysis(
    ['main.py'],
    datas=datas,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    upx=True,
    upx_exclude=[],
)