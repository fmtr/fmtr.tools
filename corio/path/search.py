from __future__ import annotations

from collections import defaultdict

import typing
from dataclasses import dataclass
from functools import cached_property
from ripgrep_rs import SearchMatch, files, search_structured

from corio.iterator import ilist

if typing.TYPE_CHECKING:
    from corio.path.path import Path


@dataclass(frozen=True)
class SearchResult:
    """

    Matches found in one file.

    """

    path: Path
    matches: tuple[SearchMatch, ...]


@dataclass(frozen=True)
class Searchers:
    """

    Search operations scoped to a path.

    """

    path: Path

    @cached_property
    def files(self):
        """

        Return the file searcher for this path.

        """
        return Files(self.path)

    @cached_property
    def contents(self):
        """

        Return the content searcher for this path.

        """
        return Contents(self.path)


@dataclass(frozen=True)
class Searcher:
    """

    Base class for a path-scoped search operation.

    """

    path: Path


class Files(Searcher):
    """

    Search for files under the configured path.

    """

    def __call__(self, *args, **kwargs) -> ilist[Path]:
        """

        Return paths matching the supplied file-search options.

        """
        options = dict(paths=[str(self.path)]) | kwargs
        paths = files(*args, **options)
        return ilist(type(self.path)(path) for path in paths)


class Contents(Searcher):
    """

    Search file contents under the configured path.

    """

    def __call__(self, *args, **kwargs) -> ilist[SearchResult]:
        """

        Return structured matches grouped by file path.

        """
        options = dict(paths=[str(self.path)]) | kwargs
        matches = search_structured(*args, **options)
        grouped = defaultdict(list)
        for match in matches:
            grouped[type(self.path)(match.path)].append(match)

        return ilist(
            SearchResult(path, tuple(path_matches))
            for path, path_matches in grouped.items()
        )
