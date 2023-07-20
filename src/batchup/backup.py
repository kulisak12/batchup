#!/usr/bin/env python3
import logging
import os
import shutil
from typing import Dict, Generator, List, Optional, Pattern, Set, TextIO, Tuple

from batchup.error import BatchupError
from batchup.interrupt import ExitOnDoubleInterrupt
from batchup.patterns import matches_any
from batchup.target import TargetDerivation

logger: logging.Logger


def backup_tree(
    tree: str, derivation: TargetDerivation,
    ignored: Set[Pattern[str]], dry_run: bool
) -> None:
    """Copies unignored files from tree to target."""
    for source in list_unignored_files_in_tree(tree, ignored):
        target = derivation(source)
        if is_newer(source, target):
            backup_file(source, target, dry_run)
        else:
            logger.log(10, f"Up to date: {source}")


def is_newer(source: str, target: str) -> bool:
    """Tests if the source file is newer than the target file."""
    if not os.path.exists(target):
        return True
    source_time = os.path.getmtime(source)
    target_time = os.path.getmtime(target)
    # some devices have limited precision
    TOLERANCE = 10  # seconds
    return source_time - target_time > TOLERANCE


def backup_file(source: str, target: str, dry_run: bool) -> None:
    """Backups source to target."""
    target_dir = os.path.dirname(target)
    if dry_run:
        logger.log(30, f"Would copy: {source}")
    else:
        logger.log(30, f"Copying: {source}")
        os.makedirs(target_dir, exist_ok=True)
        with ExitOnDoubleInterrupt(
            "Interrupt received, waiting for copy to finish. Interrupt again to force exit."
        ):
            shutil.copy(source, target)


def list_unignored_files_in_tree(
    path: str, ignored: Set[Pattern[str]]
) -> Generator[str, None, None]:
    """Generates paths to unignored files."""
    # allow patterns to filter dirs by a trailing slash
    path = end_dir_with_slash(path)

    if matches_any(path, ignored):
        logger.log(10, f"Ignored: {path}")
    elif os.path.islink(path):
        logger.log(20, f"Skipping symlink: {path}")
    elif os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            yield from list_unignored_files_in_tree(entry_path, ignored)
    else:
        raise BatchupError(f"Can't process path: {path}")


def end_dir_with_slash(path: str) -> str:
    """Ensure directory paths end with a slash."""
    if os.path.isdir(path):
        return os.path.join(path, "")
    return path


def inject_logger(logger_: logging.Logger) -> None:
    global logger
    logger = logger_
