#!/usr/bin/env python3
import sys
from typing import Dict, List, Optional, Set, TextIO, Tuple
import glob
import logging
import os

from batchup.args import Namespace, parse_args
from batchup.entries import Entry, parse_entries
from batchup.backup import backup_recursively, inject_logger


args: Namespace


def main() -> None:
    global args
    args = parse_args()
    logger = build_logger()
    inject_logger(logger)

    with open(args.entries) as f:
        entries, ignored = parse_entries(f, args.sep)
    run_backup(entries, ignored)


def run_backup(entries: List[Entry], ignored: Set[str]) -> None:
    """Backup entries to backup_dir."""
    # remove slash from source and ignored paths
    # so that we can compare them easily
    ignored = {remove_slash(path) for path in ignored}
    for entry in entries:
        sources: List[str] = glob.glob(entry.source, recursive=True)
        for source in sources:
            source = remove_slash(source)
            basename = os.path.basename(source)
            target = os.path.join(args.backup_dir, entry.target, basename)
            backup_recursively(source, target, ignored, args.dry_run)


def remove_slash(path: str) -> str:
    """Remove trailing slash from path."""
    if path.endswith(os.path.sep):
        return path[:-1]
    return path


def build_logger() -> logging.Logger:
    """Return a logger."""
    logger = logging.getLogger("batchup")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    verbosity = min(args.verbose, 2)
    logger.setLevel(30 - (10 * verbosity))
    return logger


if __name__ == "__main__":
    main()
