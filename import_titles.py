import argparse
import json
import shutil
import sys
from datetime import datetime


def read_new_titles(file_path):
    """Read one title per line from a plain text file, ignoring blank lines."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]


def read_watchlist(file_path):
    """Read the titles out of a watchlist.json file, in order."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [entry['title'] for entry in data.get("watchlist", [])]


def dedupe(titles):
    """Drop repeats, keeping the first spelling of each title.

    Matching is case-insensitive so "wolf of wall street" doesn't survive
    alongside "Wolf of Wall Street".
    """
    unique = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key not in seen:
            seen.add(key)
            unique.append(title)
    return unique


def write_watchlist(file_path, titles):
    """Write titles back out in watchlist.json's format."""
    entries = ',\n'.join(f'    {{ "title": {json.dumps(t)} }}' for t in titles)
    with open(file_path, 'w') as file:
        file.write('{\n  "watchlist": [\n' + entries + '\n  ]\n}\n')


def backup(file_path):
    """Copy the watchlist aside before it gets overwritten."""
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = f'{file_path}.{stamp}.bak'
    shutil.copy2(file_path, backup_path)
    return backup_path


def import_titles(new_titles_path, watchlist_path):
    backup_path = backup(watchlist_path)

    existing = read_watchlist(watchlist_path)
    new = read_new_titles(new_titles_path)

    combined = dedupe(existing + new)
    write_watchlist(watchlist_path, combined)

    added = len(combined) - len(dedupe(existing))
    removed = len(existing) - len(dedupe(existing))
    return backup_path, added, removed, len(combined)


def main():
    parser = argparse.ArgumentParser(
        description="Add movie titles from a text file to a watchlist.json.")
    parser.add_argument('new_titles',
                        help="text file of new movies, one title per line")
    parser.add_argument('watchlist',
                        help="the watchlist.json file to update in place")
    args = parser.parse_args()

    try:
        backup_path, added, removed, total = import_titles(
            args.new_titles, args.watchlist)
    except FileNotFoundError as error:
        sys.exit(f"Error: Could not find {error.filename}.")
    except json.JSONDecodeError:
        sys.exit(f"Error: {args.watchlist} is not valid JSON.")
    except KeyError:
        sys.exit(f"Error: An entry in {args.watchlist} is missing a 'title' key.")

    print(f"Backed up to {backup_path}.")
    if removed:
        print(f"Removed {removed} duplicate(s) already in {args.watchlist}.")
    print(f"Added {added} new title(s); {args.watchlist} now has {total}.")


if __name__ == '__main__':
    main()
