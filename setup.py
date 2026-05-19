"""Install shell CLI wrapper and magicdub-dev.pth for editable installs."""

from __future__ import annotations

import os
import site
import stat
from pathlib import Path

from setuptools import setup
from setuptools.command.editable_wheel import editable_wheel

_REPO_ROOT = Path(__file__).resolve().parent


def _site_packages_dir() -> Path:
    for p in site.getsitepackages():
        path = Path(p)
        if path.is_dir() and path.name == "site-packages":
            return path
    import sysconfig

    return Path(sysconfig.get_path("purelib"))


def _write_repo_pth(sp: Path) -> None:
    pth = sp / "magicdub-dev.pth"
    pth.write_text(f"{_REPO_ROOT}\n", encoding="utf-8")
    try:
        st = os.stat(pth)
        if hasattr(stat, "UF_HIDDEN") and (st.st_flags & stat.UF_HIDDEN):
            os.chflags(pth, st.st_flags & ~stat.UF_HIDDEN)
    except OSError:
        pass


class _EditableWheel(editable_wheel):
    def run(self) -> None:
        super().run()
        try:
            _write_repo_pth(_site_packages_dir())
        except RuntimeError:
            pass


setup(
    scripts=["scripts/magicdub"],
    cmdclass={"editable_wheel": _EditableWheel},
)
