def combine_args_kwargs(args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    args = {i: arg for i, arg in enumerate(args)}
    args.update(kwargs)
    if all(isinstance(key, int) for key in args.keys()):
        args = list(args.values())
    return args


def split_args_kwargs(args_kwargs):
    if isinstance(args_kwargs, list):
        args, kwargs = args_kwargs, {}
    else:
        args = [arg for key, arg in args_kwargs.items() if isinstance(key, int)]
        kwargs = {key: arg for key, arg in args_kwargs.items() if not isinstance(key, int)}

    return args, kwargs


