import filecmp


from .fixture_data_directory import data_directory
from .fixture_invoke_command import invoke_command
from .fixture_mocked_backend import mocked_backend


def test_upload_download(data_directory, invoke_command, mocked_backend):
    """Test if the upload and download mechanisms work correctly."""
    for format in "raw", "binary", "json":
        input = data_directory / f"recording.{format}"
        output = data_directory / f"recording.output.{format}"
        upload_result = invoke_command(
            f"--private-host={mocked_backend.private_host}",
            f"--public-host={mocked_backend.public_host}",
            "recording",
            "upload",
            "--handle=short",
            input,
        )
        assert upload_result.exit_code == 0
        assert not upload_result.exception
        assert upload_result.output.startswith("https://")
        download_result = invoke_command(
            f"--shortener-host={mocked_backend.shortener_host}",
            f"--private-host={mocked_backend.private_host}",
            f"--public-host={mocked_backend.public_host}",
            "recording",
            "download",
            f"--format={format}",
            upload_result.output.strip(),
            output,
        )
        assert download_result.exit_code == 0
        assert not download_result.exception
        assert not download_result.output
        assert output.exists()
        assert filecmp.cmp(output, input, shallow=False)


def test_export(data_directory, invoke_command):
    """Test if the export mechanism works correctly."""
    for format in "raw", "binary", "json":
        input = data_directory / f"recording.{format}"
        output = data_directory / f"recording.{format}.musicxml"
        data_directory / "recording.musicxml"
        result = invoke_command("recording", "export", input, output)
        assert result.exit_code == 0
        assert not result.exception
        assert not result.output
        # FIXME: can't compare because of non-deterministic identifiers
        assert output.exists()


def test_import(data_directory, invoke_command):
    """Test if the import mechanism works correctly."""
    for format in "raw", "binary", "json":
        input = data_directory / "recording.musicxml"
        output = data_directory / f"recording.output.{format}"
        data_directory / "recording.binary"
        result = invoke_command(
            "recording", "import", "--format=binary", input, output
        )
        assert result.exit_code == 0
        assert not result.exception
        assert not result.output
        # FIXME: can't compare because of lossy conversion
        assert output.exists()


def test_convert(data_directory, invoke_command):
    """Test if the converted files conform to the expected samples."""
    for target in "binary", "json":
        for source in "raw", "binary", "json":
            input = data_directory / f"recording.{source}"
            output = data_directory / f"{source}.to.{target}"
            sample = data_directory / f"recording.{target}"
            result = invoke_command(
                "recording",
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
