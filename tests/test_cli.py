from click.testing import CliRunner

from chronovault.cli import main


def test_cli_init_status_and_collections_list(tmp_path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["init", "--org", "org-cli", "--token", "root-secret", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        main,
        ["status", "--org", "org-cli", "--token", "root-secret", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        main,
        ["collections", "list", "--org", "org-cli", "--token", "root-secret", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0
