# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
from app import shotgrid


class FakeSg:
    def __init__(self, find_result=None):
        self.find_result = find_result or []
        self.find_calls = []
        self.downloaded = []

    def find(self, entity_type, filters, fields=None, **kwargs):
        self.find_calls.append((entity_type, filters, fields))
        return self.find_result

    def download_attachment(self, attachment, file_path=None):
        self.downloaded.append((attachment, file_path))


def test_find_notes_builds_in_filter_over_selection():
    sg = FakeSg(find_result=[{"id": 5}])
    notes = shotgrid.find_notes_for_entities(sg, "Shot", [1, 2])
    assert notes == [{"id": 5}]
    entity_type, filters, fields = sg.find_calls[0]
    assert entity_type == "Note"
    assert filters == [
        [
            "note_links",
            "in",
            [{"type": "Shot", "id": 1}, {"type": "Shot", "id": 2}],
        ]
    ]
    assert "attachments" in fields


def test_attachments_from_notes_flattens():
    a0 = {"type": "Attachment", "id": 100, "name": "a.jpg"}
    a1 = {"type": "Attachment", "id": 101, "name": "b.jpg"}
    notes = [
        {"id": 10, "attachments": [a0, a1]},
        {"id": 11, "attachments": []},
        {"id": 12},  # no attachments key at all
    ]
    assert shotgrid.attachments_from_notes(notes) == [
        {
            "note_id": 10,
            "attachment_id": 100,
            "filename": "a.jpg",
            "entity": a0,
        },
        {
            "note_id": 10,
            "attachment_id": 101,
            "filename": "b.jpg",
            "entity": a1,
        },
    ]


def test_attachments_from_notes_missing_name():
    notes = [{"id": 1, "attachments": [{"type": "Attachment", "id": 9}]}]
    assert shotgrid.attachments_from_notes(notes)[0]["filename"] == (
        "attachment"
    )


def test_download_attachment_delegates():
    sg = FakeSg()
    att = {"type": "Attachment", "id": 5}
    shotgrid.download_attachment(sg, att, "/tmp/x.jpg")
    assert sg.downloaded == [(att, "/tmp/x.jpg")]
