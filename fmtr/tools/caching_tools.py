from diskcache import Cache

from fmtr.tools import logger, Path


class Dump(dict):
    """

    Subclass `dict` to distinguish between dumped sub-caches and regular dictionaries.

    """

class Disk(Cache):
    """

    Subclass of `diskcache` Cache that implements nested/structured caches

    """

    ROOT_KEY = '__root__'

    def __init__(self, path=None, is_root=True, **settings):
        """

        Read in existing cache structure from filesystem.

        """

        path = Path(path)
        if is_root:
            if not path.parent.exists():
                raise FileNotFoundError(f"Directory {path.parent=} does not exist")
            if path and not path.exists():
                logger.warning(f'Cache does not exist. Will be created. "{path=}"...')

            logger.info(f'Initializing Disk Cache at path "{path=}"...')

        super().__init__(directory=str(path / self.ROOT_KEY), **settings)

        self.path = path
        self.children = {}

        for path_dir in self.path.iterdir():
            if path_dir.stem == self.ROOT_KEY:
                continue
            if path_dir.is_dir():
                self.create(path_dir.name)

    def create(self, key):
        if key in self.children:
            raise KeyError(f'Sub-cache for key "{key}" already exists')
        if key in self:
            raise KeyError(f'Data for key "{key}" already exists: {repr(self[key])}')

        self.children[key] = self.__class__(self.path / key, is_root=False)

    def __getitem__(self, key):
        if key in self.children:
            return self.children[key]
        else:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        if value is type(self):
            self.create(key)
        else:
            super().__setitem__(key, value)

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return self[key]

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.path}")'

    def items(self):
        for key in self:
            yield key, self[key]

    def dump(self):
        data = Dump(self.items())
        for key, child in self.children.items():
            data[key] = child.dump()
        return data

    def iterkeys(self):
        yield from self.children.keys()
        yield from super().iterkeys()

    @property
    def data(self):
        return self.dump()


if __name__ == '__main__':
    path_tmp_cache = Path.cwd().parent.parent / 'data' / 'cache'
    tc = Disk(path_tmp_cache)

    tc.setdefault('c', Disk).setdefault('c1', Disk)['subkey'] = 0000.1
    # tc['c']=Disk.Create
    tc['c']['test'] = False
    tc['val'] = 123
    tc.setdefault('b', Disk)
    tc.setdefault('a', Disk)
    tc['a']['value2'] = 456
    tc['a']['value4'] = dict(mykey='myvalue')

    tc['b']['value3'] = [789, True]
    tc.dump()
    {}.items()
