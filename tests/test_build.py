"""Tests for building the image."""

import platform
from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner, Result
from furl import furl
from requests import Response, get
from requests.auth import HTTPBasicAuth
from testcontainers.registry import DockerRegistryContainer

from static_site_containerizer import cli
from tests.constants import HTML_CONTENT, REGISTRY_PASSWORD, REGISTRY_USERNAME

BASIC_AUTH: HTTPBasicAuth = HTTPBasicAuth(REGISTRY_USERNAME, REGISTRY_PASSWORD)


def test_cli_build(
    registry_container: DockerRegistryContainer, cli_runner: CliRunner
) -> None:
    """Test building the docker image using CLI.

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
                f"linux/{platform.machine().lower()}",
            ],
        )
        assert result.exit_code == 0

        furl_item: furl = furl(f"http://{registry_container.get_registry()}")
        furl_item.path /= "v2/_catalog"

        response: Response = get(furl_item.url, auth=BASIC_AUTH)

        assert response.status_code == 200
        assert response.json() == {"repositories": ["static-build"]}

        furl_item: furl = furl(f"http://{registry_container.get_registry()}")
        furl_item.path /= "v2/static-build/tags/list"

        response: Response = get(furl_item.url, auth=BASIC_AUTH)

        assert response.status_code == 200

        response_image_tags: list[str] = response.json()["tags"]

        assert "test" in response_image_tags
