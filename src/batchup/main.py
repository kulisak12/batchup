#!/usr/bin/env python3
import logging
import os
import sys
from typing import Dict, List, Optional, Pattern, Set, TextIO, Tuple

from batchup.args import Namespace, parse_args
from batchup.backup import backup_tree, backup_zip, inject_logger
from batchup.orphans import list_orphans
from batchup.rules import Rules, expand_rules, parse_rules
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
        rules_globs = parse_rules(f)
    rules = expand_rules(rules_globs)

    run_execs(rules.exec)
    run_backup(rules, target_derivation)


def run_execs(exec_paths: List[str]) -> None:
    """Execute scripts.

    Scripts are executed in the current directory.
    """
    for exec_path in exec_paths:
        if args.dry_run:
            logger.log(30, f"Would execute: {exec_path}")
        else:
            logger.log(30, f"Executing: {exec_path}")
            os.system(exec_path)


def run_backup(rules: Rules, target_derivation: TargetDerivation) -> None:
    """Backup paths to backup_dir."""
    for source_tree in rules.copy:
        backup_tree(
            source_tree, target_derivation,
            rules.ignore, args.keep_symlinks, args.dry_run
        )
    for zip_tree in rules.zip:
        backup_zip(
            zip_tree, target_derivation,
            args.keep_symlinks, args.dry_run
        )


def print_orphans(rules: Rules, target_derivation: TargetDerivation) -> None:
    """Lists files that are in backed up but not in source."""
    for orphan in list_orphans(
        rules, target_derivation,
        args.keep_symlinks, args.backup_dir
    ):
        print(orphan)


def build_logger(verbose_count: int) -> logging.Logger:
    """Return a logger."""
    logger = logging.getLogger("batchup")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    verbosity = min(verbose_count, 2)
    logger.setLevel(30 - (10 * verbosity))
    return logger


if __name__ == "__main__":
    main()
