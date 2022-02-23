import subprocess


def julia_version(exe, slow=False):
    """
    Return the version of the julia executable `exe` as a string.

    Parameters:
    exe - the path to a possible Julia executable.
    slow - If `True` then get the variable `VERSION` from the julia runtime.
       If `False` then use the command line switch `--version` which is faster.
    """
    words = subprocess.run(
        [exe, '--version'], check=True, capture_output=True, encoding='utf8'
    ).stdout.strip().split()
    if len(words) != 3 and words[0] != "julia" and words[1] != "version":
        raise Exception(f"{exe} is not a julia exectuable")
    version = words[2]
    if slow and version.endswith("DEV"):
        return julia_version_slow(exe)
    return version


# The numbers after "DEV" (build) are ommited with --version
# Doing the following is slower, but prints the entire version
def julia_version_slow(exe):
    """
    Find the version of the Julia exectuable `exe` by examining the variable VERSION.
    """
    command = [exe, '-O', '0', '--startup-file=no', '--history-file=no',
               '-e', 'print(VERSION)']
    version = subprocess.run(
        command, check=True, capture_output=True, encoding='utf8'
    ).stdout.strip()
    return version


def to_version_path_list(paths):
    """
    Return a list of two-tuples consisting of Julia versions and paths give a list o paths.

    Parameters:
    paths - a list of paths to Julia executables. The versions will
        be determined by calling `julia --version`.
    """
    return [(julia_version(p), p) for p in paths]
