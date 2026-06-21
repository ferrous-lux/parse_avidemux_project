# Changelog

## 0.2.0 (2026-06-21)

### Breaking changes

- **`Segment.video_path` removed** — use `project.video_files[segment.ref_video_idx]` instead
- **`AvidemuxProject.video_file` (singular) removed** — replaced by `video_files: list[str]`
- **`AvidemuxProject.additional_videos` removed** — merged into `video_files`
- **Segments now require at least one video file** — `parse_project()` raises `ValueError` if any segment exists without a `loadVideo`/`appendVideo` call
- **`ref_video_idx` validation** — `parse_project()` raises `ValueError` if a segment's `ref_video_idx` is out of bounds
- **CSV `video_path` column is required** — `parse_segments_csv()` raises `ValueError` if empty or missing
- **CSV gap detection** — `parse_segments_csv()` raises `ValueError` if ref indices have gaps (e.g., refs 0 and 2 without 1)

### Features

- **Multi-video project support** — `AvidemuxProject.video_files` captures all `loadVideo` + `appendVideo` calls in order
- **Segment `ref_video_idx`** — captures the video reference index from `adm.addSegment(ref, ...)` instead of hardcoding 0
- **`parse_segments_csv()` / `parse_segments_csv_file()`** — new public API to parse Avidemux CSV segment exports into `AvidemuxProject`
- **CSV→Project bridge** — CSV input rebuilds `video_files` by collecting unique paths ordered by `ref_video_idx`
- **Bounds-safe path resolution** — `project.video_files[seg.ref_video_idx]` always returns the correct video path

### Internal

- `csv_loader.py` — new module for CSV parsing
- `parser.py` — `_parse_video_files()` collects all video paths; strict `ref_video_idx` bounds checking
- `models.py` — simplified `Segment` (start, duration, ref_video_idx only); `AvidemuxProject.video_files`
- CLI — JSON output now uses `video_files` array, no per-segment `video_path`

## 0.1.0 (2026-06-18)

- Initial release
- Parse Avidemux TinyPY project files into structured data
- `AvidemuxProject` with `video_file`, `segments`, `markers`, `codecs`, `container`, `audio_tracks`, `hdr_config`
- `Segment` with `start`, `duration`, and `.end` property
- `parse_project()`, `parse_project_file()`, `us_to_iso_time()`
- CLI tool `parse-avidemux-project`
