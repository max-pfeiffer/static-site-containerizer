"""Test fixtures for image build tests."""

from collections.abc import Generator
from typing import Any

import pytest
from click.testing import CliRunner
from python_on_whales import DockerClient
from testcontainers.registry import DockerRegistryContainer

from tests.constants import REGISTRY_PASSWORD, REGISTRY_USERNAME


@pytest.fixture(scope="function")
def registry_container() -> Generator[DockerRegistryContainer, Any, None]:
    """Provide a Registry container locally for publishing the image.

    :return:
    """
    with DockerRegistryContainer(
        username=REGISTRY_USERNAME, password=REGISTRY_PASSWORD
    ).with_bind_ports(5000, 5000) as registry_container:
        yield registry_container


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    """Provide CLI runner for testing click CLI.

    :return:
    """
    runner = CliRunner()
    return runner


@pytest.fixture(scope="function")
def docker_client(
    registry_container: DockerRegistryContainer,
) -> Generator[DockerClient, Any, None]:
    """Provide a DockerClient.

    :param registry_container:
    :return:
    """
    docker_client: DockerClient = DockerClient()

    docker_client.login(
        server=registry_container.get_registry(),
        username=REGISTRY_USERNAME,
        password=REGISTRY_PASSWORD,
    )
    yield docker_client
