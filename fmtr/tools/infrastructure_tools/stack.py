from functools import cached_property

from fmtr.tools import Path, merge, logger
from fmtr.tools.docker_tools import DockerClient
from fmtr.tools.infrastructure_tools.project import Project
from fmtr.tools.inherit_tools import Inherit
from fmtr.tools.iterator_tools import IndexList


class Stack(Inherit[Project]):
    """
    
    Represents the Docker stack for a project. Manages different deployment targets including:

    - Development compose stack with docker-compose configuration
    - Build targets for dev and production environments

    """

    CHANNEL = None

    @cached_property
    def path_compose(self):
        return Path.temp() / f'{self.name}.yml'

    @cached_property
    def client(self):
        return DockerClient(host=f"ssh://{self.hostname}", compose_files=self.path_compose)

    @classmethod
    def get_all(self):
        return [Dev]


class Dev(Stack):
    """

    Represents the development environment stack with channel-specific configuration

    """

    CHANNEL = 'dev'

    @cached_property
    def composes_all(self):
        return IndexList[Compose](cls(self) for cls in (Compose, ComposeDocumentDatabase,))

    @cached_property
    def compose_data(self):
        """

        Merge Compose data for all project services

        """
        data = []
        for service in [Compose.NAME] + self.services:
            compose = self.composes_all.NAME[service]
            data.append(compose.data)
        data = merge(*data)
        return data

    def build(self):
        """

        Builds a Docker image using the specified build arguments, tags, and contexts.

        """

        build_args = dict(
            ORG=self.org,
            PACKAGE=self.package,
            BASE=self.base,
            EXTRAS=self.extras_str,
            ENTRYPOINT=f"{self.org}-{self.package}-{self.entrypoint}",
        )

        tags = [
            f'{self.org}.{self.package}:{self.CHANNEL}-{self.extras_str}',
            f'{self.org}.{self.package}:{self.CHANNEL}-{self.extras_str}-{self.repo.data.current}'
        ]

        contexts = dict(
            package=str(self.paths.repo)
        )

        self.client.build(
            build_contexts=contexts,
            file='Dockerfile',
            context_path=self.paths.repo,
            build_args=build_args,
            tags=tags,
            target=self.CHANNEL,
            load=True,

        )

    def recreate(self):
        """
        Recreates a compose deployment

        """
        data = self.compose_data

        with logger.span(f'Writing compose file to "{self.path_compose}"'):
            self.path_compose.write_yaml(data)
        # project_name = f"{self.org}-{self.package}"

        self.client.compose.up(
            detach=True,
            force_recreate=True,
            # project_name=project_name,
        )


class Compose(Inherit[Stack]):
    """

    Compose file representation

    """
    NAME = 'base'

    @property
    def data(self):
        data = dict(
            name=f"{self.name_dash}",
            services=dict(
                interpreter=dict(
                    image=f"{self.name}:dev-{self.extras_str}",
                    restart="unless-stopped",
                    container_name=f"{self.name}",
                    hostname=f"{self.name_dash}-{self.CHANNEL}",
                    env_file=[
                        "/opt/dev/repo/env",
                    ],
                    environment=dict(
                        # DISPLAY=f"{self.display}",
                    ),
                    volumes=[
                        "dev:/opt/dev/repo",
                        "ssh:/home/user/.ssh",
                        "/opt/dev/data:/opt/dev/data",
                        "/home/user/.Xauthority:/home/user/.Xauthority:ro",
                        "/tmp/.X11-unix:/tmp/.X11-unix",
                    ],
                    ports=[
                        f"{2200 + self.port}:22",
                        f"{8000 + self.port}:8080",
                        f"{8100 + self.port}:8180",
                    ],
                    user="1000:1000",
                ),
            ),
            secrets=dict(
                hf_token=dict(
                    environment="HF_TOKEN",
                ),
            ),
            volumes=dict(
                dev=dict(
                    name=f"{self.name}",
                ),
                ssh=dict(
                    name="ssh",
                    external=True,
                ),
            ),
        )
        return data


class ComposeDocumentDatabase(Compose):
    """

    Compose file representation for document database service

    """
    NAME = 'db.document'

    @property
    def data(self):
        data = dict(
            # todo
        )
        return data
