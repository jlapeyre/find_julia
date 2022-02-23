# find_julia

This Python package provides functions for searching the file system for the path to a Julia
executable or installing Julia if none is found.
It is meant to be used by other Python projects that need to find a Julia installation.
It also may be used interactively.

## Install

```sh
pip install find_julia
```

Several locations are searched for Julia installations, including the default locations
used by [`jill.py`](https://github.com/johnnychen94/jill.py) and
by [`juliaup`](https://github.com/JuliaLang/juliaup).


### Examples

#### Simplest use

Find julia

```python
In [1]: from find_julia import find

In [2]: find()
Out[2]: '/usr/bin/julia'
```

Find or install julia

```python
In [1]: from find_julia import find_or_install

In [2]: find_or_install()
Out[2]: '/usr/bin/julia'
```

### Function `find`

`find(version_spec=None, check_exe=False, find_all=False, strict=False, env_var=None)`

Calling `find()` will use reasonable defaults.

#### Parameters

-  `env_var` : The environment variable to check for a julia path.
        If this variable is set and the exectuable satisfies `version_spec`, then it will be
        preferred to all other paths. Default: "JULIA".
-  `version_spec` : A [Julia compatibility version specification](https://pkgdocs.julialang.org/v1/compatibility/)
        as a str or object. The returned executable must satisfy this specification. Default: "^1".
-  `strict` : If `True` then prerelease (development) versions will be excluded.
-  `check_exe` : If `True` then check that the path is a Julia by querying it for the version.
        Note that this has already been done for most Julias found when the version was extracted.
-  `find_all` : If `False` skip the locations that are slower to search. If no other exectuables
        are found, the slower locations may be searched anyway. The only slow location is the
        jill-installed location.


### Function `find_or_install`

```
find_or_install(version_spec=None, check_exe=False, find_all=False, strict=False,
                    answer_yes=False, post_question_hook=None,
                    env_var=None)
```

Calling `find_or_install()` will use reasonable defaults.

This function takes all the same parameters as does `find` as well as the following.

#### Parameters

-  `answer_yes` - if `True`, then ask no questions, assume answers are "yes".
-  `post_question_hook` -  a function to run if and after the consumer is asked whether
        to install Julia. This can be used to ask and record more questions rather
        than waiting till after the download. Default: None

