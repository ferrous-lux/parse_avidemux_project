from pathlib import Path

import pytest

from parse_avidemux_project import (
    Segment,
    parse_segments_csv,
    parse_segments_csv_file,
)

FIXTURES = Path(__file__).parent / "fixtures"

CSV_SINGLE = (
    "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
    "0,0,/tmp/test.mkv,84752000,709025000\n"
)

CSV_MULTI = (
    "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
    "0,0,/tmp/test.mkv,84752000,709025000\n"
    "1,0,/tmp/test.mkv,1050751000,438955000\n"
    "2,0,/tmp/test.mkv,1780930000,422672000\n"
)

CSV_MULTI_VIDEO = (
    "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
    "0,0,/tmp/movie1.mkv,1000000,5000000\n"
    "1,1,/tmp/movie2.mkv,2000000,3000000\n"
)

CSV_NO_PATH = (
    "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
    "0,0,,1000000,5000000\n"
)

CSV_GAP_REFS = (
    "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
    "0,0,/tmp/a.mkv,1000000,5000000\n"
    "1,2,/tmp/c.mkv,2000000,3000000\n"
)


def test_parse_segments_csv_single_segment():
    project = parse_segments_csv(CSV_SINGLE)
    assert project.video_files == ["/tmp/test.mkv"]
    assert len(project.segments) == 1
    assert project.segments[0] == Segment(
        start=84752000, duration=709025000, ref_video_idx=0,
    )


def test_parse_segments_csv_multi_segment():
    project = parse_segments_csv(CSV_MULTI)
    assert project.video_files == ["/tmp/test.mkv"]
    assert len(project.segments) == 3
    assert project.segments[0] == Segment(
        start=84752000, duration=709025000, ref_video_idx=0,
    )
    assert project.segments[2] == Segment(
        start=1780930000, duration=422672000, ref_video_idx=0,
    )


def test_parse_segments_csv_multi_video():
    project = parse_segments_csv(CSV_MULTI_VIDEO)
    assert project.video_files == ["/tmp/movie1.mkv", "/tmp/movie2.mkv"]
    assert len(project.segments) == 2
    assert project.video_files[project.segments[0].ref_video_idx] == "/tmp/movie1.mkv"
    assert project.video_files[project.segments[1].ref_video_idx] == "/tmp/movie2.mkv"


def test_parse_segments_csv_no_path_errors():
    with pytest.raises(ValueError, match="Missing or empty video_path"):
        parse_segments_csv(CSV_NO_PATH)


def test_parse_segments_csv_gap_refs_errors():
    with pytest.raises(ValueError, match="Gap in ref_video_idx"):
        parse_segments_csv(CSV_GAP_REFS)


def test_parse_segments_csv_file():
    csv_path = FIXTURES / "test-segments.csv"
    csv_path.write_text(CSV_MULTI, encoding="utf-8")
    try:
        project = parse_segments_csv_file(str(csv_path))
        assert len(project.segments) == 3
        assert project.video_files == ["/tmp/test.mkv"]
    finally:
        csv_path.unlink()


def test_parse_segments_csv_empty():
    with pytest.raises(ValueError, match="CSV content is empty"):
        parse_segments_csv("")


def test_parse_segments_csv_no_data():
    with pytest.raises(ValueError, match="No segment data found"):
        parse_segments_csv("segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n")


def test_parse_segments_csv_missing_offset_errors():
    with pytest.raises(ValueError, match="Missing or empty CSV column: offset_pts"):
        parse_segments_csv(
            "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
            "0,0,/tmp/test.mkv,,709025000\n"
        )


def test_parse_segments_csv_bad_int():
    with pytest.raises(ValueError, match="Invalid integer in column.*offset_pts"):
        parse_segments_csv(
            "segment_idx,ref_video_idx,video_path,offset_pts,duration_pts\n"
            "0,0,/tmp/test.mkv,abc,709025000\n"
        )


def test_parse_segments_csv_file_append_4_files():
    project = parse_segments_csv_file(str(FIXTURES / "append_4_files.csv"))
    assert project.video_files == [
        "/tmp/adm_testing/1.mkv",
        "/tmp/adm_testing/2.mkv",
        "/tmp/adm_testing/3.mkv",
        "/tmp/adm_testing/4.mkv",
    ]
    assert len(project.segments) == 4
    assert project.segments[0] == Segment(
        start=67234, duration=10010000, ref_video_idx=0,
    )
    assert project.segments[3] == Segment(
        start=67234, duration=10010000, ref_video_idx=3,
    )


def test_segment_defaults():
    seg = Segment(start=1000, duration=2000)
    assert seg.ref_video_idx == 0


def test_segment_explicit():
    seg = Segment(start=1000, duration=2000, ref_video_idx=2)
    assert seg.ref_video_idx == 2
