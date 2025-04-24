def cache_hfh():
    from fmtr import tools
    tools.hfh.main()


def remote_debug_test():
    """

    Test debugger connection

    """
    from fmtr.tools import debug
    debug.trace(is_debug=True)
