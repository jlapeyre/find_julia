# This file should only be used until these features are available in jill.py
import os
import getpass
import platform

from .julia_version import to_version_path_list

# import jill
### `install_from_jill` below is the only function that requires jill.
### So, we import jill in the function rather than at the top
### jill.py takes 50-60 ms to load, much longer to load than anything else.

### Code taken from jill.py source
### This is all that is necessary to examine installation locations.
### If we need to install, we load the heavier jill dependency.


def _current_system():
    rst = platform.system()
    if rst.lower() == "linux":
        return "linux"
    if rst.lower() == "darwin":
        return "mac"
    if rst.lower() == "freebsd":
        return "freebsd"
    if rst.lower() == "windows":
        return "winnt"
    raise ValueError(f"Unsupported system {rst}")


def _default_install_dir():
    _dir = os.environ.get("JILL_INSTALL_DIR", None)
    if _dir:
        return os.path.expanduser(_dir)

    system = _current_system()
    if system == "mac":
        return "/Applications"
    if system in ["linux", "freebsd"]:
        if getpass.getuser() == "root":
            return "/opt/julias"
        return os.path.expanduser("~/packages/julias")
    if system == "winnt":
        return os.path.expanduser(r"~\AppData\Local\julias")
    raise ValueError(f"Unsupported system: {system}")

### End code taken from jill.py source

# There is a PR to put the following in jill.py itself. I just have to finish it.
def _get_relative_bin_path():
    system = _current_system()
    if system == "winnt":
        return os.path.join("bin", "julia.exe")
    if system == "mac":
        return os.path.join("Contents", "Resources", "julia", "bin", "julia")
    if system in ["linux", "freebsd"]:
        return os.path.join("bin", "julia")
    raise ValueError(f"Unsupported system {system}")


def _julia_bin_paths(install_root_dir=None):
    if install_root_dir is None:
        install_root_dir = _default_install_dir()
    if not os.path.isdir(install_root_dir):
        return None
    rel_bin_path = _get_relative_bin_path()
    return [os.path.join(install_root_dir, subdir, rel_bin_path)
            for subdir in os.listdir(install_root_dir) if subdir.startswith("julia")]


def version_path_list(install_root_dir=None):
    """
    Return a list of two-tuples of versions and paths of Julias installed by jill.py.
    """
    system = _current_system()
    if install_root_dir is None and system in ["linux", "freebsd"]:
        root = os.path.join("/", "opt", "julias")
        paths1 = _julia_bin_paths(install_root_dir=root)
        root = os.path.expanduser(os.path.join("~", "packages", "julias"))
        paths2 = _julia_bin_paths(install_root_dir=root)
        paths1 = paths1 if paths1 else []
        paths2 = paths2 if paths2 else []
        paths = paths1 + paths2
    else:
        paths = _julia_bin_paths(install_root_dir=install_root_dir)
    return to_version_path_list(paths)


def install_from_jill(answer_yes=False, version=None):
    """
    Use jill.py to install Julia.

    Parameters:
    answer_yes : If `True` ask no questions, assuming answers are "yes".
    version str : The Julia version to install. If `None`, then the latest
       stable release is installed. Default: None
    """
    import jill.install
    result = jill.install.install_julia(confirm=answer_yes, version=version)
    print(f"Install from jill returned '{result}'.") # Return val is complicted, not documented.
    return result
