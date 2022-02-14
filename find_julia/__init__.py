"""
Search the file system for the path to a Julia executable or install Julia if none is found.
"""
from .find import find, find_or_install

from ._version import __version__
