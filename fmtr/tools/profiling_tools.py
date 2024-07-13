try:
    from contexttimer import Timer
except ImportError as exception:  # pragma: no cover
    from fmtr.tools.tools import raise_missing_extra

    raise_missing_extra('profiling', exception)

Timer = Timer
