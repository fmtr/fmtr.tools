import regex as re
from dataclasses import dataclass
from functools import cached_property
from typing import List

from fmtr.tools.logging_tools import logger


class RewriteCircularLoopError(Exception):
    """

    Circular loop error

    """


@dataclass
class Rule:
    """
    Represents a single rule for pattern matching and target string replacement.

    This class is used to define a rule with a pattern and a target string.
    The `pattern` is a regular expression used to identify matches in input text.
    The `target` allows rewriting the identified matches with a formatted string.
    It provides properties for generating a unique identifier for use as a regex group name and compiling the provided pattern into a regular expression object.

    """
    pattern: str
    target: str

    @cached_property
    def id(self):
        """
        
        Regex group name.
        
        """
        return f'id{abs(hash(self.pattern))}'

    @cached_property
    def rx(self):
        """

        Regex object.

        """
        return re.compile(self.pattern)

    def apply(self, match: re.Match):
        """

        Rewrite using the target string and match groups.

        """
        target = self.target.format(**match.groupdict())
        return target


@dataclass
class Rewriter:
    """
    
    Represents a Rewriter class that handles pattern matching, rule application, and text rewriting.
    Compiles a single regex pattern from a list of rules, and determines which rule matched.
    It supports initialization from structured rule data, execution of a single rewrite pass, and
    recursive rewriting until a stable state is reached.

    """
    rules: List[Rule]

    @cached_property
    def pattern(self):
        """
        
        Provides a dynamically generated regex pattern based on the rules provided.

        """
        patterns = [fr"(?P<{rule.id}>{rule.pattern})" for rule in self.rules]
        sorted(patterns, key=len, reverse=True)
        pattern = '|'.join(patterns)
        return pattern

    @cached_property
    def rule_lookup(self):
        """

        Dictionary mapping rule identifiers to their corresponding rules.
        """

        return {rule.id: rule for rule in self.rules}

    @cached_property
    def rx(self):
        """

        Regex object.

        """
        return re.compile(self.pattern)

    def rewrite_pass(self, source: str):
        """

        Single rewrite pass.
        Rewrites the provided source string based on the matching rule.

        """

        match = self.rx.match(source)

        if not match:
            return source

        match_ids = {k: v for k, v in match.groupdict().items() if v}
        match_id = match_ids & self.rule_lookup.keys()

        if len(match_id) != 1:
            msg = f'Multiple group matches: {match_id}'
            raise ValueError(msg)

        match_id = next(iter(match_id))
        rule = self.rule_lookup[match_id]
        target = rule.apply(match)

        logger.debug(f'Rewrote using {match_id=}: {source=} -> {target=}')

        return target

    def rewrite(self, source: str) -> str:
        """

        Rewrites the provided text by continuously applying rewrite rules until no changes are made
        or a circular loop is detected.

        """
        history = []
        previous = source

        def get_history_str():
            return ' -> '.join(history)

        with logger.span(f'Rewriting "{source}"...'):
            while True:
                if previous in history:
                    history.append(previous)
                    msg = f'Loop detected on node "{previous}": {get_history_str()}'
                    raise RewriteCircularLoopError(msg)

                history.append(previous)

                new = previous

                new = self.rewrite_pass(new)

                if new == previous:
                    break

                previous = new

            logger.debug(f'Finished rewriting: {get_history_str()}')

        return previous

    @classmethod
    def from_data(cls, data):
        rules = [Rule(*pair) for pair in data.items()]
        self = cls(rules=rules)
        return self


if __name__ == '__main__':
    data = {

        r'(?P<name>[a-z]+)\.dev\.example\.com': '{name}.test.example.com',
        r'img\d+\.static\.cdn\.example\.com': 'images.cdn.example.com',
        r'service\.(?P<env>dev|staging|prod)\.example\.org': '{env}-service.example.org',
        r'legacy\.(?P<region>[a-z]+)\.oldsite\.com': '{region}.newsitenow.com',
        r'shop\.(?P<country_code>[a-z]{2})\.example\.net': 'store.{country_code}.example.net',
        r'(?P<user>[a-z]+)\.mail\.example\.com': '{user}.email.example.com',
        r'app1\.cluster(?P<num>[0-9]+)\.example\.cloud': 'service{num}.example.cloud',
        r'(?P<project>[a-z]+)\.research\.corp\.com': '{project}.lab.corp.com',
        r'cdn\.(?P<version>v[0-9]+)\.content\.net': 'static.{version}.content.net',
        # Literal rule without named group
        r'corp\.secureaccess\.com': 'access.corp.com',
        # Literal rule without named group
        r'redirect\.oldsite\.org': 'homepage.newsite.org',
        # # Recursive rules

        r'archive\.(?P<year>\d{4})\.oldsite\.net': 'legacy.{year}.oldsite.net',  # Recursive matching
        r'legacy\.(?P<year>\d{4})\.oldsite\.net': 'archive-backup.{year}.net',  # Continuation

        # r'(?P<subd>[a-zA-Z]+)\.vpn': '{subd}.loop.ts.net',
        # r'(?P<subd>[a-zA-Z]+)\.loop\.ts\.net': '{subd}.vpn',  # Recursive loop back to .vpn
    }

    rewriter = Rewriter.from_data(data)

    tests = [
        "sales.vpn",
        "marketing.dev.example.com",
        "img01.static.cdn.example.com",
        "service.dev.example.org",
        "legacy.eu.oldsite.com",
        "shop.us.example.net",
        "alice.mail.example.com",
        "app1.cluster1.example.cloud",
        "genetics.research.corp.com",
        "cdn.v2.content.net",
        "corp.secureaccess.com",
        "redirect.oldsite.org",
        "support.bbb.ts.net",
        "support.ccc.ts.net",
        "archive.2022.oldsite.net",
        "legacy.2022.oldsite.net",
        "finance.vpn",
        "engineering.dev.example.com",
        "img02.static.cdn.example.com",
        "service.staging.example.org",
        "legacy.apac.oldsite.com",
        "shop.uk.example.net",
        "bob.mail.example.com",
        "app1.cluster2.example.cloud",
        "astrophysics.research.corp.com",
        "cdn.v3.content.net",
        "archive.2021.oldsite.net",
        "legacy.2021.oldsite.net",
        "quality.bbb.ts.net",
        "quality.ccc.ts.net"
    ]

    logger.warning('hello?')
    for test in tests:
        print(test)
        text = rewriter.rewrite(test)
        text

    tests
