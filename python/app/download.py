# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""Orchestrates: selection -> linked notes -> attachments -> download -> open.

Pure of ``sgtk``; the caller (``app.py``) injects the ShotGrid connection,
logger, and selection.
"""

import datetime
import os

from . import naming, paths, reveal, shotgrid


class DownloadNotesError(Exception):
    """Raised when the flow cannot complete; the message is user-facing."""


def run(
    entity_type,
    entity_ids,
    sg,
    logger,
    desktop_dir=None,
    reveal_fn=reveal.reveal,
    today=None,
) -> None:
    """Download attachments from Notes linked to the selected entities."""
    if not entity_ids:
        logger.info("No entities selected.")
        return

    today = today or datetime.date.today()

    notes = shotgrid.find_notes_for_entities(sg, entity_type, entity_ids)
    attachments = shotgrid.attachments_from_notes(notes)
    if not attachments:
        logger.info("No note attachments found for the selection.")
        return

    dest_dir = os.path.join(
        desktop_dir or paths.desktop_dir(),
        paths.annotations_dirname(today),
    )
    os.makedirs(dest_dir, exist_ok=True)

    downloaded = skipped = failed = 0
    for attachment, target in naming.plan_downloads(attachments):
        dest_path = os.path.join(dest_dir, target)
        if os.path.exists(dest_path):
            skipped += 1
            continue
        try:
            shotgrid.download_attachment(sg, attachment["entity"], dest_path)
            downloaded += 1
        except Exception as err:
            failed += 1
            logger.error("Failed to download %s: %s" % (target, err))

    reveal_fn(dest_dir)
    logger.info(
        "Download complete: %d downloaded, %d skipped, %d failed."
        % (downloaded, skipped, failed)
    )
