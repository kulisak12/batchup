#!/usr/bin/env python3
import logging
import os
import re
import shutil
from typing import Dict, Generator, List, Optional, Set, TextIO, Tuple

from batchup.error import BatchupError
from batchup.patterns import matches_any

logger: logging.Logger


def cover_tree_without_ignored(
    path: str, ignored: Set[re.Pattern]
) -> Generator[str, None, None]:
    """Generates a disjoin cover of the non-ignored subtree of path.

    Creates the smallest possible cover:
    lists the entire directory if nothing in subtree is ignored.
    """
    for entry in _cover_tree_without_ignored(path, ignored):
        if entry is not None:
            yield entry


def _cover_tree_without_ignored(
    path: str, ignored: Set[re.Pattern]
) -> Generator[Optional[str], None, None]:
    """Internal version of `cover_tree_without_ignored`.
    Yields `None` for skipped entries.
    """
    # allow patterns to filter dirs by a trailing slash
    path = end_dir_with_slash(path)
    if matches_any(path, ignored):
        yield None
        logger.log(10, f"Ignored: {path}")
    elif os.path.islink(path):
        yield None
        logger.log(20, f"Skipping symlink: {path}")
    elif os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        yield from _cover_dir_tree_without_ignored(path, ignored)
    else:
        raise BatchupError(f"Can't process path: {path}")


def _cover_dir_tree_without_ignored(
    dir: str, ignored: Set[re.Pattern]
) -> Generator[Optional[str], None, None]:
    """Version of `cover_tree_without_ignored` for a directory."""
    postponed: List[str] = []
    has_skipped = False

    # don't yield results immediately, save them to postponed
    # if nothing in subtree is ignored, discard the results and return dir
    # if something is ignored, flush the previous results
    # (which should come first) and then only then continue traversing
    for entry_result in _list_dir_covers(dir, ignored):
        if entry_result is None:
            yield None  # flush postponed from callers
            if not has_skipped:
                has_skipped = True
                yield from postponed
        elif has_skipped:
            yield entry_result
        else:
            postponed.append(entry_result)

    # can return the entire directory
    if not has_skipped:
        yield dir


def _list_dir_covers(
    dir: str, ignored: Set[re.Pattern]
) -> Generator[Optional[str], None, None]:
    """Generates a concatenation of covers of directory entries."""
    for entry in os.listdir(dir):
        entry_path = os.path.join(dir, entry)
        yield from cover_tree_without_ignored(entry_path, ignored)


def list_outdated_files(source: str, target: str) -> Generator[str, None, None]:
    """Generates paths to outdated files.

    Source must be a regular file or a directory.
    """
    if os.path.isfile(source):
        if not is_newer(source, target):
            logger.log(10, f"Up to date: {source}")
        else:
            yield source
        return

    # directory => recurse
    for entry in os.listdir(source):
        yield from list_outdated_files(
            os.path.join(source, entry),
            os.path.join(target, entry)
        )


def backup_file(source: str, target: str, dry_run: bool) -> None:
    """Copies source to target if source is newer than target."""
    target_dir = os.path.dirname(target)
    if not dry_run:
        os.makedirs(target_dir, exist_ok=True)

    if not is_newer(source, target):
        logger.log(10, f"Up to date: {source}")
    elif dry_run:
        logger.log(30, f"Would copy: {source}")
    else:
        logger.log(30, f"Copying: {source}")
        shutil.copy(source, target)


def is_newer(source: str, target: str) -> bool:
    """Tests if the source file is newer than the target file."""
    if not os.path.exists(target):
        return True
    source_time = os.path.getmtime(source)
    target_time = os.path.getmtime(target)
    # some devices have limited precision
    TOLERANCE = 10  # seconds
    return source_time - target_time > TOLERANCE


def end_dir_with_slash(path: str) -> str:
    """Ensure directory paths end with a slash."""
    if os.path.isdir(path):
        return os.path.join(path, "")
    return path


def inject_logger(logger_: logging.Logger) -> None:
    global logger
    logger = logger_
