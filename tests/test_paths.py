# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
import datetime
import os

from app import paths


def test_desktop_dir_darwin(monkeypatch):
    monkeypatch.setenv("HOME", "/Users/tester")
    assert paths.desktop_dir("darwin") == os.path.join(
        "/Users/tester", "Desktop"
    )


def test_desktop_dir_linux(monkeypatch):
    monkeypatch.setenv("HOME", "/home/tester")
    assert paths.desktop_dir("linux") == os.path.join(
        "/home/tester", "Desktop"
    )


def test_annotations_dirname():
    assert (
        paths.annotations_dirname(datetime.date(2026, 7, 10))
        == "Annotations_20260710"
    )
