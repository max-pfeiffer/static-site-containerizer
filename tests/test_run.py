"""Tests for running the image."""

import platform
from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner, Result
from python_on_whales import DockerClient
from requests import get
from testcontainers.registry import DockerRegistryContainer
from utils import get_platform

from static_site_containerizer import cli
from tests.constants import HTML_CONTENT, REGISTRY_PASSWORD, REGISTRY_USERNAME


def test_cli_run(
    registry_container: DockerRegistryContainer,
    cli_runner: CliRunner,
    docker_client: DockerClient,
) -> None:
    """Test running the docker image using CLI.

    :param registry_container:
    :param cli_runner:
    :return:
    """
    tag: str = f"{registry_container.get_registry()}/static-build:test"
    print(platform.uname())

    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        index_file = tmpdir_path / "index.html"
        with open(index_file, "w") as file:
            file.write(HTML_CONTENT)

        result: Result = cli_runner.invoke(
            cli,
            args=[
                "--content",
                tmpdir,
                "--registry",
                registry_container.get_registry(),
                "--registry-username",
                REGISTRY_USERNAME,
                "--registry-password",
                REGISTRY_PASSWORD,
                "--tag",
                tag,
                "--platform",
                get_platform(),
                "--push",
            ],
        )
        assert result.exit_code == 0

    with docker_client.run(tag, detach=True, publish=[(80, 80)]):
        response = get("http://localhost")
        assert response.status_code == 200
        assert response.text == HTML_CONTENT
