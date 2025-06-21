from fmtr.tools.import_tools import MissingExtraMockModule

try:
    from fmtr.tools.dns_tools import server, client, dm, proxy
    import dns
except ImportError as exception:
    dns = server = client = dm = proxy = MissingExtraMockModule('dns', exception)
