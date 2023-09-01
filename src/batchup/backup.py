#!/usr/bin/env python3
import logging
import os
import shutil
from typing import Optional, Pattern, Set

from batchup import BatchupError
from batchup.interrupt import ExitOnDoubleInterrupt
from batchup.target import TargetDerivation
from batchup.tree import categorize_paths_in_tree, is_newer, needs_zip_update
from batchup.zip import zip_directory

logger: logging.Logger


def backup_tree(
    tree: str, derivation: TargetDerivation,
    ignored: Set[Pattern[str]], keep_symlinks: bool, dry_run: bool
) -> None:
    """Performs a backup of a tree."""
    categorized_tree = categorize_paths_in_tree(tree, ignored, keep_symlinks)
    for source, category in categorized_tree:
        if category != "":
            logger.log(20, f"{category}: {source}")
            continue
        target = derivation(source)
        if not is_newer(source, target):
            logger.log(10, f"Up to date: {source}")
            continue

        backup_file(source, target, dry_run)


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
            if os.path.islink(source):
                _copy_link(source, target)
            else:
                shutil.copy(source, target)


def _copy_link(source: str, target: str) -> None:
    """Copies a symlink.

    Throws an exception if the symlink can't be copied.
    """
    try:
        os.symlink(os.readlink(source), target)
    except OSError as e:
        raise BatchupError("Symlink copy failed") from e


def backup_zip(
    source: str, derivation: TargetDerivation,
    keep_symlinks: bool, dry_run: bool
) -> None:
    """Zips source and backups it to target."""
    target = derivation(source) + ".zip"
    target_dir = os.path.dirname(target)
    if not needs_zip_update(source, target, keep_symlinks):
        logger.log(10, f"Up to date: {source}")
    elif dry_run:
        logger.log(30, f"Would zip: {source}")
    else:
        logger.log(30, f"Zipping: {source}")
        os.makedirs(target_dir, exist_ok=True)
        with ExitOnDoubleInterrupt(
            "Interrupt received, waiting for zip to finish. Interrupt again to force exit."
        ):
            zip_directory(
                source, target,
                keep_empty_dirs=True, keep_symlinks=keep_symlinks
            )


def inject_logger(logger_: logging.Logger) -> None:
    global logger
    logger = logger_
