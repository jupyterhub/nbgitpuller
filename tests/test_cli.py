import pytest
from click.testing import CliRunner
from gitautosync import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Hello, world.'


def test_cli_with_option(runner):
    result = runner.invoke(cli.main, ['--as-cowboy'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == 'Howdy, world.'


def test_cli_with_arg(runner):
    result = runner.invoke(cli.main, ['Peter'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Hello, Peter.'


def test_cli_with_option_and_arg(runner):
    result = runner.invoke(cli.main, ['--as-cowboy', 'Peter'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Howdy, Peter.'
