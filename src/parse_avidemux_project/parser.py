import re

from .models import AudioTrack, AvidemuxProject, Segment


def parse_project(content: str) -> AvidemuxProject:
    """
    Parse an Avidemux TinyPY script into a structured AvidemuxProject object.

    Parameters:
    content (str): The full text of an Avidemux TinyPY project file.

    Returns:
    AvidemuxProject: Structured representation of the project.

    Raises:
    ValueError: If the content cannot be parsed as a valid Avidemux project.
    """
    video_files = _parse_video_files(content)
    segments = _parse_segments(content)

    if not video_files and not segments:
        raise ValueError("No Avidemux project data found in content")

    if segments and not video_files:
        raise ValueError("Segments require at least one video file (none found)")

    for i, seg in enumerate(segments):
        if seg.ref_video_idx < 0 or seg.ref_video_idx >= len(video_files):
            raise ValueError(
                f"Segment {i}: invalid ref_video_idx {seg.ref_video_idx} "
                f"(expected 0..{len(video_files) - 1})"
            )

    return AvidemuxProject(
        video_files=video_files,
        segments=segments,
        marker_a=_parse_marker(content, "A"),
        marker_b=_parse_marker(content, "B"),
        video_codec=_parse_video_codec(content),
        container=_parse_container(content),
        container_options=_parse_container_options(content),
        audio_tracks=_parse_audio_tracks(content),
        hdr_config=_parse_hdr_config(content),
    )


def parse_project_file(path: str) -> AvidemuxProject:
    """
    Read and parse an Avidemux TinyPY project file.

    Parameters:
    path (str): Filesystem path to a TinyPY project file.

    Returns:
    AvidemuxProject: Structured representation of the project.
    """
    with open(path, encoding="utf-8") as f:
        return parse_project(f.read())


def us_to_iso_time(us: int) -> str:
    """
    Convert microseconds to the format HH:MM:SS.mmm.

    Parameters:
    us (int): Microseconds to convert.

    Returns:
    str: Formatted time string.
    """
    ms = int(us) // 1000
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


_PATTERN_VIDEO = re.compile(
    r"adm = Avidemux\(\)\s*\n"
    r'if not adm\.loadVideo\("(.+?)"\):\s*raise'
)

_PATTERN_SEGMENT = re.compile(r"adm\.addSegment\((\d+), (\d+), (\d+)\)")

_PATTERN_APPEND_VIDEO = re.compile(
    r'if not adm\.appendVideo\("(.+?)"\):\s*raise'
)

_PATTERN_MARKER = re.compile(r"adm\.marker([AB])\s*=\s*(\d+)")

_PATTERN_VIDEO_CODEC = re.compile(r'adm\.videoCodec\("(.+?)"\)')

_PATTERN_CONTAINER = re.compile(r"adm\.setContainer\(([^)]+)\)")

_PATTERN_HDR_CONFIG = re.compile(r"adm\.setHDRConfig\(([^)]+)\)")

_PATTERN_SOURCE_LANG = re.compile(r'adm\.setSourceTrackLanguage\((\d+),"(.+?)"\)')

_PATTERN_AUDIO_ADD = re.compile(r"adm\.audioAddTrack\((\d+)\)")

_PATTERN_AUDIO_CODEC = re.compile(r'adm\.audioCodec\((\d+), "(.+?)"\)')


def _parse_video_files(content: str) -> list[str]:
    videos = []
    match = _PATTERN_VIDEO.search(content)
    if match:
        videos.append(match.group(1))
    videos.extend(_PATTERN_APPEND_VIDEO.findall(content))
    return videos


def _parse_segments(content: str) -> list[Segment]:
    matches = _PATTERN_SEGMENT.findall(content)
    return [
        Segment(ref_video_idx=int(ref), start=int(start), duration=int(duration))
        for ref, start, duration in matches
    ]


def _parse_marker(content: str, marker: str) -> int | None:
    for m, val in _PATTERN_MARKER.findall(content):
        if m == marker:
            return int(val)
    return None


def _parse_video_codec(content: str) -> str | None:
    match = _PATTERN_VIDEO_CODEC.search(content)
    return match.group(1) if match else None


def _parse_container(content: str) -> str | None:
    match = _PATTERN_CONTAINER.search(content)
    if not match:
        return None
    parts = re.findall(r'"([^"]*)"', match.group(1))
    return parts[0] if parts else None


def _parse_container_options(content: str) -> dict[str, str]:
    match = _PATTERN_CONTAINER.search(content)
    if not match:
        return {}
    parts = re.findall(r'"([^"]*)"', match.group(1))
    options = {}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            options[key] = value
    return options


def _parse_hdr_config(content: str) -> tuple[int, ...]:
    match = _PATTERN_HDR_CONFIG.search(content)
    if not match:
        return ()
    return tuple(int(x.strip()) for x in match.group(1).split(","))


def _parse_audio_tracks(content: str) -> list[AudioTrack]:
    source_languages = {
        int(index): lang
        for index, lang in _PATTERN_SOURCE_LANG.findall(content)
    }
    codecs = {
        int(index): codec
        for index, codec in _PATTERN_AUDIO_CODEC.findall(content)
    }
    track_indices = sorted({
        int(index)
        for index in _PATTERN_AUDIO_ADD.findall(content)
    }.union(codecs.keys()))

    tracks = []
    for idx in track_indices:
        tracks.append(AudioTrack(
            index=idx,
            language=source_languages.get(idx),
            codec=codecs.get(idx),
        ))
    return tracks
