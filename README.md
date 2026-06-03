# parse-avidemux-project

Standalone Python library for parsing [Avidemux](https://avidemux.sourceforge.net/) TinyPY project scripts into structured data (video path, segments, filters, audio tracks, etc.). No ffmpeg, ccextractor, or Avidemux CLI required.

## Installation

```bash
pip install parse-avidemux-project
```

## CLI Usage

```bash
parse-avidemux-project input.py -o output.json
```

Omitting `-o` prints the JSON to stdout.

## Python API

```python
from parse_avidemux_project import (
    AvidemuxProject,
    Segment,
    AudioTrack,
    parse_project,
    parse_project_file,
    us_to_iso_time,
)

# Parse a file
project: AvidemuxProject = parse_project_file("project.py")

# Or parse a string
project = parse_project('''
    adm = Avidemux()
    if not adm.loadVideo("/path/to/video.mkv"):
        raise
    adm.addSegment(0, 1000000, 5000000)
    adm.markerA = 0
    adm.markerB = 6000000
''')

print(project.video_file)       # /path/to/video.mkv
print(project.segments)         # [Segment(start=1000000, duration=5000000)]
print(project.segments[0].end)  # 6000000 (computed property)

# Convert to dict for JSON serialization
print(project.to_dict())

# Microsecond to ISO time conversion
print(us_to_iso_time(3661000000))  # 01:01:01.000
```

### Data model

| Attribute | Type | Description |
|---|---|---|
| `video_file` | `str \| None` | Path to the source video |
| `segments` | `list[Segment]` | List of cut segments (each has `start`, `duration`, and `end` property) |
| `marker_a`, `marker_b` | `int \| None` | A/B markers in microseconds |
| `video_codec` | `str \| None` | Output video codec |
| `container` | `str \| None` | Output container format |
| `container_options` | `dict[str, str]` | Container options |
| `audio_tracks` | `list[AudioTrack]` | Audio track configs (each has `index`, `language`, `codec`) |
| `hdr_config` | `tuple[int, ...]` | HDR parameters |

## License

MIT
