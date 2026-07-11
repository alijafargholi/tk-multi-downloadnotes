# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""Open a directory in the OS file browser. No ShotGrid dependency."""
import subprocess
import sys


def reveal(
    directory: str,
    platform: str = sys.platform,
    runner=subprocess.Popen,
) -> None:
    """Open ``directory`` in Finder (macOS), Explorer (Windows), or the
    Linux file manager."""
    if platform == "darwin":
        runner(["open", directory])
    elif platform == "win32":
        runner(["explorer", directory])
    else:
        runner(["xdg-open", directory])
