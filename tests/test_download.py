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

from app import download

TODAY = datetime.date(2026, 7, 10)
FOLDER = "Annotations_20260710"


class FakeSg:
    def __init__(self, notes):
        self.notes = notes
        self.fail_ids = set()
        self.partial_ids = set()
        self.downloaded = []

    def find(self, entity_type, filters, fields=None, **kwargs):
        return self.notes

    def download_attachment(self, attachment, file_path=None):
        if attachment["id"] in self.partial_ids:
            with open(  # ty: ignore[no-matching-overload]
                file_path, "w"
            ) as fh:
                fh.write("partial")
            raise RuntimeError("boom-after-partial")
        if attachment["id"] in self.fail_ids:
            raise RuntimeError("boom")
        self.downloaded.append((attachment, file_path))
        with open(file_path, "w") as fh:  # ty: ignore[no-matching-overload]
            fh.write("data")


class FakeLogger:
    def __init__(self):
        self.infos = []
        self.errors = []

    def info(self, msg):
        self.infos.append(msg)

    def error(self, msg):
        self.errors.append(msg)


def _note(note_id, attachments):
    return {"id": note_id, "attachments": attachments}


def _att(att_id, name):
    return {"type": "Attachment", "id": att_id, "name": name}


def test_no_entities_selected(tmp_path):
    sg = FakeSg([])
    logger = FakeLogger()
    revealed = []
    download.run(
        "Shot",
        [],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=revealed.append,
        today=TODAY,
    )
    assert revealed == []
    assert os.listdir(tmp_path) == []


def test_no_notes_creates_nothing(tmp_path):
    sg = FakeSg([])
    logger = FakeLogger()
    revealed = []
    download.run(
        "Shot",
        [1],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=revealed.append,
        today=TODAY,
    )
    assert revealed == []
    assert os.listdir(tmp_path) == []


def test_downloads_and_reveals(tmp_path):
    notes = [_note(50, [_att(500, "a.jpg"), _att(501, "b.jpg")])]
    sg = FakeSg(notes)
    logger = FakeLogger()
    revealed = []
    download.run(
        "Shot",
        [1],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=revealed.append,
        today=TODAY,
    )
    folder = tmp_path / FOLDER
    assert (folder / "50_500_a.jpg").exists()
    assert (folder / "50_501_b.jpg").exists()
    assert revealed == [str(folder)]


def test_skips_existing_file(tmp_path):
    notes = [_note(50, [_att(500, "a.jpg")])]
    sg = FakeSg(notes)
    logger = FakeLogger()
    folder = tmp_path / FOLDER
    folder.mkdir()
    (folder / "50_500_a.jpg").write_text("old")
    download.run(
        "Shot",
        [1],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=lambda d: None,
        today=TODAY,
    )
    assert sg.downloaded == []
    assert (folder / "50_500_a.jpg").read_text() == "old"


def test_per_file_failure_is_isolated(tmp_path):
    notes = [_note(50, [_att(500, "a.jpg"), _att(501, "b.jpg")])]
    sg = FakeSg(notes)
    sg.fail_ids = {500}
    logger = FakeLogger()
    download.run(
        "Shot",
        [1],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=lambda d: None,
        today=TODAY,
    )
    folder = tmp_path / FOLDER
    assert not (folder / "50_500_a.jpg").exists()
    assert (folder / "50_501_b.jpg").exists()
    assert any("Failed to download" in e for e in logger.errors)


def test_partial_download_is_removed(tmp_path):
    notes = [_note(50, [_att(500, "a.jpg")])]
    sg = FakeSg(notes)
    sg.partial_ids = {500}
    logger = FakeLogger()
    download.run(
        "Shot",
        [1],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=lambda d: None,
        today=TODAY,
    )
    folder = tmp_path / FOLDER
    assert not (folder / "50_500_a.jpg").exists()


def test_no_reveal_when_all_downloads_fail(tmp_path):
    notes = [_note(50, [_att(500, "a.jpg")])]
    sg = FakeSg(notes)
    sg.fail_ids = {500}
    logger = FakeLogger()
    revealed = []
    download.run(
        "Shot",
        [1],
        sg,
        logger,
        desktop_dir=str(tmp_path),
        reveal_fn=revealed.append,
        today=TODAY,
    )
    assert revealed == []
