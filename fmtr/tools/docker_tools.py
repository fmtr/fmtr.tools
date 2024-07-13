import contextlib

try:
    import docker
except ImportError as exception:  # pragma: no cover
    from fmtr.tools.tools import raise_missing_extra

    raise_missing_extra('docker', exception)


@contextlib.contextmanager
def Container(image='', ports=None, name=None, **kwargs):
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


if __name__ == '__main__':
    with Container('yeasy/simple-web:latest', ports=[80], name='ws') as container:
        container.logs()
