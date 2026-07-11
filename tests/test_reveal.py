# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
from app import reveal


def _capture():
    calls = []
    return calls, lambda cmd: calls.append(cmd)


def test_reveal_darwin():
    calls, runner = _capture()
    reveal.reveal("/some/dir", platform="darwin", runner=runner)
    assert calls == [["open", "/some/dir"]]


def test_reveal_windows():
    calls, runner = _capture()
    reveal.reveal("/some/dir", platform="win32", runner=runner)
    assert calls == [["explorer", "/some/dir"]]


def test_reveal_linux():
    calls, runner = _capture()
    reveal.reveal("/some/dir", platform="linux", runner=runner)
    assert calls == [["xdg-open", "/some/dir"]]
