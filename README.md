# find_julia

This Python package provides functions for searching the file system for the path to a Julia
executable or installing Julia if none is found.
It is meant to be used by other Python projects that need to find a Julia installation.
It also may be used interactively.

## Install

```sh
pip install find_julia`
```

Several locations are searched for Julia installations, including the default locations
used by [`jill.py`](https://github.com/johnnychen94/jill.py) and
by [`juliaup`](https://github.com/JuliaLang/juliaup).


See the docstrings for `find` and `find_or_install` for a description of the parameters.

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
