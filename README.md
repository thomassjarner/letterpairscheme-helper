# BLD Letter Memo

A desktop app (built with [Flet](https://flet.dev)) for managing 3x3
blindfolded (3BLD) letter schemes and their letter-pair memo words, as a
foundation for future scramble-tracing and practice features.

## Status

Implemented so far:
- Persistent storage layer (JSON, stored outside the repo — see below)
- **Letter Schemes** page: create / rename / duplicate / delete / switch
  schemes, per-category (corners/edges) buffer selection, and a grouped
  sticker grid matching the requested U/L/F/R/B/D layout
- **Letter Pairs** page: one global, searchable/filterable, inline-editable
  word table shared across all schemes, with Active/Inactive status and
  keyboard (Enter) navigation between rows

Not yet implemented (intentionally stubbed, see `core/tracer.py`):
- Scramble → Memo tracing (needs a conventions discussion: orientation,
  cycle breaks, parity, memo grouping — see the docstring in
  `core/tracer.py`)
- Practice/quiz features

**This code has not been run end-to-end**, because the sandbox it was
written in has no network access and can't `pip install flet`. The
`core/` and `data/` layers (all the actual logic — sticker/piece
definitions, valid-pair rules, JSON storage, models) have been unit
tested directly with plain Python and all checks pass. The `ui/` layer
(Flet widgets) is written carefully against the Flet 0.24 API but has
**not** been visually verified. Please run it locally and report back
anything that errors or looks wrong — that's expected for a first pass
on UI code that couldn't be executed before delivery.

## Running it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

This opens a native desktop window. (Flet can also run as a web app via
`flet run --web main.py` if you'd ever want that instead.)

## Where your data lives

Schemes and words are saved to your OS's standard per-user data
directory (via `platformdirs`), **not** inside this repository:

- Linux: `~/.local/share/BLDLetterMemo/data.json`
- macOS: `~/Library/Application Support/BLDLetterMemo/data.json`
- Windows: `%APPDATA%\BLDLetterMemo\data.json`

This means pulling app updates from GitHub (or reinstalling) never
touches your saved schemes or the word dictionary. The Settings page
shows the exact path and has an "Export backup" button.

If the data file is ever unreadable (corrupted), it's copied aside as
`data.corrupt-backup.json` next to it rather than silently discarded.

## Architecture

```
core/       Pure logic, no I/O, no Flet import. Sticker/piece definitions
            and the valid-letter-pair rules live here so BLD rules can be
            refined later without touching the GUI. Also the stub for the
            future scramble tracer.
data/       Storage layer. models.py defines the data shapes; repository.py
            is an abstract interface; json_repository.py is the current
            JSON-backed implementation. Swapping to SQLite later means
            writing a new repository implementation, not touching ui/.
ui/         Flet widgets/pages. state.py is the single place pages read
            and mutate data through (every mutation autosaves).
```

### A note on the global word dictionary

Per your call: a pair like `AB` has exactly **one** word regardless of
whether it comes from a corner scheme, an edge scheme, or several
different schemes at once (`core/pairs.get_active_pairs` reports *where*
a pair is active, for display, but there's only ever one word for it).

### Known trade-offs worth knowing about

- The Letter Schemes grid does **not** rebuild itself on every keystroke
  (that would steal keyboard focus). Duplicate-letter warnings refresh
  when you switch tabs/schemes, not instantly as you type.
- The Letter Pairs table renders all matching rows at once. Flet's
  `ListView` doesn't virtualize in the classic API, so if you get into
  the high hundreds/low thousands of pairs and it feels sluggish, that's
  the place to optimize next (e.g. pagination or a virtualized list).
- `flet==0.24.1` is pinned deliberately — Flet's API changed significantly
  in later versions, and this code targets the classic (pre-0.70-ish) API.

## Development

The BLD-validity rules are unit-testable without any GUI dependency:

```python
from data.models import LetterScheme
from core.pairs import generate_letter_pairs, find_duplicate_letters
```

See the module docstrings in `core/pairs.py` and `core/cube_definitions.py`
for the exact rules currently implemented.
