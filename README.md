# parse-avidemux-project

Standalone Python library for parsing [Avidemux](https://avidemux.sourceforge.net/) TinyPY project scripts into structured data (video files, segments, markers, audio tracks, filters, etc.). No ffmpeg, ccextractor, or Avidemux CLI required.

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
    AudioTrack,
    AvidemuxProject,
    Segment,
    parse_project,
    parse_project_file,
    parse_segments_csv,
    parse_segments_csv_file,
    us_to_iso_time,
)

# Parse a TinyPY project file
project: AvidemuxProject = parse_project_file("project.py")

# Or parse a TinyPY string
project = parse_project('''
    adm = Avidemux()
    if not adm.loadVideo("/path/to/video.mkv"):
        raise
    adm.addSegment(0, 1000000, 5000000)
    adm.markerA = 0
    adm.markerB = 6000000
''')

print(project.video_files)       # ['/path/to/video.mkv']
print(project.segments)          # [Segment(start=1000000, duration=5000000)]
print(project.segments[0].end)   # 6000000 (computed property)
print(project.video_files[project.segments[0].ref_video_idx])  # first video path

# Convert to dict for JSON serialization
print(project.to_dict())

# Microsecond to ISO time conversion
print(us_to_iso_time(3661000000))  # 01:01:01.000
```

### Parsing segment CSV exports

Avidemux can export segment data as CSV from its TinyPy console:

```python
# Parse a CSV string
project = parse_segments_csv(
    "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
    "0,0,/tmp/test.mkv,84752000,709025000\n"
)

# Or read from a CSV file
project = parse_segments_csv_file("segments.csv")
```

### Data model

#### `AvidemuxProject`

| Attribute | Type | Description |
|---|---|---|
| `video_files` | `list[str]` | All source videos (loadVideo + appendVideo order) |
| `segments` | `list[Segment]` | Cut segments |
| `marker_a`, `marker_b` | `int \| None` | A/B markers in microseconds |
| `video_codec` | `str \| None` | Output video codec |
| `container` | `str \| None` | Output container format |
| `container_options` | `dict[str, str]` | Container options |
| `audio_tracks` | `list[AudioTrack]` | Audio track configurations |
| `hdr_config` | `tuple[int, ...]` | HDR parameters |

#### `Segment`

| Attribute | Type | Description |
|---|---|---|
| `start` | `int` | Start offset in microseconds |
| `duration` | `int` | Duration in microseconds |
| `ref_video_idx` | `int` | Index into `video_files` (default `0`) |
| `.end` (property) | `int` | Computed: `start + duration` |

#### `AudioTrack`

| Attribute | Type | Description |
|---|---|---|
| `index` | `int` | Track index |
| `language` | `str \| None` | Language code (e.g. `"eng"`) |
| `codec` | `str \| None` | Audio codec (e.g. `"copy"`) |

## License

MIT
