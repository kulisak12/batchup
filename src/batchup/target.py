import os
from typing import Callable, Optional

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
    return lambda source: os.path.join(
        backup_dir, os.path.relpath(source, source_root)
    )


def get_default_target_derivation(backup_dir: str) -> TargetDerivation:
    """Returns a function to derive backup target from source.

    The root of source tree is mounted at `backup_dir`.
    """
    root = os.path.abspath(os.sep)
    return get_target_derivation(root, backup_dir)
