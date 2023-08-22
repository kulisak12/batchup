import os
import stat
import zipfile


def zip_directory(
    source: str, target: str,
    keep_empty_dirs: bool = True, keep_symlinks: bool = True
) -> None:
    """Zips up a directory."""
    # based on: https://gist.github.com/kgn/610907

    def _add_dir_to_archive(dir_path: str) -> None:
        contents = os.listdir(dir_path)
        # store empty directories
        if not contents and keep_empty_dirs:
            arcname = os.path.join(_arcname(dir_path), "")
            zip_info = zipfile.ZipInfo(arcname)
            zipf.writestr(zip_info, "")

        for item in contents:
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path) and not os.path.islink(item_path):
                _add_dir_to_archive(item_path)
            else:
                _add_file_to_archive(item_path)

    def _add_file_to_archive(file_path: str) -> None:
        arcname = _arcname(file_path)
        if not os.path.islink(file_path):
            zipf.write(file_path, arcname)
        elif keep_symlinks:
            zip_info = zipfile.ZipInfo(arcname)
            # zip_info.create_system = 3
            zip_info.external_attr |= stat.S_IFLNK << 16  # set link bit
            zipf.writestr(zip_info, os.readlink(file_path))

    def _arcname(path: str) -> str:
        """Returns the path within the zip archive."""
        return os.path.relpath(path, source)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zipf:
        _add_dir_to_archive(source)
