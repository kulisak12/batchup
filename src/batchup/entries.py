from typing import Dict, List, Optional, Set, TextIO, Tuple

from batchup.error import BatchupError


def parse_entries(
    entries_file: TextIO
) -> Tuple[List[str], Set[str]]:
    """Parses entries and ignored patterns from a file."""
    sections = parse_headered_file(entries_file)
    entries = sections.pop("", []) + sections.pop("[copy]", [])
    ignored = set(sections.pop("[ignore]", []))
    if sections:
        raise BatchupError(f"Unknown section(s): {', '.join(sections)}")
    return entries, ignored


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
