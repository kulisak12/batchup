#!/usr/bin/env python3
import sys
from typing import Dict, List, Optional, Set, TextIO, Tuple
import glob
import logging
import os

from batchup.args import Namespace, parse_args
from batchup.backup import backup_recursively, inject_logger
from batchup.entries import parse_entries
from batchup.patterns import glob_to_path_matching_pattern


args: Namespace


def main() -> None:
    global args
    args = parse_args()
    logger = build_logger(args.verbose)
    inject_logger(logger)

    with open(args.entries) as f:
        entries, ignored_globs = parse_entries(f)
    run_backup(entries, ignored_globs)


def run_backup(entries: List[str], ignored_globs: Set[str]) -> None:
    """Backup entries to backup_dir."""
    ignored = {glob_to_path_matching_pattern(path) for path in ignored_globs}
    for entry in entries:
        sources: List[str] = glob.glob(entry, recursive=True)
        for source in sources:
            target = os.path.join(args.backup_dir, source.lstrip(os.path.sep))
            backup_recursively(source, target, ignored, args.dry_run)


def build_logger(verbose_count: int) -> logging.Logger:
    """Return a logger."""
    logger = logging.getLogger("batchup")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    verbosity = min(verbose_count, 2)
    logger.setLevel(30 - (10 * verbosity))
    return logger


if __name__ == "__main__":
    main()
