# pick-movie

Can't decide what to watch? Keep a watchlist in JSON and let the script choose.

Two small Python scripts, no dependencies beyond the standard library.

## Requirements

Python 3. That's it — no install step, no virtualenv, no packages.

## Pick something to watch

```bash
python3 pick_movie.py
```

```
How about watching: Mulholland Drive?
```

Reads `watchlist.json` from the current directory, so run it from the repo root.

## Add titles to the watchlist

Put new titles in a plain text file, one per line:

```
Dr. Strangelove
The Odyssey
```

Then merge them in:

```bash
python3 import_titles.py new_titles.txt watchlist.json
```

```
Backed up to watchlist.json.20260822-174958.bak.
Added 2 new title(s); watchlist.json now has 54.
```

Both paths are arguments, so this one can run from anywhere.

### What it does to your list

- **Backs up first.** The watchlist is copied to `watchlist.json.<timestamp>.bak` before anything is written.
- **Skips duplicates,** ignoring case. A title already on the list won't be added again, and `mulholland drive` won't join the existing `Mulholland Drive` — the spelling already in the watchlist wins.
- **Tidies input.** Leading and trailing whitespace is trimmed and blank lines are ignored, so a sloppy text file is fine.
- **Leaves the text file alone.** Clear it out yourself before staging the next batch.

The staging file is never modified, and the watchlist is only ever rewritten after a successful read of both inputs.

## Watchlist format

```json
{
  "watchlist": [
    { "title": "Manhunter" },
    { "title": "The Conversation" }
  ]
}
```

Every entry is an object with a single `title` key. `import_titles.py` writes this shape back out, one entry per line.

## Exit codes

`import_titles.py` exits `1` with a message if a file is missing, the JSON is malformed, or an entry has no `title` key. `pick_movie.py` prints its errors but always exits `0`.
