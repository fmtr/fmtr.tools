import regex as re
from dataclasses import dataclass, asdict
from functools import cached_property
from typing import List, Any

from fmtr.tools.logging_tools import logger
from fmtr.tools.string_tools import join


class RewriteCircularLoopError(Exception):
    """

    Circular loop error

    """


MASK_GROUP = '(?:{pattern})'
MASK_NAMED = r"(?P<{key}>{pattern})"


def alt(*patterns):
    patterns = sorted(patterns, key=len, reverse=True)
    pattern = '|'.join(patterns)
    pattern = MASK_GROUP.format(pattern=pattern)
    return pattern






@dataclass
class Key:
    RECORD_SEP = '␞'

    def flatten(self, data):
        """

        Flatten/serialise dictionary data

        """
        pairs = [f'{value}' for key, value in data.items()]
        string = self.RECORD_SEP.join(pairs)
        return string

    @cached_property
    def pattern(self):
        """

        Serialise to pattern

        """
        data = {key: MASK_NAMED.format(key=key, pattern=value) for key, value in asdict(self).items()}
        pattern = self.flatten(data)
        return pattern

    @cached_property
    def rx(self):
        """

        Compile to Regular Expression

        """
        return re.compile(self.pattern)

    @cached_property
    def string(self):
        """

        Serialise to string

        """
        string = self.flatten(asdict(self))
        return string

    def transform(self, match: re.Match):
        """

        Transform match object into a new object of the same type.

        """
        groupdict = match.groupdict()
        data = {key: value.format(**groupdict) for key, value in asdict(self).items()}
        obj = self.__class__(**data)
        return obj


@dataclass
class Item:
    """

    Key-value pair

    """
    key: Key
    value: Key

@dataclass
class Mapper:
    """
    
    Pattern-based, dictionary-like mapper.
    Compiles a single regex pattern from a list of rules, and determines which rule matched.
    It supports initialization from structured rule data, execution of a single lookup pass, and
    recursive lookups until a stable state is reached.

    """
    PREFIX_GROUP = '__'
    items: List[Item]
    default: Any = None
    is_recursive: bool = False

    @cached_property
    def pattern(self):
        """
        
        Provides a dynamically generated regex pattern based on the rules provided.

        """
        patterns = [
            MASK_NAMED.format(key=f'{self.PREFIX_GROUP}{i}', pattern=item.key.pattern)
            for i, item in enumerate(self.items)
        ]
        pattern = alt(*patterns)
        return pattern

    @cached_property
    def rx(self):
        """

        Regex object.

        """
        return re.compile(self.pattern)

    def get_default(self, key: Key):
        if self.is_recursive:
            return key
        else:
            return self.default

    def get(self, key: Key) -> Key:
        """

        Use recursive or single lookup pass, depending on whether recursive lookups have been specified.

        """
        if self.is_recursive:
            return self.get_recursive(key)
        else:
            return self.get_one(key)

    def get_one(self, key: Key):
        """

        Single lookup pass.
        Lookup the source string based on the matching rule.

        """

        match = self.rx.fullmatch(key.string)

        if not match:
            value = self.get_default(key)
            logger.debug(f'No match for {key=}.')
        else:

            match_ids = {name: v for name, v in match.groupdict().items() if v}
            rule_ids = {
                int(id.removeprefix(self.PREFIX_GROUP))
                for id in match_ids.keys() if id.startswith(self.PREFIX_GROUP)
            }

            if len(rule_ids) != 1:
                msg = f'Multiple group matches: {rule_ids}'
                raise ValueError(msg)

            rule_id = next(iter(rule_ids))
            rule = self.items[rule_id]

            if isinstance(rule.value, Key):
                value = rule.value.transform(match)
            else:
                value = rule.value

            logger.debug(f'Matched using {rule_id=}: {key=} → {value=}')

        return value

    def get_recursive(self, key: Key) -> Key:
        """

        Lookup the provided text by continuously applying lookup rules until no changes are made
        or a circular loop is detected.

        """
        history = []
        previous = key

        def get_history_str():
            return join(history, sep=' → ')

        with logger.span(f'Matching {key=}...'):
            while True:
                if previous in history:
                    history.append(previous)
                    msg = f'Loop detected on node "{previous}": {get_history_str()}'
                    raise RewriteCircularLoopError(msg)

                history.append(previous)

                new = previous

                new = self.get_one(new)

                if new == previous:
                    break

                previous = new

        if len(history) == 1:
            history_str = 'No matching performed.'
        else:
            history_str = get_history_str()
        logger.debug(f'Finished matching: {history_str}')

        return previous


if __name__ == '__main__':
    ...
