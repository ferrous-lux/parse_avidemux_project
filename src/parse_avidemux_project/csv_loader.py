import csv
import io

from .models import AvidemuxProject, Segment


def parse_segments_csv(content: str) -> AvidemuxProject:
    """
    Parse Avidemux segment CSV output into an AvidemuxProject.

    Parameters:
    content (str): CSV text exported from Avidemux's TinyPy shell.

    Returns:
    AvidemuxProject: Structured representation of the project.

    Raises:
    ValueError: If the CSV content is empty or the header is missing.
    """
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames is None:
        raise ValueError("CSV content is empty or missing header")

    segments = []
    ref_to_path: dict[int, str] = {}
    for row in reader:
        start = _parse_int(row, "offset_pts")
        duration = _parse_int(row, "duration_pts")
        ref_video_idx = _parse_int(row, "ref_video_idx")
        video_path = str(row.get("video_path", "")).strip()
        if not video_path:
            raise ValueError(f"Missing or empty video_path for segment with ref_video_idx={ref_video_idx}")
        if ref_video_idx not in ref_to_path:
            ref_to_path[ref_video_idx] = video_path
        segments.append(Segment(
            start=start,
            duration=duration,
            ref_video_idx=ref_video_idx,
        ))

    if not segments:
        raise ValueError("No segment data found in CSV content")

    max_ref = max(ref_to_path)
    video_files = [ref_to_path.get(i, "") for i in range(max_ref + 1)]
    for i, path in enumerate(video_files):
        if not path:
            raise ValueError(f"Gap in ref_video_idx: no video_path for ref {i}")

    return AvidemuxProject(video_files=video_files, segments=segments)


def parse_segments_csv_file(path: str) -> AvidemuxProject:
    """
    Read and parse an Avidemux segment CSV file.

    Parameters:
    path (str): Filesystem path to a segment CSV file.

    Returns:
    AvidemuxProject: Structured representation of the project.
    """
    with open(path, encoding="utf-8") as f:
        return parse_segments_csv(f.read())


def _parse_int(row: dict[str, str], key: str) -> int:
    val = row.get(key, "").strip()
    if not val:
        raise ValueError(f"Missing or empty CSV column: {key}")
    try:
        return int(val)
    except ValueError:
        raise ValueError(f"Invalid integer in column '{key}': {val!r}")
