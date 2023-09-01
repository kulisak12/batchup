from typing import List, Pattern, Set

from batchup.backup import get_zip_name
from batchup.rules import Rules
from batchup.target import TargetDerivation
from batchup.tree import list_included_paths_in_tree


def list_orphans(
    rules: Rules, target_derivation: TargetDerivation,
    keep_symlinks: bool, backup_dir: str
):
    """Generates paths to files that are in backup_dir but not in source."""
    expected_targets = {
        target_derivation(source)
        for source in list_expected_sources(
            rules, keep_symlinks
        )
    }
    for target in list_included_paths_in_tree(
        backup_dir, set(), keep_symlinks=True
    ):
        if target not in expected_targets:
            yield target


def list_expected_sources(
    rules: Rules, keep_symlinks: bool
):
    """Generates paths to files that should be backed up."""
    for source_tree in rules.copy:
        yield from list_included_paths_in_tree(
            source_tree, rules.ignore, keep_symlinks
        )
    for zip_tree in rules.zip:
        yield get_zip_name(zip_tree)
