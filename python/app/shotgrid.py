# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""ShotGrid queries for the download-notes flow.

Every function takes a duck-typed ``sg`` (a ``shotgun_api3.Shotgun``-like
object) as its first argument, so the module needs no ``sgtk`` import and is
testable with a fake.
"""

_NOTE_FIELDS = ["id", "subject", "attachments"]


def find_notes_for_entities(sg, entity_type, entity_ids):
    """Return Notes linked directly (via ``note_links``) to any selected
    entity."""
    entities = [{"type": entity_type, "id": i} for i in entity_ids]
    return sg.find(
        "Note",
        [["note_links", "in", entities]],
        _NOTE_FIELDS,
    )


def attachments_from_notes(notes):
    """Flatten Notes into attachment dicts tagged with their source note.

    Each result has ``note_id``, ``attachment_id``, ``filename`` (falling back
    to ``"attachment"``), and ``entity`` (the raw Attachment dict to
    download).
    """
    result = []
    for note in notes:
        note_id = note["id"]
        for att in note.get("attachments") or []:
            result.append(
                {
                    "note_id": note_id,
                    "attachment_id": att["id"],
                    "filename": att.get("name") or "attachment",
                    "entity": att,
                }
            )
    return result


def download_attachment(sg, attachment, dest_path) -> None:
    """Download an uploaded attachment to ``dest_path``."""
    sg.download_attachment(attachment, file_path=dest_path)
