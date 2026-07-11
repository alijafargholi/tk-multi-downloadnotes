# tk-multi-downloadnotes

A Flow Production Tracking (ShotGrid) Toolkit app that downloads the
attachments of Notes linked to the entities you select, straight to your
Desktop.

## For producers

Select one or more entities in Flow Production Tracking (Shot, Asset, Task,
Version, or any note-linkable entity), right-click, and run **Download Note
Attachments**. The app will:

1. Find the Notes linked directly to your selected entities.
2. Download every Note's attachments into
   `~/Desktop/Annotations_yyyymmdd/` (today's date).
   - Each file is named `<note_id>_<attachment_id>_<original name>` so files
     from different notes never collide.
   - A file that is already on your Desktop is **not** re-downloaded and
     **never** overwritten.
3. Open the `Annotations_yyyymmdd` folder when it finishes.

Multi-entity selection is supported, and both macOS and Windows work. If a
selection has no linked notes (or no attachments), the app logs that and does
nothing else.

## For developers

### Layout

| File | Responsibility |
|------|----------------|
| `app.py` | sgtk bundle: registers the multi-select `download_notes` command. The **only** file that imports `sgtk`. |
| `info.yml` | Toolkit app manifest. |
| `python/app/download.py` | Orchestrator (`run(...)`) plus the `DownloadNotesError` type. |
| `python/app/shotgrid.py` | ShotGrid queries: linked notes, attachment flatten, download. |
| `python/app/naming.py` | Pure filename planning (`{note_id}_{attachment_id}_{filename}`). |
| `python/app/paths.py` | Cross-platform Desktop dir + dated folder name. |
| `python/app/reveal.py` | Open the download folder in the OS file browser. |

Everything under `python/app/` is `sgtk`-free: dependencies (`sg`, logger,
`desktop_dir`, `reveal_fn`, `today`) are injected, so each module is
unit-testable with fakes. `app.py` is the thin adapter that wires the live
sgtk objects into `download.run(...)`.

### Requirements

- Runs inside the Toolkit engine's Python; targets **Python 3.11+** so it
  works in older Flow Production Tracking Desktop builds. Local development
  uses **Python 3.13** (see `.python-version`).
- Managed with [`uv`](https://docs.astral.sh/uv/).

### Setup & checks

```bash
uv sync                      # create the venv and install dev dependencies
uv run pytest                # run the test suite
uv run ruff check .          # lint
uv run ruff format --check . # format check
uv run ty check              # type check
pre-commit install           # enable the hooks locally
```

### Installing into a config

Add a location descriptor and register the app on the desired `tk-shotgun`
contexts (e.g. `shot`, `asset`, `version`, `task`). For local development use
a `type: dev` descriptor pointing at this checkout; switch to a
`type: shotgun` payload descriptor before releasing.
