from dataclasses import dataclass, field, asdict


@dataclass
class Segment:
    start: int
    duration: int

    @property
    def end(self) -> int:
        return self.start + self.duration


@dataclass
class AudioTrack:
    index: int
    language: str | None = None
    codec: str | None = None


@dataclass
class AvidemuxProject:
    video_file: str | None = None
    segments: list[Segment] = field(default_factory=list)
    marker_a: int | None = None
    marker_b: int | None = None
    video_codec: str | None = None
    container: str | None = None
    container_options: dict[str, str] = field(default_factory=dict)
    audio_tracks: list[AudioTrack] = field(default_factory=list)
    hdr_config: tuple[int, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "video_file": self.video_file,
            "segments": [asdict(s) | {"end": s.end} for s in self.segments],
            "marker_a": self.marker_a,
            "marker_b": self.marker_b,
            "video_codec": self.video_codec,
            "container": self.container,
            "container_options": self.container_options,
            "audio_tracks": [asdict(t) for t in self.audio_tracks],
            "hdr_config": list(self.hdr_config),
        }
