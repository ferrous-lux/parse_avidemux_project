# parse-avidemux-project

Standalone Python library for parsing Avidemux TinyPY project scripts into structured data (video path, segments, filters). No ffmpeg, ccextractor, or Avidemux CLI required.

- **Language:** Python 3.10+
- **No runtime dependencies**
- **Source:** `src/parse_avidemux_project/`

## Build / Lint / Test Commands

- **Install (editable):** `pip install -e .` (from repo root)
- **Run CLI:** `parse-avidemux-project <input.py> [-o output.json]`
- **Lint:** `ruff check src/` (install via `pip install ruff`)
- **Format:** `ruff format src/`
- **Type-check:** `mypy src/ --ignore-missing-imports`
- **Test (all):** `pytest tests/`
- **Test (single):** `pytest tests/test_parser.py::test_parse_project_file_adm1 -v`
- **Dev install:** `pip install -e ".[dev]"` (includes pytest)

## Code Style Guidelines

### Imports
```python
# 1. Standard library — one per line, alphabetical
import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict

# 2. Third-party — none for this package

# 3. Local — explicit relative imports
from .models import AvidemuxProject, Segment
from .parser import parse_project
```
- Group in three blocks separated by blank lines.
- Use relative imports within the package.

### Formatting
- **Indent:** 4 spaces. No tabs.
- **Line length:** ~100 columns (soft).
- **Quotes:** Double quotes for strings (`f"..."`).
- **Trailing commas:** Yes in multi-line structures (dicts, function calls).

### Types
- **Type hints:** Required for public API; optional internally.
- Use built-in generics: `list[...]`, `dict[...]`, `str | None` (Python 3.10+ union syntax).
- Prefer `from __future__ import annotations` if targeting older Python.

### Naming
| Kind | Convention | Example |
|---|---|---|
| Functions | `snake_case` | `parse_project()`, `us_to_iso_time()` |
| Variables | `snake_case` | `video_file`, `first_frame_pts` |
| Classes | `PascalCase` | `AvidemuxProject`, `Segment` |
| Private helpers | `_leading_underscore` | `_parse_video_file()` |
| Modules | `snake_case` | `parser.py`, `models.py` |
| CLI entry | `main()` | always inside `if __name__ == "__main__":` |

### Docstrings
```python
def function_name(param1, param2):
    """
    Short summary line.

    Parameters:
    param1 (type): Description.
    param2 (type): Description.

    Returns:
    type: Description.

    Raises:
    ValueError: When ...
    """
```

### Error Handling
- Raise specific exceptions (`ValueError`, `FileNotFoundError`).
- Catch specific exceptions, not broad `Exception`.
- CLI scripts print errors to stderr and `sys.exit(1)`.
- Library code raises; does not print.

### CLI Pattern
```python
def main():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("input", help="...")
    parser.add_argument("-o", "--output", help="...")
    args = parser.parse_args()
    # ...

if __name__ == "__main__":
    main()
```

### File I/O
- Always `with open(...) as f:`.
- Explicit `encoding="utf-8"`.
- JSON: `json.dump(data, f, indent=4)`.

### Public API
All public symbols are exported from `src/parse_avidemux_project/__init__.py`.

```python
from parse_avidemux_project import (
    AvidemuxProject,  # dataclass: video_file, segments, markers, codecs, audio_tracks
    Segment,          # dataclass: start, duration (+ .end property)
    AudioTrack,       # dataclass: index, language, codec
    parse_project,    # parse TinyPY string → AvidemuxProject
    parse_project_file,  # parse TinyPY file → AvidemuxProject
    us_to_iso_time,       # int → "HH:MM:SS.mmm"
)
```
