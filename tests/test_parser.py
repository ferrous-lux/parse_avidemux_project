from pathlib import Path

import pytest

from parse_avidemux_project import (
    AudioTrack,
    AvidemuxProject,
    Segment,
    parse_project,
    parse_project_file,
    us_to_iso_time,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_project_file_adm1():
    project = parse_project_file(str(FIXTURES / "test-adm.py"))
    assert project.video_file == "/tmp/test.mkv"
    assert len(project.segments) == 5
    assert project.marker_a == 0
    assert project.marker_b == 2597779000
    assert project.video_codec == "Copy"
    assert project.container == "MKV"
    assert len(project.container_options) == 8
    assert project.container_options["forceAspectRatio"] == "False"
    assert project.container_options["displayWidth"] == "1280"
    assert project.container_options["colMatrixCoeff"] == "2"
    assert len(project.audio_tracks) == 2
    assert project.audio_tracks[0] == AudioTrack(index=0, language="eng", codec="copy")
    assert project.audio_tracks[1] == AudioTrack(index=1, language="spa", codec="copy")
    assert project.hdr_config == (1, 1, 1, 1, 0)


def test_parse_project_file_adm2():
    project = parse_project_file(str(FIXTURES / "test2-adm.py"))
    assert project.video_file == "/tmp/test-video2.mkv"
    assert len(project.segments) == 10
    assert project.marker_a == 0
    assert project.marker_b == 4905816000
    assert project.video_codec == "Copy"
    assert project.container == "MKV"
    assert len(project.container_options) == 8
    assert len(project.audio_tracks) == 2
    assert project.audio_tracks[0] == AudioTrack(index=0, language="eng", codec="copy")
    assert project.audio_tracks[1] == AudioTrack(index=1, language="spa", codec="copy")
    assert project.hdr_config == (1, 1, 1, 1, 0)


def test_segment_end():
    seg = Segment(start=1000000, duration=5000000)
    assert seg.end == 6000000
    assert seg.start == 1000000
    assert seg.duration == 5000000


def test_segment_zero_duration():
    seg = Segment(start=5000, duration=0)
    assert seg.end == 5000


def test_parse_project_invalid_content():
    with pytest.raises(ValueError, match="No Avidemux project data found"):
        parse_project("not an avidemux file")


def test_parse_project_empty_string():
    with pytest.raises(ValueError, match="No Avidemux project data found"):
        parse_project("")


def test_parse_project_just_segments():
    project = parse_project("adm.addSegment(0, 1000, 2000)")
    assert project.video_file is None
    assert len(project.segments) == 1
    assert project.segments[0] == Segment(start=1000, duration=2000)


def test_parse_project_just_video():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
    )
    project = parse_project(content)
    assert project.video_file == "/path/to/video.mkv"
    assert len(project.segments) == 0


def test_parse_project_no_segments():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
        "adm.markerA = 0\n"
    )
    project = parse_project(content)
    assert project.video_file == "/path/to/video.mkv"
    assert len(project.segments) == 0
    assert project.marker_a == 0


def test_parse_project_no_video():
    project = parse_project("adm.addSegment(0, 1000, 2000)\nadm.addSegment(0, 5000, 3000)")
    assert project.video_file is None
    assert len(project.segments) == 2


def test_parse_project_no_hdr():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
    )
    project = parse_project(content)
    assert project.hdr_config == ()


def test_parse_project_no_container():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
    )
    project = parse_project(content)
    assert project.container is None
    assert project.container_options == {}


def test_parse_project_no_audio():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
    )
    project = parse_project(content)
    assert project.audio_tracks == []


def test_parse_project_no_codec():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
    )
    project = parse_project(content)
    assert project.video_codec is None


def test_parse_project_no_markers():
    content = (
        "adm = Avidemux()\n"
        'if not adm.loadVideo("/path/to/video.mkv"):\n'
        "    raise\n"
    )
    project = parse_project(content)
    assert project.marker_a is None
    assert project.marker_b is None


def test_us_to_iso_time_zero():
    assert us_to_iso_time(0) == "00:00:00.000"


def test_us_to_iso_time_one_second():
    assert us_to_iso_time(1_000_000) == "00:00:01.000"


def test_us_to_iso_time_one_minute():
    assert us_to_iso_time(60_000_000) == "00:01:00.000"


def test_us_to_iso_time_one_hour():
    assert us_to_iso_time(3_600_000_000) == "01:00:00.000"


def test_us_to_iso_time_milliseconds():
    assert us_to_iso_time(1_500_000) == "00:00:01.500"


def test_us_to_iso_time_complex():
    assert us_to_iso_time(9_999_999_999) == "02:46:39.999"


def test_to_dict_shape():
    project = AvidemuxProject(
        video_file="/path/to/video.mkv",
        segments=[Segment(start=1000, duration=2000)],
        marker_a=0,
        marker_b=5000,
        video_codec="Copy",
        container="MKV",
        container_options={"forceAspectRatio": "False"},
        audio_tracks=[AudioTrack(index=0, language="eng", codec="copy")],
        hdr_config=(1, 1, 1, 1, 0),
    )
    d = project.to_dict()
    assert d["video_file"] == "/path/to/video.mkv"
    assert d["segments"] == [{"start": 1000, "duration": 2000, "end": 3000}]
    assert d["marker_a"] == 0
    assert d["marker_b"] == 5000
    assert d["video_codec"] == "Copy"
    assert d["container"] == "MKV"
    assert d["container_options"] == {"forceAspectRatio": "False"}
    assert d["audio_tracks"] == [{"index": 0, "language": "eng", "codec": "copy"}]
    assert d["hdr_config"] == [1, 1, 1, 1, 0]


def test_to_dict_empty_project():
    d = AvidemuxProject().to_dict()
    assert d["video_file"] is None
    assert d["segments"] == []
    assert d["marker_a"] is None
    assert d["marker_b"] is None
    assert d["video_codec"] is None
    assert d["container"] is None
    assert d["container_options"] == {}
    assert d["audio_tracks"] == []
    assert d["hdr_config"] == []


def test_audio_track_equality():
    t1 = AudioTrack(index=0, language="eng", codec="copy")
    t2 = AudioTrack(index=0, language="eng", codec="copy")
    assert t1 == t2


def test_segment_equality():
    s1 = Segment(start=1000, duration=2000)
    s2 = Segment(start=1000, duration=2000)
    assert s1 == s2
