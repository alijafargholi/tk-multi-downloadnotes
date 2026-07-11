# tk-multi-downloadnotes — Design

**Date:** 2026-07-10
**Status:** Approved (pending spec review)

## Summary

A Flow Production Tracking (ShotGrid) Toolkit app that lets producers
right-click one or more entities in the ShotGrid web UI (Shot, Asset, Task,
Version, or any note-linkable entity), find the Notes linked directly to those
entities, and download every Note's attachments to a dated folder on the
Desktop.

Launched from the **tk-shotgun** engine (web action menu). Supports
multi-entity selection. Works on macOS and Windows.

## Goals

- One action — **"Download Note Attachments"** — on the right-click menu of
  note-linkable entities.
- Gather Notes whose `note_links` point **directly** at the selected
  entities, and download the attachments on those Notes.
- Save everything into `~/Desktop/Annotations_yyyymmdd/`.
- Never re-download a file that is already present; never overwrite.
- Silent operation (log only), then open the folder in Finder/Explorer.
- Entity-type agnostic in code; the config decides where the action appears.

## Non-goals (YAGNI)

- No traversal to child/related entities (selecting a Shot does **not** pull
  its Versions'/Tasks' notes). Direct `note_links` only.
- No Reply attachments — only each Note's own `attachments` field.
- No summary dialog / progress UI.
- No filtering by author, date, or note status.

## Decisions (resolved during brainstorming)

| Question | Decision |
|----------|----------|
| Which notes? | Direct `note_links` only. |
| Which attachments? | Note `attachments` field only (not Replies). |
| Folder layout | Flat inside `Annotations_yyyymmdd/`; every file named `{note_id}_{attachment_id}_{filename}`. |
| While/after download | Silent + open the folder when done. |
| Command title | "Download Note Attachments". |
| Type checking | Add `ty` (dev dep + pre-commit hook). |

## Architecture

Mirrors the studio reference app `tk-multi-launchphotoshop`: a thin sgtk
adapter wiring live sgtk objects into a pure, dependency-injected
`python/app/` package. `app.py` is the **only** file that imports `sgtk`;
everything under `python/app/` is sgtk-free and unit-testable with fakes.

| File | Responsibility |
|------|----------------|
| `app.py` | sgtk bundle. Registers the `download_notes` command with `"supports_multiple_selection": True`. Callback `(entity_type, entity_ids)` → `import_module("app")` → `download.run(...)`. Catches `DownloadNotesError` (logs message) and unexpected `Exception` (logs traceback). |
| `python/app/download.py` | Orchestrator `run(...)` + the user-facing `DownloadNotesError` type. Pure of sgtk. |
| `python/app/shotgrid.py` | ShotGrid queries: find Notes linked to the selected entities, extract their attachments, download an attachment. Duck-typed `sg`; no sgtk import. |
| `python/app/naming.py` | Pure collision-planning: given all gathered attachments, decide each target filename. |
| `python/app/paths.py` | Cross-platform `desktop_dir()` (from the reference) + `annotations_dirname(today)` → `Annotations_yyyymmdd`. |
| `python/app/reveal.py` | Open a directory in Finder/Explorer, cross-platform. Injected runner for testability. |

### tk-shotgun multi-select mechanism

The `tk-shotgun` engine invokes commands registered with
`"supports_multiple_selection": True` via `execute_old_style_command`, calling
the callback as `callback(entity_type, entity_ids)` — a single entity type and
a list of ids (confirmed in `tk-shotgun/engine.py` and the
`tk-shotgun-folders` app). This is the app's entry point.

## Data flow (`download.run`)

Signature:

```python
run(entity_type, entity_ids, sg, logger,
    desktop_dir=None, reveal_fn=reveal.reveal, today=None)
```

1. If `entity_ids` is empty → log "No entities selected." and return.
2. `shotgrid.find_notes_for_entities(sg, entity_type, entity_ids)` → Notes
   whose `note_links` point directly at any selected entity, each with its
   `attachments`.
3. Flatten to a list of attachments, each tagged with its source `note_id`,
   `attachment_id`, and `filename`.
4. If none → log "No note attachments found." and return (no empty folder
   created, nothing opened).
5. `naming.plan_downloads(attachments)` → `[(attachment, target_filename), ...]`.
6. Create `~/Desktop/Annotations_yyyymmdd/`. For each planned file: if the
   target already exists on disk → skip ("already downloaded"); else
   `shotgrid.download_attachment(...)`. Per-file failures are logged and the
   loop continues.
7. `reveal_fn(dest_dir)` to open the folder. Log a summary
   (`N downloaded, M skipped, K failed`).

`today` and `reveal_fn` are injected so the folder name and the folder-open
side effect are deterministic and mockable in tests. `today` defaults to
`datetime.date.today()`, `reveal_fn` to `reveal.reveal`.

## Naming + idempotency rule

Every downloaded file uses one unconditional convention:

```
{note_id}_{attachment_id}_{filename}
```

- No conditional/collision logic. Because ShotGrid attachment ids are globally
  unique, this name is unique by construction — two attachments can never
  collide, and the same attachment always maps to the same name.
- **Skip = already downloaded**: before downloading, if the target name
  already exists in the folder, skip it (never overwrite). Since the name is a
  stable function of the attachment, re-running the action never re-downloads a
  file that is already present.

`naming.target_filename(note_id, attachment_id, filename)` is a small pure
function; `naming.plan_downloads(attachments)` maps the gathered attachments to
`[(attachment, target_filename), ...]`.

## Error handling & scope

- `DownloadNotesError` for user-facing stops (mirrors the reference's
  `LaunchError`); `app.py` logs its message cleanly. Unexpected exceptions are
  logged with a traceback.
- Per-attachment download failures are logged and skipped; the run continues
  and reports them in the summary.
- **Entity-type agnostic**: the code operates on whatever `entity_type`
  arrives. Which contexts show the action is decided by the config
  (`tk-config-greenportal`, `env/*.yml` under `settings.tk-shotgun.*`).
- Existing files are never overwritten.

## ShotGrid query notes (to verify during implementation)

- Notes linked to the selection use the multi-entity `note_links` field.
  Intended filter: `["note_links", "in", [{"type": entity_type, "id": id}, ...]]`
  returning Notes linked to any selected entity. Confirm the `"in"` operator
  semantics for multi-entity fields against the live site; fall back to a
  per-entity query if needed.
- Fields fetched per Note: `id`, `subject`, `attachments`. Each `attachments`
  element is an Attachment entity `{type, id, name}` where `name` is the
  filename.
- Download uses `sg.download_attachment({"type": "Attachment", "id": id},
  file_path=dest)` (works from the attachment id alone).

## Tooling

- **uv** for dependency management; **ruff** for lint/format; **pytest**
  (+ `pytest-cov`) for tests; **ty** for type checking; **pre-commit** to run
  them.
- `requires-python = ">=3.11"` (runs in older FPTR Desktop Python); local dev
  on **3.13** (`.python-version`). Ruff `target-version = "py311"`,
  `line-length = 79`, same rule set as the reference
  (`["C4","SIM","TCH","F401","E5","UP032","I0","N8"]`, ignore `SIM115`).
- Copyright header (Shotgun Software) on every source file.
- `conftest.py` inserts `python/` on `sys.path` (from the reference).
- `.pre-commit-config.yaml`: standard `pre-commit-hooks` (check-ast,
  check-yaml, check-case-conflict, check-merge-conflict, end-of-file-fixer,
  trailing-whitespace) + `astral-sh/ruff-pre-commit` (ruff + ruff-format) +
  `astral-sh/ty-pre-commit` (ty), following the config repo's layout.
- `info.yml` toolkit manifest (display name "Download Note Attachments",
  `supported_engines:` empty / all, `requires_core_version` as reference).

## Testing

One test module per source module, using fakes + `tmp_path` + injected
`today` / `reveal_fn`:

- `tests/test_download.py` — orchestration: empty selection, no notes, no
  attachments, happy path (downloads + skips), per-file failure isolation,
  folder opened only when something exists. Fake `sg`, fake `reveal_fn`,
  `tmp_path` as `desktop_dir`, fixed `today`.
- `tests/test_shotgrid.py` — note/attachment queries and download, with a fake
  duck-typed `sg`.
- `tests/test_naming.py` — `target_filename` produces
  `{note_id}_{attachment_id}_{filename}`; `plan_downloads` maps a list of
  attachments; stability (same attachment → same name).
- `tests/test_paths.py` — `annotations_dirname` formatting; `desktop_dir`
  per-platform branch (as in the reference).
- `tests/test_reveal.py` — correct command per platform via an injected runner
  (no real process spawned).

## File inventory

```
app.py
info.yml
pyproject.toml
README.md
LICENSE
conftest.py
.python-version            # 3.13
.gitignore
.pre-commit-config.yaml
python/__init__.py
python/app/__init__.py
python/app/download.py
python/app/shotgrid.py
python/app/naming.py
python/app/paths.py
python/app/reveal.py
tests/test_download.py
tests/test_shotgrid.py
tests/test_naming.py
tests/test_paths.py
tests/test_reveal.py
docs/superpowers/specs/2026-07-10-tk-multi-downloadnotes-design.md
```

## Config integration (separate repo, out of scope for this app's code)

To ship, `tk-config-greenportal` adds a location descriptor for
`tk-multi-downloadnotes` and registers it under the desired
`settings.tk-shotgun.<context>` blocks (e.g. `shot`, `asset`, `version`,
`task`). Dev uses a `type: dev` descriptor pointing at this checkout. This is
noted for context and handled in the config repo, not here.
