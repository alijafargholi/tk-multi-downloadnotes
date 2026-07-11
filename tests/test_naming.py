# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
from app import naming


def test_target_filename():
    assert naming.target_filename(12, 34, "annot.jpg") == "12_34_annot.jpg"


def test_plan_downloads_maps_each_attachment():
    attachments = [
        {
            "note_id": 1,
            "attachment_id": 2,
            "filename": "a.jpg",
            "entity": {"id": 2},
        },
        {
            "note_id": 1,
            "attachment_id": 3,
            "filename": "a.jpg",
            "entity": {"id": 3},
        },
    ]
    assert naming.plan_downloads(attachments) == [
        (attachments[0], "1_2_a.jpg"),
        (attachments[1], "1_3_a.jpg"),
    ]


def test_different_attachments_never_collide():
    # Same filename, different note/attachment ids -> distinct target names.
    a = naming.target_filename(1, 2, "annot.jpg")
    b = naming.target_filename(1, 3, "annot.jpg")
    c = naming.target_filename(4, 2, "annot.jpg")
    assert a != b
    assert a != c
    assert len({a, b, c}) == 3


def test_note_and_attachment_ids_are_positional():
    # Swapping the two ids must change the result (order is significant).
    assert naming.target_filename(7, 8, "x.png") != naming.target_filename(
        8, 7, "x.png"
    )


def test_safe_filename_strips_posix_separators():
    assert naming.safe_filename("../../evil.jpg") == "evil.jpg"
    assert naming.safe_filename("a/b/c.jpg") == "c.jpg"


def test_safe_filename_strips_windows_separators():
    assert naming.safe_filename("..\\..\\evil.jpg") == "evil.jpg"


def test_safe_filename_empty_or_trailing_separator():
    assert naming.safe_filename("") == "attachment"
    assert naming.safe_filename(None) == "attachment"
    assert naming.safe_filename("foo/") == "attachment"


def test_target_filename_sanitizes():
    assert naming.target_filename(1, 2, "../x.jpg") == "1_2_x.jpg"
