#!/usr/bin/env python3
import glob
import logging
import os
import sys
from typing import Dict, List, Optional, Set, TextIO, Tuple

from batchup.args import Namespace, parse_args
from batchup.backup import backup_recursively, inject_logger
from batchup.patterns import glob_to_path_matching_pattern
from batchup.rules import parse_rules

args: Namespace


def main() -> None:
    global args
    args = parse_args()
    logger = build_logger(args.verbose)
    inject_logger(logger)

    with open(args.rules) as f:
        paths, ignored_globs = parse_rules(f)
    run_backup(paths, ignored_globs)


def run_backup(paths: List[str], ignored_globs: Set[str]) -> None:
    """Backup paths to backup_dir."""
    ignored = {glob_to_path_matching_pattern(path) for path in ignored_globs}
    for path in paths:
        sources: List[str] = glob.glob(path, recursive=True)
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
