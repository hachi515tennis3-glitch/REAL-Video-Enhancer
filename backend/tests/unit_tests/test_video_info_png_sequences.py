import os
import sys
import types
from pathlib import Path


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def _import_video_info_module(monkeypatch):
    sys.modules.pop("src.utils.VideoInfo", None)
    monkeypatch.setitem(sys.modules, "cv2", types.SimpleNamespace())
    from src.utils import VideoInfo as video_info_module

    return video_info_module


def test_count_png_sequence_frames_supports_unicode_prefix_and_zero_start(tmp_path, monkeypatch):
    video_info_module = _import_video_info_module(monkeypatch)

    for frame_number in range(3):
        Path(tmp_path, f"ライアー_{frame_number:05d}.png").touch()

    video_info = video_info_module.OpenCVInfo.__new__(video_info_module.OpenCVInfo)
    video_info.input_file = str(tmp_path / "ライアー_%05d.png")
    video_info.cap = None

    assert video_info._count_png_sequence_frames() == 3


def test_count_png_sequence_frames_supports_ascii_prefix_and_six_digits(tmp_path, monkeypatch):
    video_info_module = _import_video_info_module(monkeypatch)

    for frame_number in range(4):
        Path(tmp_path, f"frame_{frame_number:06d}.png").touch()

    video_info = video_info_module.OpenCVInfo.__new__(video_info_module.OpenCVInfo)
    video_info.input_file = str(tmp_path / "frame_%06d.png")
    video_info.cap = None

    assert video_info._count_png_sequence_frames() == 4


def test_ffmpeg_info_command_uses_png_sequence_start_number(monkeypatch):
    video_info_module = _import_video_info_module(monkeypatch)

    captured = {}

    class DummyProc:
        def __init__(self):
            self.stderr = type("DummyStderr", (), {"read": lambda self: ""})()

    def mock_subprocess(command, **kwargs):
        captured["command"] = command
        return DummyProc()

    monkeypatch.setattr(video_info_module, "subprocess_popen_without_terminal", mock_subprocess)

    video_info_module.FFMpegInfoWrapper(
        "/tmp/frame_%06d.png",
        ffmpeg_path="ffmpeg",
        input_is_png_sequence=True,
        input_png_sequence_start_number=0,
    )

    assert captured["command"][:8] == [
        "ffmpeg",
        "-f",
        "image2",
        "-framerate",
        "25",
        "-start_number",
        "0",
        "-i",
    ]


def test_ffmpeg_info_returns_zero_resolution_when_stream_is_missing(monkeypatch):
    video_info_module = _import_video_info_module(monkeypatch)

    wrapper = video_info_module.FFMpegInfoWrapper.__new__(video_info_module.FFMpegInfoWrapper)
    wrapper.ffmpeg_output_stripped = "no video stream found"

    assert wrapper.get_width_x_height() == [0, 0]
