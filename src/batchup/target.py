import os
from typing import Callable, Optional

from batchup import BatchupError


class DerivationError(BatchupError):
    """Error raised during target derivation."""
    pass


TargetDerivation = Callable[[str], str]


def select_target_derivation(
        root: Optional[str], backup_dir: str
) -> TargetDerivation:
    """Selects a function to derive backup target from source."""
    if root is None:
        return get_default_target_derivation(backup_dir)
    else:
        return get_target_derivation(root, backup_dir)


def get_target_derivation(source_root: str, backup_dir: str) -> TargetDerivation:
    """Returns a function to derive backup target from source.

    The source tree starting at `source_root` is mounted at `backup_dir`.
    """
    # prevent same-file errors and repeated backups
    if _is_subdir(source_root, backup_dir):
        raise BatchupError(
            f"Root can't be a subdirectory of backup dir"
        )

    def derivation(source: str) -> str:
        # source_root must be a prefix of source
        if not _is_subdir(source, source_root):
            raise DerivationError(
                f"Source {source} is not in tree of {source_root}"
            )
        relpath = os.path.relpath(source, source_root)
        return os.path.join(backup_dir, relpath)

    return derivation


def get_default_target_derivation(backup_dir: str) -> TargetDerivation:
    """Returns a function to derive backup target from source.

    The root of source tree is mounted at `backup_dir`.
    """
    root = os.path.abspath(os.sep)
    return get_target_derivation(root, backup_dir)


def _is_subdir(path: str, parent: str) -> bool:
    """Returns True if `path` is a subdirectory of `parent`."""
    path = os.path.abspath(path)
    parent = os.path.abspath(parent)
    return path.startswith(parent)
