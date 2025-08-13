from fmtr.tools.import_tools import MissingExtraMockModule

try:
    from python_on_whales import docker as client
except ModuleNotFoundError as exception:
    client = MissingExtraMockModule('docker.client', exception)
