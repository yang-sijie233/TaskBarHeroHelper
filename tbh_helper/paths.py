"""应用路径：开发模式与 PyInstaller 打包通用。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """用户可读写目录（配置、profiles 存于此）。"""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def bundle_dir() -> Path:
    """打包内嵌的只读资源目录。"""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def ensure_runtime_files() -> Path:
    """首次运行：从模板复制 config.yaml / portal_profile.yaml。"""
    base = app_dir()
    profiles = base / "profiles"
    profiles.mkdir(parents=True, exist_ok=True)

    config = base / "config.yaml"
    if not config.exists():
        src = bundle_dir() / "config.default.yaml"
        if src.exists():
            shutil.copy2(src, config)

    profile = profiles / "portal_profile.yaml"
    if not profile.exists():
        src = bundle_dir() / "profiles" / "portal_profile.default.yaml"
        if src.exists():
            shutil.copy2(src, profile)

    return base
