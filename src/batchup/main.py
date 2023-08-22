#!/usr/bin/env python3
import logging
import os
import sys
from typing import Dict, List, Optional, Set, TextIO, Tuple

from batchup.args import Namespace, parse_args
from batchup.backup import backup_tree, backup_zip, expand_globs, inject_logger
from batchup.patterns import glob_to_path_matching_pattern
from batchup.rules import parse_rules
from batchup.target import TargetDerivation, select_target_derivation

args: Namespace
logger: logging.Logger


def main() -> None:
    global args
    global logger
    args = parse_args()
    logger = build_logger(args.verbose)
    inject_logger(logger)

    target_derivation = select_target_derivation(args.root, args.backup_dir)
    with open(args.rules) as f:
        exec_paths, copy_paths, zip_paths, ignored_globs = parse_rules(f)
    # no need to copy files that will be zipped
    ignored_globs.update(zip_paths)

    run_execs(exec_paths)
    run_backup(copy_paths, zip_paths, target_derivation, ignored_globs)


def run_execs(exec_paths: List[str]) -> None:
    """Execute scripts.

    Scripts are executed in the current directory.
    """
    for exec_path in expand_globs(exec_paths):
        if args.dry_run:
            logger.log(30, f"Would execute: {exec_path}")
        else:
            logger.log(30, f"Executing: {exec_path}")
            os.system(exec_path)


def run_backup(
    paths: List[str], zip_paths: List[str],
    target_derivation: TargetDerivation, ignored_globs: Set[str]
) -> None:
    """Backup paths to backup_dir."""
    ignored = {glob_to_path_matching_pattern(path) for path in ignored_globs}
    for source_tree in expand_globs(paths):
        backup_tree(
            source_tree, target_derivation,
            ignored, args.keep_symlinks, args.dry_run
        )
    for zip_tree in expand_globs(zip_paths):
        backup_zip(
            zip_tree, target_derivation,
            args.keep_symlinks, args.dry_run
        )


def build_logger(verbose_count: int) -> logging.Logger:
    """Return a logger."""
    logger = logging.getLogger("batchup")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    verbosity = min(verbose_count, 2)
    logger.setLevel(30 - (10 * verbosity))
    return logger


if __name__ == "__main__":
    main()
