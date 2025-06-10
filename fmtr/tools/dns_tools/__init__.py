from fmtr.tools.import_tools import MissingExtraMockModule

try:
    from fmtr.tools.dns_tools import server, client, dm, proxy
except ImportError as exception:
    server = client = dm = proxy = MissingExtraMockModule('dns', exception)
