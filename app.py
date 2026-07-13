# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
from sgtk.platform import Application  # ty: ignore[unresolved-import]


class DownloadNotesApp(Application):
    """Download attachments from Notes linked to the selected entities."""

    def init_app(self):
        """Register the multi-select command with the current engine."""
        self.engine.register_command(
            "download_notes",
            self.download_notes,
            {
                "title": "Download Note Attachments",
                "supports_multiple_selection": True,
            },
        )

    def download_notes(self, entity_type, entity_ids):
        """Resolve Notes linked to the selection and download attachments."""
        payload = self.import_module("app")
        try:
            payload.download.run(
                entity_type, entity_ids, self.shotgun, self.logger
            )
        except payload.download.DownloadNotesError as err:
            self.logger.error(str(err))
        except Exception:
            self.logger.exception(
                "Download Note Attachments failed unexpectedly."
            )
