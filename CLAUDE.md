# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

Pick something to watch:

```bash
python3 pick_movie.py
```

Add new titles to the watchlist:

```bash
python3 import_titles.py new_titles.txt watchlist.json
```

There is no build, test suite, dependency manifest, or virtualenv — both scripts use only the standard library (`json`, `random`, `argparse`, `shutil`, `sys`, `datetime`).

This directory is **not under version control**. Deleting or overwriting a file here is unrecoverable, so confirm before doing either — the watchlist is curated by hand.

## Architecture

Two scripts and two data files:

- `pick_movie.py` — reads `watchlist.json`, prints one randomly chosen title. `get_random_item()` returns a user-facing string for every outcome, including errors (missing file, bad JSON, empty list); the module body prints it. There is no exit-code signalling, so callers can't distinguish success from failure. The path `'watchlist.json'` is hardcoded and relative, so it only works when run from the repo root.
- `import_titles.py` — merges a plain-text list of titles into a watchlist. Takes both paths as arguments (`argparse`), so unlike `pick_movie.py` it is not tied to the repo root. Exits 1 with a message on a missing file, malformed JSON, or an entry missing its `title` key.
- `watchlist.json` — `{"watchlist": [{"title": "..."}]}`, one key per entry. `pick_movie.py` reads `selection['title']` directly, so an entry missing that key raises `KeyError` rather than being handled.
- `new_titles.txt` — staging file for `import_titles.py`: one title per line, no quotes or punctuation. Contents are merged into the watchlist but the file itself is left alone, so clear it out after an import to avoid re-importing.

`resume.txt` is a personal scratch file for keeping track of terminal sessions. It is unrelated to the watchlist tooling — leave it alone.

## How import_titles.py handles the merge

Behaviour worth knowing before changing it — each rule exists because the source lists violated it:

- **Backup first.** Copies the watchlist to `<path>.<YYYYMMDD-HHMMSS>.bak` before writing. This happens before the inputs are validated, so a run that fails on a bad file still leaves a `.bak` behind.
- **Dedupe is case-insensitive and keeps the first spelling.** Existing watchlist entries come first, so their casing wins over the incoming file's (`Wolf of Wall Street` survives, `wolf of wall street` does not). Duplicates within the incoming file collapse too.
- **Whitespace is stripped and blank lines are skipped.** The original text lists had trailing spaces on most lines, which would otherwise defeat the dedupe entirely.
- **Titles are written through `json.dumps`,** so quotes and backslashes in a title escape correctly. Don't hand-format the entries.

Output is written as one `{ "title": "..." }` per line rather than via `json.dump(indent=2)`, to match the existing file's formatting.
