import os
import shutil
import subprocess
import itertools
import julia_semver
from . import juliaup
from . import _jill
from . import install_julia
from . import util
from . import julia_version


def is_julia_executable(exe):
    """
    Return True if exe is the path to a Julia exectuable, otherwise False.

    The test consists of checking the output of "julia --version".
    """
    try:
        words = subprocess.run(
            [exe, '--version'], check=True, capture_output=True, encoding='utf8'
        ).stdout.strip().split()
    except:
        return False
    return len(words) == 3 and words[0] == "julia" and words[1] == "version"


# Strange to take the argument to skip check. But, it makes call site much simpler
def _check_path(path, check_exe=True):
    if not check_exe:
        return True
    if not os.path.isfile(path):
        return False
    return is_julia_executable(path)


def _to_semver(versions_paths):
    return [(julia_semver.version(v), p) for (v, p) in versions_paths]

def _default_locations(default=True):
    return {'jill': default, 'juliaup': default, 'which': default, 'env': default}

def _collect_paths(locations):
    all_paths = []
    def tolist(x):
        if x is None:
            return []
        return x if isinstance(x, list) else [x]
    # Finding juliaup versions is fast because they are cached in the filesystem.
    if locations['juliaup']:
        paths_juliaup = _to_semver(juliaup.version_path_list())
        all_paths.append(paths_juliaup)
    if locations['which']:
        wpath = shutil.which("julia")
        # Exclude ~/.juliaup/bin/julia . It actually links to julialauncher. This program
        # is not really julia. Eg, if DEPOT_PATH[1] has been changed, julialauncher will error.
        if wpath is not None and (not wpath.find("juliaup") >= 0): # juliaup is not in the path name
            paths_which = _to_semver(julia_version.to_version_path_list(tolist(wpath)))
            all_paths.append(paths_which)
    if locations['jill']:
        paths_jill = _to_semver(_jill.version_path_list())
        all_paths.append(paths_jill)
    return all_paths


def _env_var_julia(var_name):
    path = os.getenv(var_name)
    if path is None:
        return None, None
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Executable {var_name} = {path} does not exist.")
    version = julia_version.julia_version(path)
    return version, path


def _find_version(version_spec=None, check_exe=False, strict=False, env_var=None, locations=None):
    if version_spec is None:
        version_spec = julia_semver.semver_spec("^1")
    elif isinstance(version_spec, str):
        version_spec = julia_semver.semver_spec(version_spec)
    if locations is None:
        locations = _default_locations()
    if locations['env']:
        if env_var is None:
            env_var = "JULIA"
            env_version, env_path = _env_var_julia(env_var)
            if (env_version is not None and
                julia_semver.match(version_spec, env_version, strict=strict) and
                _check_path(env_path, check_exe)
                ):
                return (env_version, env_path)
    jlists = _collect_paths(locations=locations)
    paths = set(itertools.chain.from_iterable(jlists))
    maxv = julia_semver.version("0.0.0")
    best = (None, None)
    for vers, path in paths:
        if (vers > maxv and julia_semver.match(version_spec, vers, strict=strict)
            and _check_path(path, check_exe)):
            maxv = vers
            best = (vers, path)
    return best


def find(version_spec=None, check_exe=False, find_all=False, strict=False, env_var=None):
    """
    Search for and return the path to a Julia executable.

    Calling `find()` will use reasonable defaults.

    Parameters:
    env_var : The environment variable to check for a julia path.
        If this variable is set and the exectuable satisfies `version_spec`, then it will be
        preferred to all other paths. Default: "JULIA".
    version_spec : A Julia version specification as a str or object. The returned executable
        must satisfy this specification. Default: "^1".
    strict : If `True` then prerelease (development) versions will be excluded.
    check_exe : If `True` then check that the path is a Julia by querying it for the version.
        Note that this has already been done for most Julias found when the version was extracted.
    find_all : If `False` skip the locations that are slower to search. If no other exectuables
        are found, the slower locations may be searched anyway. The only slow location is the
        jill-installed location.
    """
    locations = _default_locations()
    if find_all is False: # Finding jill-installed julia versions is a bit slow
        locations['jill'] = False
    _, path = _find_version(
        version_spec=version_spec, check_exe=check_exe, strict=strict,
        env_var=env_var, locations=locations
    )
    if path is not None:
        return path
    if find_all is not True: # Try other places if no versions were acceptable
        locations = _default_locations(default=False)
        locations['jill'] = True
        _, path = _find_version(
            version_spec=version_spec, check_exe=check_exe, strict=strict, locations=locations
        )
    return path


def find_or_install(version_spec=None, check_exe=False, find_all=False, strict=False,
                    answer_yes=False, post_question_hook=None,
                    env_var=None): # , install_root=None):
    """
    Search for and return the path to a Julia executable or install one if none is found.

    Calling `find_or_install()` will use reasonable defaults.

    This function takes all the same parameters as does `find` as well as the following.
    Parameters:
    answer_yes - if `True`, then ask no questions, assume answers are "yes".
    post_question_hook -  a function to run if and after the consumer is asked whether
        to install Julia. This can be used to ask and record more questions rather
        than waiting till after the download. Default: None
    """
    path = find(
        version_spec=version_spec, check_exe=check_exe, find_all=find_all, strict=strict, env_var=env_var
    )
    if path is not None:
        return path
    util.log(f"No Julia version satisfying spec '{str(version_spec)}' found.")
    install_julia.prompt_and_install(
        answer_yes=answer_yes, post_question_hook=post_question_hook, version_spec=version_spec)
    # find_all=True !!
    path = find(version_spec=version_spec, check_exe=check_exe, find_all=True, strict=strict)
    return path
