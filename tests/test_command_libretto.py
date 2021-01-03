import filecmp

from .fixture_data_directory import data_directory
from .fixture_invoke_command import invoke_command
from .fixture_mocked_static_server import mocked_static_server


def test_download(data_directory, invoke_command, mocked_static_server):
    """Test if the download mechanism works correctly."""
    for format in "raw", "binary", "json":
        output = data_directory / f"downloaded.{format}"
        sample = data_directory / f"libretto.{format}"
        result = invoke_command(
            f"--static-host={mocked_static_server.static_host}",
            "libretto",
            "download",
            f"--format={format}",
            output,
        )
        assert result.exit_code == 0
        assert not result.exception
        assert not result.output
        assert output.exists()
        assert filecmp.cmp(output, sample, shallow=False)


def test_convert(data_directory, invoke_command):
    """Test if the converted files conform to the expected samples."""
    for target in "binary", "json":
        for source in "raw", "binary", "json":
            input = data_directory / f"libretto.{source}"
            output = data_directory / f"{source}.to.{target}"
            sample = data_directory / f"libretto.{target}"
            result = invoke_command(
                "libretto",
                "convert",
                f"--format={target}",
                input,
                output,
            )
            assert result.exit_code == 0
            assert not result.exception
            assert not result.output
            assert output.exists()
            assert filecmp.cmp(output, sample, shallow=False)


def test_export(data_directory, invoke_command):
    """Test if the exported phonemes conform to the expected samples."""
    for file in "libretto.raw", "libretto.binary", "libretto.json":
        output = data_directory / f"{file}.generated.txt"
        sample = data_directory / "libretto.txt"
        result = invoke_command(
            "libretto",
            "export",
            data_directory / file,
            output,
        )
        assert result.exit_code == 0
        assert not result.exception
        assert not result.output
        assert output.exists()
        assert filecmp.cmp(output, sample, shallow=False)
