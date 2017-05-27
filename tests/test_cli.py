import pytest
from click.testing import CliRunner
from gitautosync import cli


ALREADY_PULLED_IN_TEXT = "Repo name [data8assets]: \n\
Branch name [gh-pages]: \n\
Paths [['README.md']]: \n\
Config file name [/.gitautosync/config.json]: \n\
Starting pull.\n\
    User: jovyan\n\
    Domain: github.com\n\
    Account: data-8\n\
    Repo: data8assets\n\
    Branch: gh-pages\n\
    Paths: ['README.md']\n\
Existing pulls in .autopull_list: ['data8assets,github.com,data-8,gh-pages']\n\
Existing paths in sparse-checkout: ['.gitignore', 'README.md']\n\
[] written to sparse-checkout\n\
Starting pull from origin\n\
Pulled from origin\n\
We're in development so we won't chown the dir.\n\
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
