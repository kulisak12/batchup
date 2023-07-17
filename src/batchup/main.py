#!/usr/bin/env python3
import sys
from typing import Dict, List, Optional, Set, TextIO, Tuple
import glob
import logging
import os

from batchup.args import Namespace, parse_args
from batchup.backup import backup_recursively, inject_logger
from batchup.entries import Entry, parse_entries
from batchup.patterns import glob_to_path_matching_pattern


args: Namespace


def main() -> None:
    global args
    args = parse_args()
    logger = build_logger(args.verbose)
    inject_logger(logger)

    with open(args.entries) as f:
        entries, ignored_globs = parse_entries(f, args.sep)
    run_backup(entries, ignored_globs)


def run_backup(entries: List[Entry], ignored_globs: Set[str]) -> None:
    """Backup entries to backup_dir."""
    ignored = {glob_to_path_matching_pattern(path) for path in ignored_globs}
    for entry in entries:
        sources: List[str] = glob.glob(entry.source, recursive=True)
        for source in sources:
            basename = os.path.basename(source.rstrip(os.path.sep))
            target = os.path.join(args.backup_dir, entry.target, basename)
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
