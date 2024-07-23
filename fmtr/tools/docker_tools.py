import contextlib
import docker


@contextlib.contextmanager
def Container(image, ports=None, name=None, **kwargs):
    """

    Run a Docker container in a context manager

    """
    client = docker.from_env()

    try:
        container = client.containers.get(name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass

    ports = {f'{port}/tcp': port for port in ports}
    container = client.containers.run(image, ports=ports, detach=True, name=name, **kwargs)

    try:
        yield container
    finally:
        container.stop()
        container.remove()


