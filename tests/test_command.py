from .fixture_invoke_command import invoke_command

def test_command_help(invoke_command):
    """Test if the command help works correctly."""
    result = invoke_command("--help")
    assert "Usage:" in result.output
    assert result.exit_code == 0


def test_command_invalid(invoke_command):
    """Test the help menu when entering an invalid command."""
    result = invoke_command("invalid")
    assert "No such command" in result.output
    assert result.exit_code == 2
