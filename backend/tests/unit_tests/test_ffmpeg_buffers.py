import io
import os
import sys

import pytest


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class _DummyProc:
    def __init__(self):
        self.stdout = io.BytesIO(b"")
        self.stdin = io.BytesIO()
        self.returncode = 0

    def wait(self):
        return 0

    def terminate(self):
        return None


@pytest.fixture()
def ffmpeg_buffers_module():
    import src.FFmpegBuffers as ffmpeg_buffers

    return ffmpeg_buffers


def _mock_subprocess(*args, **kwargs):
    return _DummyProc()


def test_ffmpeg_read_command_for_png_sequence(ffmpeg_buffers_module, monkeypatch):
    monkeypatch.setattr(ffmpeg_buffers_module, "subprocess_popen_without_terminal", _mock_subprocess)
    reader = ffmpeg_buffers_module.FFmpegRead(
        inputFile="/tmp/frames/frame%04d.png",
        width=1920,
        height=1080,
        start_time=0,
        end_time=None,
        borderX=0,
        borderY=0,
        hdr_mode=False,
        ffmpeg_path="ffmpeg",
        input_is_png_sequence=True,
        input_png_sequence_start_number=10,
    )
    command = reader.command()
    assert "-start_number" in command
    assert "10" in command
    assert "/tmp/frames/frame%04d.png" in command


def test_ffmpeg_write_command_for_png_sequence_output(ffmpeg_buffers_module, monkeypatch):
    from src.utils.Encoders import EncoderSettings

    monkeypatch.setattr(ffmpeg_buffers_module, "subprocess_popen_without_terminal", _mock_subprocess)
    writer = ffmpeg_buffers_module.FFmpegWrite(
        inputFile="/tmp/in.mp4",
        outputFile="/tmp/out_%08d.png",
        width=1280,
        height=720,
        start_time=0,
        end_time=None,
        fps=24,
        crf="18",
        audio_bitrate="192k",
        pixelFormat="yuv420p",
        overwrite=True,
        custom_encoder=None,
        benchmark=False,
        slowmo_mode=False,
        upscaleTimes=2,
        interpolateFactor=1,
        ceilInterpolateFactor=1,
        video_encoder=EncoderSettings("libx264"),
        audio_encoder=EncoderSettings("copy_audio", type="audio"),
        subtitle_encoder=EncoderSettings("copy_subtitle", type="subtitle"),
        hdr_mode=False,
        mpv_output=False,
        merge_subtitles=False,
        ffmpeg_path="ffmpeg",
        ffmpeg_log_file="/tmp/ffmpeg-test-log.txt",
    )
    command = writer.command()
    assert "-f" in command
    assert "image2" in command
    assert "/tmp/out_%08d.png" in command
    assert "1:a?" not in command


def test_ffmpeg_write_command_downscale_to_original(ffmpeg_buffers_module, monkeypatch):
    from src.utils.Encoders import EncoderSettings

    monkeypatch.setattr(ffmpeg_buffers_module, "subprocess_popen_without_terminal", _mock_subprocess)
    writer = ffmpeg_buffers_module.FFmpegWrite(
        inputFile="/tmp/in.mp4",
        outputFile="/tmp/out.mkv",
        width=640,
        height=360,
        start_time=0,
        end_time=None,
        fps=24,
        crf="18",
        audio_bitrate="192k",
        pixelFormat="yuv420p",
        overwrite=True,
        custom_encoder=None,
        benchmark=False,
        slowmo_mode=False,
        upscaleTimes=2,
        interpolateFactor=1,
        ceilInterpolateFactor=1,
        video_encoder=EncoderSettings("libx264"),
        audio_encoder=EncoderSettings("copy_audio", type="audio"),
        subtitle_encoder=EncoderSettings("copy_subtitle", type="subtitle"),
        hdr_mode=False,
        mpv_output=False,
        merge_subtitles=False,
        ffmpeg_path="ffmpeg",
        ffmpeg_log_file="/tmp/ffmpeg-test-log-2.txt",
        ffmpeg_downscale_to_original=True,
    )
    command = writer.command()
    assert "-vf" in command
    assert "scale=640:360" in command
