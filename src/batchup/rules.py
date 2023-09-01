from typing import Dict, List, NamedTuple, Pattern, Set, TextIO

from batchup import BatchupError
from batchup.patterns import glob_to_path_matching_pattern
from batchup.tree import expand_globs


class RulesGlobs(NamedTuple):
    exec: List[str]
    copy: List[str]
    zip: List[str]
    ignore: List[str]


class Rules(NamedTuple):
    exec: List[str]
    copy: List[str]
    zip: List[str]
    ignore: Set[Pattern[str]]


def expand_rules(rules_globs: RulesGlobs) -> Rules:
    """Expands globs into lists of paths."""
    # no need to copy files that will be zipped
    ignore = rules_globs.ignore + rules_globs.zip
    patterns = {glob_to_path_matching_pattern(glob) for glob in ignore}
    return Rules(
        expand_globs(rules_globs.exec),
        expand_globs(rules_globs.copy),
        expand_globs(rules_globs.zip),
        patterns
    )


def parse_rules(
    rules_file: TextIO
) -> RulesGlobs:
    """Parses rules globs from a file."""
    sections = parse_headered_file(rules_file)
    exec = sections.pop("[exec]", [])
    copy = sections.pop("", []) + sections.pop("[copy]", [])
    zip = sections.pop("[zip]", [])
    ignore = sections.pop("[ignore]", [])
    if sections:
        raise BatchupError(f"Unknown section(s): {', '.join(sections)}")
    return RulesGlobs(exec, copy, zip, ignore)


def parse_headered_file(file: TextIO) -> Dict[str, List[str]]:
    """Reads a file in simplified INI format.

    Returns a list of non-comment lines grouped by header.
    Lines before the first header are stored under an empty name.
    """
    result: Dict[str, List[str]] = {}
    section = ""
    result[section] = []
    for line in file:
        line = line.rstrip()
        if not line or is_comment(line):
            pass
        elif is_header(line):
            section = line
            result[section] = []
        else:
            result[section].append(line)
    return result


def is_comment(line: str) -> bool:
    return line.startswith(";")


def is_header(line: str) -> bool:
    return line.startswith("[") and line.endswith("]")
