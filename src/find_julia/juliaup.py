import subprocess
import shutil
import json
import os
import warnings


def _is_juliaup_locked(exe):
    assert exe is not None
    with subprocess.Popen(
        [exe, "status"], stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, encoding='utf8'
    ) as process:
        while True:
            output = process.stderr.readline().strip()
            if output.startswith("Juliaup configuration"):
                return True
            if output == '' and process.poll() is not None:
                return False


def _check_is_juliaup_locked(exe):
    assert exe is not None
    if _is_juliaup_locked(exe):
        raise Exception(f"{exe} is locked. Try again later")


def _is_juliaup_executable(exe):
    """
    Return True if exe is the path to a juliaup exectuable, otherwise False.

    The test consists of checking the output of "juliaup --version".
    """
    if exe is None or not os.path.isfile(exe):
        return False
    try:
        words = subprocess.run(
            [exe, '--version'], check=True, capture_output=True, encoding='utf8'
        ).stdout.strip().split()
    except Exception as err:
        print(err)
        return False
    return len(words) == 2 and words[0] == "Juliaup"


def reset_env_var(var_name, old_val):
    if old_val:
        os.environ[var_name] = old_val
    elif os.getenv(var_name):
        del os.environ[var_name]


def _get_juliaup_config():
    exe = shutil.which("juliaup")
    if exe is None:
        return None
    if not _is_juliaup_executable(exe):
        warnings.warn(f"{exe} is not a valid juliaup executable", RuntimeWarning)
        return None
    _check_is_juliaup_locked(exe)
    payload = subprocess.run(
        [exe, "api", "getconfig1"], check=True, capture_output=True, encoding='utf8'
    ).stdout.strip()
    juliaup_config = json.loads(payload)
    if juliaup_config["DefaultChannel"] is not None:
        return juliaup_config

    old_julia_depot_path = os.getenv("JULIA_DEPOT_PATH") # Maybe juliaup is looking in the wrong depot.
    # Follow code in initdefs.jl here.
    os.environ["JULIA_DEPOT_PATH"] = os.path.join(os.path.expanduser("~"), ".julia")
    payload = subprocess.run(
        [exe, "api", "getconfig1"], check=True, capture_output=True, encoding='utf8'
    ).stdout.strip()
    juliaup_config = json.loads(payload)
    reset_env_var("JULIA_DEPOT_PATH", old_julia_depot_path)
    return juliaup_config


def version_path_list():
    """
    Return a list of julia versions and executable paths as two-tuples.

    Each two-tuple is of the form `(version, path)`.
    """
    config = _get_juliaup_config()
    if config is None:
        return []
    channels = config["OtherChannels"]
    chlist = []
    for chan in channels:
        chlist.append((chan['Version'], chan['File']))
    return chlist
