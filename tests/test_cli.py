import pytest
from click.testing import CliRunner
from gitautosync import cli


ALREADY_PULLED_IN_TEXT = "Repo name [data8assets]: \n\
Account name [data-8]: \n\
Branch name [gh-pages]: \n\
Config file name [/.gitautosync/config.json]: \n\
Starting pull.\n\
    Domain: github.com\n\
    Repo: data8assets\n\
    Branch: gh-pages\n\
Starting pull from origin\n\
Pulled from origin\n\
Pulled from repo: data8assets"


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
    actual = result.output.strip()
    expected = ALREADY_PULLED_IN_TEXT
    print("Actual:")
    print(actual)
    print("")
    print("Expectd:")
    print(expected)
    assert actual == expected
