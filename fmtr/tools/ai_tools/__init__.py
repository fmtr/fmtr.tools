from fmtr.tools.import_tools import MissingExtraMockModule

try:
    from fmtr.tools.ai_tools import inference_tools as infer
except ImportError as exception:
    infer = MissingExtraMockModule('infer', exception)

try:
    from fmtr.tools.ai_tools import agentic_tools as agentic
except ImportError as exception:
    agentic = MissingExtraMockModule('agentic', exception)
