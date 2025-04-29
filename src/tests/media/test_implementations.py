"""Tests for implementations."""

from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

from media.implementations import FfmpegPreparing


@mock.patch("media.implementations.ffmpeg")
def test_ffmpeg_implementation(mock_ffmpeg: MagicMock) -> None:
    """Test for ffmpeg implementation algo."""
    mock_stream = mock_ffmpeg.input.return_value
    mock_stream2 = mock_stream.afftdn.return_value
    mock_stream3 = mock_stream2.loudnorm.return_value
    mock_stream3.output.return_value = None

    test_file = Path("/fake/input/file.mp3")
    preparer = FfmpegPreparing()

    with preparer.get_stream_from_file(test_file) as temp_path:
        assert temp_path.suffix == ".wav"
        assert temp_path.exists()
        mock_ffmpeg.input.assert_called_with(test_file)
        mock_stream.afftdn.assert_called()
        mock_stream2.loudnorm.assert_called_with(I=-16, LRA=5, TP=0)
        mock_stream3.output.assert_called()

    assert not temp_path.exists()
