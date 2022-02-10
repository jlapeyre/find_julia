# find_julia

This package provides the Python class `FindJulia` for searching for the path to a Julia
executable or installing Julia if none is found.
It is meant to be used by other Python projects that need to find a Julia installation.
But, it may have wider uses.


`find_julia` is available on pypi; it may be installed via `pip install find_julia`.
It is meant to be used as a library in other packages.


Several locations are searched for Julia installations, including the default location
used by [`jill.py`](https://github.com/johnnychen94/jill.py). The locations
used by [`juliaup`](https://github.com/JuliaLang/juliaup) are not searched, mostly
because they are not documented anywhere.

### Examples

#### Example 1

```python
julia_path = FindJulia().get_or_install_julia()
```

This searches for and returns a path to a Julia executable in the following
locations, in order: The environment variable `JULIA`.
The standard locations used by the installer `jill.py`.
In a directory in the user `PATH` environment variable.
If no Julia exectuable is found, `jill.py` is used to install Julia (after prompting)
and a path to the exectuable is returned.

#### Example 2

```python
fj = FindJulia(
    preferred_julia_versions = ['1.7', '1.6', '1.5', 'latest'],
    strict_preferred_julia_versions = True,
    confirm_install = False,
    julia_env_var = 'JULIA_EXE',
    other_julia_installations = ['/a/julia/path', '/b/julia/path']
    )

fj.get_or_install_julia(order = ['env', 'other', 'jill', 'path'])
```

This looks for Julia executables in the order specified by `order`. To exclude
a location omit it from the list `order`. Allowed strings are

* `env` -- found at `julia_env_var`
* `other` -- installations found in `other_julia_installations`
* `jill` -- jill installation directory. (e.g. `~/packages/julias/` in Linux)
* `path` -- in the user's `PATH` environment variable

#### Require a specific Julia version

```python
fj = find_julia.FindJulia(preferred_julia_versions = ['1.2'],
               strict_preferred_julia_versions = True)

julia_path = fj.get_or_install_julia(['jill'])
```

This currently only works with jill.py installations.

### Arguments to FindJulia

```python
preferred_julia_versions = ['1.7', '1.6', '1.5', 'latest'],
strict_preferred_julia_versions = False,
version_to_install = None,
confirm_install=False,
julia_env_var = None,
other_julia_installations=None,
post_question_hook=None
```

* `preferred_julia_versions` -- a list of preferred julia versions to search for, in order, in the [`jill.py`](https://github.com/johnnychen94/jill.py)
   installation directory.
*  `strict_preferred_julia_versions` -- if `True` and if no preferred version is found, then no jill.py-installed path is returned.
   Note that the versions at other locations, those specified by `julia_env_var`, `other_julia_installations`, and the user `PATH`, are
   *not* checked.
*  `version_to_install` -- The version requested when installing with `jill.py`. If this is `None`, then the first
    version in `preferred_julia_versions` is used. If the latter is empty, then `latest` is used.
    See `jill.py` for the syntax of this version string.
*  `confirm_install` -- if `False` some questions are asked before installing Julia with jill.py
*  `julia_env_var` -- an environment variable that may be set to the path to a Julia exectuable.
    If `None`, then the default value `JULIA` is used.
*  `other_julia_installations` a string or list of strings specifying paths to Julia installations.
    Note these are not paths to executables. In particular, if `a_path` is an installation path, then
    the executable is expected in `a_path/bin/julia`.
*   `post_question_hook` A callback function to be executed prompting for whether to download and
    install Julia. This callback is executed only if the question is asked. The callback is executed
    after the question is asked, but before any action is taken to download or install. If
    find_julia is part of a larger procedure that requires other interactive input, this parameter
    may be used to ask all questions at once without intervening, time consuming operations.


### Detailed information on search for Julia

To search for Julia installations, do this
```python
fj = FindJulia()
fj.find_julias()
```

The results of searching in each location are recorded in `fj.results`.
The method `fj.results.get_julia_executable(order=['env', 'other', 'jill', 'path'])` then selects
the preferred path.
