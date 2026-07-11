# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""Pure filename planning for downloaded note attachments.

The name is unconditional: ``{note_id}_{attachment_id}_{filename}``. Because
ShotGrid attachment ids are globally unique, the name is unique by
construction and stable per attachment, so re-runs never collide and the
orchestrator can skip any target that already exists on disk.
"""


def target_filename(note_id, attachment_id, filename) -> str:
    """Build the unique local filename for a note attachment."""
    return "%s_%s_%s" % (note_id, attachment_id, filename)


def plan_downloads(attachments):
    """Map gathered attachment dicts to ``(attachment, target_filename)``.

    Each attachment dict has ``note_id``, ``attachment_id`` and ``filename``.
    """
    return [
        (
            a,
            target_filename(
                a["note_id"], a["attachment_id"], a["filename"]
            ),
        )
        for a in attachments
    ]
