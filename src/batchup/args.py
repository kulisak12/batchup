import argparse
from typing import Any, Optional


class Namespace(argparse.Namespace):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.dry_run: bool
        self.keep_symlinks: bool
        self.orphans: bool
        self.root: Optional[str]
        self.verbose: int

        self.rules: str
        self.backup_dir: str


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument("-n", "--dry-run", action="store_true", help="Don't copy anything, just show what would be done.")
    parser.add_argument("-l", "--keep-symlinks", action="store_true", help="Keep symbolic links. The target filesystem must support them.")
    parser.add_argument("-o", "--orphans", action="store_true", help="Don't back up; list files that are backed up but have no preimage.")
    parser.add_argument("-r", "--root", default=None, help="The path that will correspond to the backup directory. Defaults to filesystem root.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Be more verbose. Can be used up to 2 times.")

    parser.add_argument("rules", help="Path to the rules file.")
    parser.add_argument("backup_dir", help="Path to the backup directory.")

    parser.epilog = """
The rules file contains several sections preceded by a header. Each section
consists of glob patterns, one per line. The following headers are recognized:
- [copy]: Files and directories that will be backed up.
- [ignore]: Patterns that will not be backed up.
- [zip]: Directories that will be backed up as zip files.
- [exec]: Scripts that will be executed before the backup starts.
"""

    args = Namespace()
    parser.parse_args(namespace=args)
    return args
