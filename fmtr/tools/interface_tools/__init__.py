from fmtr.tools.import_tools import MissingExtraMockModule

try:
    from fmtr.tools.interface_tools.interface_tools import Interface, update
    from fmtr.tools.interface_tools import controls
except ImportError as exception:
    Interface = update = controls = MissingExtraMockModule('interface', exception)
