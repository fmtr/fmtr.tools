try:
    from faker import Faker
    import sre_yield
except ImportError as exception:  # pragma: no cover
    from fmtr.tools.tools import raise_missing_extra

    raise_missing_extra('augmentation', exception)

fake = Faker()
to_generator = sre_yield.AllStrings
