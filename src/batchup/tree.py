#!/usr/bin/env python3
import glob
import os
from typing import Generator, Iterable, List, Pattern, Set, Tuple

from batchup import BatchupError
from batchup.patterns import matches_any


def expand_globs(globs: List[str]) -> List[str]:
    """Generates all paths defined by globs."""
    paths: List[str] = []
    for path in globs:
        paths.extend(glob.glob(path))
    return paths


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


def list_included_paths_in_tree(
    tree: str, ignore: Set[Pattern[str]], keep_symlinks: bool
) -> Generator[str, None, None]:
    """Generates paths to files that aren't ignored or skipped."""
    categorized_tree = categorize_paths_in_tree(tree, ignore, keep_symlinks)
    yield from filter_included_files(categorized_tree)


def categorize_paths_in_tree(
    path: str, ignore: Set[Pattern[str]], keep_symlinks: bool
) -> Generator[Tuple[str, str], None, None]:
    """Partitions the tree to ignored, skipped and included paths.

    The category of included paths is an empty string.
    """
    # allow patterns to filter dirs by a trailing slash
    decorated_path = _end_dir_with_slash(path)

    if matches_any(decorated_path, ignore):
        yield (decorated_path, "Ignored")
    elif os.path.islink(path):  # must use un-decorated path
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
                entry_path, ignore, keep_symlinks
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
    included = list_included_paths_in_tree(dir, set(), keep_symlinks)
    for entry in included:
        if is_newer(entry, zip_file):
            return True
    return False


def _end_dir_with_slash(path: str) -> str:
    """Ensures directory paths end with a slash."""
    if os.path.isdir(path):
        return os.path.join(path, "")
    return path

