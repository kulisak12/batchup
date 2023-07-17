#!/usr/bin/env python3
from typing import Dict, Iterable, List, Optional, Set, TextIO, Tuple
import logging
import os
import re
import shutil

from batchup.patterns import matches_any


logger: logging.Logger


def backup_recursively(
    source: str, target: str, ignored: Set[re.Pattern], dry_run: bool
) -> None:
    """Backup source to target recursively.

    If source is a file, it is copied to target.
    If source is a directory, it is traversed recursively.
    If any file or directory matches an entry in ignored, it is skipped.
    """
    source = ensure_slash_if_dir(source)
    if matches_any(source, ignored):
        logger.log(10, f"Ignored: {source}")
        return
    if os.path.islink(source):
        logger.log(20, f"Skipping symlink: {source}")
        return
    if os.path.isfile(source):
        backup_file(source, target, dry_run)
        return
    if os.path.isdir(source):
        # recurse
        for filename in os.listdir(source):
            backup_recursively(
                os.path.join(source, filename),
                os.path.join(target, filename),
                ignored, dry_run
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


def ensure_slash_if_dir(path: str) -> str:
    """Ensure directory paths end with a slash."""
    if os.path.isdir(path):
        return os.path.join(path, "")
    return path


def inject_logger(logger_: logging.Logger) -> None:
    global logger
    logger = logger_
