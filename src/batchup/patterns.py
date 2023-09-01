import re
from typing import Iterable, Pattern


def matches(s: str, pat: Pattern[str]) -> bool:
    return pat.match(s) is not None


def matches_any(s: str, pats: Iterable[Pattern[str]]) -> bool:
    return any(matches(s, pat) for pat in pats)


def glob_to_path_matching_pattern(glob: str) -> Pattern[str]:
    """Compiles a glob pattern of a path to a regular expression."""
    pattern = _translate(glob)
    if not pattern.endswith("/"):
        pattern += "/?"
    anchored = r'(?s:%s)\Z' % pattern
    return re.compile(anchored)


def _translate(pat: str) -> str:
    """Translates a shell PATTERN to a regular expression.

    Similar to fnmatch, but '*' only matches a single path segment.
    Multiple segments can be matched by '**'.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            if i < n and pat[i] == '*':
                res = res + '.*'
                i = i+1
            else:
                res = res + '[^/]*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j]
                if '--' not in stuff:
                    stuff = stuff.replace('\\', r'\\')
                else:
                    chunks = []
                    k = i+2 if pat[i] == '!' else i+1
                    while True:
                        k = pat.find('-', k, j)
                        if k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k+1
                        k = k+3
                    chunks.append(pat[i:j])
                    # Escape backslashes and hyphens for set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = '-'.join(s.replace('\\', r'\\').replace('-', r'\-')
                                     for s in chunks)
                # Escape set operations (&&, ~~ and ||).
                stuff = re.sub(r'([&~|])', r'\\\1', stuff)
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] in ('^', '['):
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res
