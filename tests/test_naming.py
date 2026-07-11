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
        {"note_id": 1, "attachment_id": 2, "filename": "a.jpg",
         "entity": {"id": 2}},
        {"note_id": 1, "attachment_id": 3, "filename": "a.jpg",
         "entity": {"id": 3}},
    ]
    assert naming.plan_downloads(attachments) == [
        (attachments[0], "1_2_a.jpg"),
        (attachments[1], "1_3_a.jpg"),
    ]


def test_same_attachment_maps_to_same_name():
    assert (
        naming.target_filename(7, 8, "x.png")
        == naming.target_filename(7, 8, "x.png")
    )
