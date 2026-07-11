# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""Cross-platform filesystem locations. No ShotGrid dependency."""
import os
import sys


def desktop_dir(platform: str = sys.platform) -> str:
    """Return the current user's Desktop directory on macOS/Linux/Windows."""
    if platform != "win32":
        return os.path.join(os.path.expanduser("~"), "Desktop")

    # Windows: resolve the real Desktop via the Win32 shell API.
    from ctypes import (
        create_unicode_buffer,
        windll,  # type: ignore
        wintypes,
    )

    csidl_desktopdirectory = 0x10
    shgfp_type_current = 0

    buf = create_unicode_buffer(wintypes.MAX_PATH)
    result = windll.shell32.SHGetFolderPathW(
        None, csidl_desktopdirectory, None, shgfp_type_current, buf
    )
    if result != 0:
        return os.path.join(os.path.expanduser("~"), "Desktop")
    return buf.value


def annotations_dirname(today) -> str:
    """Return the dated download folder name, e.g. ``Annotations_20260710``."""
    return "Annotations_%s" % today.strftime("%Y%m%d")
