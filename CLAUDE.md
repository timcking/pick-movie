# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

Pick something to watch (CLI):

```bash
python3 pick_movie.py
```

Add new titles to the watchlist:

```bash
python3 import_titles.py new_titles.txt watchlist.json
```

Preview the web version (`index.html`):

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000/. Opening `index.html` directly as a `file://` URL doesn't work — browsers block `fetch()` of local files under that protocol, so the page shows "Could not load the watchlist."

There is no build, test suite, or dependency manifest. The two Python scripts use only the standard library (`json`, `random`, `argparse`, `shutil`, `sys`, `datetime`); `index.html` uses only vanilla JS (no framework, no bundler).

## Repository

Git repo, pushed to the **public** GitHub repo `timcking/pick-movie` on branch `main`, deployed via GitHub Pages at https://timcking.github.io/pick-movie/. Commit and push only when asked.

The repo was flipped from private to public deliberately, to make GitHub Pages hosting possible (Pages doesn't serve private repos on the free tier). Treat that as one-way — old commits are forkable/cacheable once public, so don't suggest flipping back as if it undoes exposure.

`.gitignore` excludes `resume.txt`, `pick-movie-session.md` (an exported chat transcript kept locally for reference), the `*.bak` files `import_titles.py` writes, and the usual Python and macOS noise.

`watchlist.json` is curated by hand and is the point of the project — it is committed, but confirm before overwriting or deleting it rather than relying on `git checkout` to bail you out.

Auto-mode's permission classifier blocks Claude Code's own `git commit`/`git push` when the diff touches `index.html`, since the file embeds a live OMDb API key and the classifier treats that as a secret-looking change — it blocks even after the user has confirmed in chat. Don't retry; hand the exact `git add`/`commit`/`push` commands to the user and let them run it.

## Architecture

Two Python scripts, a web front end, two data files, and the docs:

- `pick_movie.py` — reads `watchlist.json`, prints one randomly chosen title. `get_random_item()` returns a user-facing string for every outcome, including errors (missing file, bad JSON, empty list); the module body prints it. There is no exit-code signalling, so callers can't distinguish success from failure. The path `'watchlist.json'` is hardcoded and relative, so it only works when run from the repo root.
- `import_titles.py` — merges a plain-text list of titles into a watchlist. Takes both paths as arguments (`argparse`), so unlike `pick_movie.py` it is not tied to the repo root. Exits 1 with a message on a missing file, malformed JSON, or an entry missing its `title` key.
- `index.html` — the web front end, deployed as-is via GitHub Pages. Static HTML/CSS/JS, no build step or framework. Fetches `watchlist.json` client-side and picks randomly, the same idea as `pick_movie.py` but reimplemented in JS rather than sharing code with it. Details below.
- `watchlist.json` — `{"watchlist": [{"title": "..."}]}`, one key per entry. `pick_movie.py` reads `selection['title']` directly, so an entry missing that key raises `KeyError` rather than being handled. Must stay at the repo root — `index.html`'s `fetch('watchlist.json')` is a relative path, and Pages serves the repo as-is.
- `new_titles.txt` — staging file for `import_titles.py`: one title per line, no quotes or punctuation. Kept empty between imports, since the script never clears it itself and a leftover line would just be re-imported (harmlessly, thanks to the dedupe).
- `README.md` — user-facing usage for both scripts. Update it alongside any change to a command line, an output string, or the watchlist format.

This file explains *why* the merge rules below exist; the README explains *how* to run things. Keep that split.

`resume.txt` is a personal scratch file for keeping track of terminal sessions. It is unrelated to the watchlist tooling — leave it alone.

### index.html

Clicking the current title or its poster looks the title up via the [OMDb API](https://www.omdbapi.com/) — a free, key-based wrapper around IMDb data; IMDb itself has no public self-serve API. A successful lookup navigates to the exact `imdb.com/title/<id>/` page; a miss falls back to an `imdb.com/find/?q=...` search. The same OMDb response also supplies the poster image shown centered above the title, so one lookup per pick covers both the poster and the eventual click-through — the poster/title click doesn't trigger a second API call.

Two non-obvious choices worth preserving:

- **The API key is embedded directly in the client-side JS**, visible to anyone who views source. That's the expected pattern for OMDb's free tier (rate-limited per key rather than treated as a secret), and the repo is already public — but it does mean this file is never a place to put an actual secret.
- **Clicking navigates the current tab** (`window.location.href = ...`) rather than opening a new one. An earlier version tried opening a blank tab synchronously and redirecting it once the async OMDb fetch resolved (the standard workaround for "open a tab after an async lookup"); it was silently blocked as a popup in real testing. Don't reintroduce that pattern without verifying it against an actual browser, not just assuming it works because it's the documented workaround.

OMDb's exact-title match (`t=`) can pick the wrong film for an ambiguous or short title (e.g. `Anchorman` matched an obscure 2009 short instead of the 2004 comedy) — a data quirk of the API, not a bug in `index.html`.

## How import_titles.py handles the merge

Behaviour worth knowing before changing it — each rule exists because the source lists violated it:

- **Backup first.** Copies the watchlist to `<path>.<YYYYMMDD-HHMMSS>.bak` before writing. This happens before the inputs are validated, so a run that fails on a bad file still leaves a `.bak` behind.
- **Dedupe is case-insensitive and keeps the first spelling.** Existing watchlist entries come first, so their casing wins over the incoming file's (`Wolf of Wall Street` survives, `wolf of wall street` does not). Duplicates within the incoming file collapse too.
- **Whitespace is stripped and blank lines are skipped.** The original text lists had trailing spaces on most lines, which would otherwise defeat the dedupe entirely.
- **Titles are written through `json.dumps`,** so quotes and backslashes in a title escape correctly. Don't hand-format the entries.

Output is written as one `{ "title": "..." }` per line rather than via `json.dump(indent=2)`, to match the existing file's formatting.
