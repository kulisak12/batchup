#!/usr/bin/env python3
import glob
import os
from typing import Generator, Iterable, Optional, Pattern, Set, Tuple

from batchup import BatchupError
from batchup.patterns import matches_any


def expand_globs(globs: Iterable[str]) -> Generator[str, None, None]:
    """Generates all paths defined by globs."""
    for path in globs:
        yield from glob.glob(path, recursive=True)


def is_newer(source: str, target: str) -> bool:
    """Tests if the source file is newer than the target file."""
    if not os.path.exists(target):
        return True
    # using lstat to avoid following symlinks
    source_time = os.lstat(source).st_mtime
    target_time = os.lstat(target).st_mtime
    # some devices have limited precision
    TOLERANCE = 10  # seconds
    return source_time - target_time > TOLERANCE


def categorize_paths_in_tree(
    path: str, ignored: Set[Pattern[str]], keep_symlinks: bool
) -> Generator[Tuple[str, str], None, None]:
    """Partitions the tree to ignored, skipped and included paths.

    The category of included paths is an empty string.
    """
    # allow patterns to filter dirs by a trailing slash
    path = _end_dir_with_slash(path)

    if matches_any(path, ignored):
        yield (path, "Ignored")
    elif os.path.islink(path):
        if keep_symlinks:
            yield (path, "")
        else:
            yield (path, "Skipped symlink")
    elif os.path.isfile(path):
        yield (path, "")
    elif os.path.isdir(path):
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            yield from categorize_paths_in_tree(
                entry_path, ignored, keep_symlinks
            )
    else:
        raise BatchupError(f"Can't process path: {path}")


def filter_included_files(
    path_category_pairs: Iterable[Tuple[str, str]]
) -> Generator[str, None, None]:
    """Filters only unignored and unskipped paths."""
    for path, category in path_category_pairs:
        if category == "":
            yield path


def needs_zip_update(dir: str, zip_file: str, keep_symlinks: bool) -> bool:
    """Decides whether contents of directory updated since zipped."""
    categorized_dir = categorize_paths_in_tree(dir, set(), keep_symlinks)
    for entry in filter_included_files(categorized_dir):
        if is_newer(entry, zip_file):
            return True
    return False


def _end_dir_with_slash(path: str) -> str:
    """Ensure directory paths end with a slash."""
    if os.path.isdir(path):
        return os.path.join(path, "")
    return path

