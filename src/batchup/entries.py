from typing import Dict, List, Optional, Set, TextIO, Tuple
import dataclasses


@dataclasses.dataclass(frozen=True)
class Entry:
    source: str
    target: str


class EntryError(Exception):
    pass


COMMENT_CHAR = "#"
IGNORE_CHAR = "!"


def parse_entries(
    entries_file: TextIO, sep: str
) -> Tuple[List[Entry], Set[str]]:
    """Parse entries and ignored patterns from a file."""
    entries: List[Entry] = []
    ignored: Set[str] = set()
    for line in entries_file:
        line = line.rstrip()
        if not line or line.startswith(COMMENT_CHAR):
            continue
        # ignore pattern
        if line.startswith(IGNORE_CHAR):
            ignored.add(line[1:])
            continue
        # entry
        parts = line.split(sep)
        if len(parts) != 2:
            raise EntryError(f"Invalid entry: {line}")
        entries.append(Entry(parts[0], parts[1]))
    return entries, ignored
