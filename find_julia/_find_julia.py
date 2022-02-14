import os
import sys
import shutil
import logging

import jill.install
import jill.utils

# There is a PR to put the following in jill.py itself. I just have to finish it.
from .jill_install import get_installed_bin_paths


class JuliaResults:
    """
    This class stores the results of the search for Julia installations.

    A method `get_julia_executable` can then be used to select the preferred installation from
    those found.
    """

    def __init__(self):

        self.julia_env_var_set = False
        self.want_julia_env_var = False
        self.julia_env_var_file = None

        self.want_other_julia_installation = False
        self.other_julia_installation = None
        self.exists_other_julia_not_installation = False
        self.other_julia_executable = None

        self.jill_julia_bin_paths = None
        self.preferred_jill_julia_executable = None

        self.julia_executable_in_path = None

        self.want_jill_install = None
        self.new_jill_installed_executable = None


    def get_julia_executable(self, order=None):
        """
        Return the path to the first Julia executable found by checking locations given
        by the list `order`. If no executable is found, return `None`.

        Paramters
        ---------
        order : list
           Specification of the preferred locations for finding julia. Defaults to
           `['env', 'other', 'jill', 'path']`. The meaning of the strings are:
           `env` -- found at `julia_env_var`
           `other` -- installations found in `other_julia_installations`
           `jill` -- jill installation directory. (e.g. `~/packages/julias/` in Linux)
           `path` -- in the user's `PATH` environment variable
        """
        if order is None:
            order = ['env', 'other', 'jill', 'path']

        found_julias = {'env': self.julia_env_var_file,
                        'other': self.other_julia_executable,
                        'jill': self.preferred_jill_julia_executable,
                        'path': self.julia_executable_in_path}
        for location in order:
            julia = found_julias[location]
            if julia:
                return julia
        return None


class FindJulia:
    """
    This class searches for a Julia exectuable and optionally installs Julia if none is found.

    Reasonable defaults are chosen if the constructor is called with no arguments.

    The highest-level method is `get_or_install_julia`, which returns the path to a Julia executable,
    after optionally having installed Julia. If no arguments are given, reasonable defaults are chosen.

    The method `find_julias` searches in various locations and records the results.
    Among the locations searched is the jill.py installation directory,
    and a single, preferred jill.py is recorded. The preferred jill.py installed versions
    are specified in the argument `preferred_julia_versions`.

    The method `find_one_julia` first searches with `find_julias`, then selects and returns
    the path to a preferred julia among all searched locations.


    Parameters
    ----------
    preferred_julia_versions : list
        A list of the preferred jill.py-installed Julia versions with highest preference first.
        The first of these versions that is found will be recorded as the jill.py-installed julia.
        A reasonable default is supplied. But, this code must be updated as new minor Julia versions
        are released. This cannot be done automatically upon importing this module, because it is a slow
        operation.
    strict_preferred_julia_versions : bool
        If `False`, then the first jill.py-installed Julia is returned if none of the preferred versions
        are found. Otherwise no jill.py version is recorded or returned. Default is `False`.
    version_to_install : str
        The Julia version to install if no julia is found. This defaults to the first version in the list
        `preferred_julia_versions`. The format is that specified by the method `jill.install`.
    confirm_install : bool
        If `False`, then prompt the user before installing Julia. Default is `False`.
    julia_env_var : str
        An environment variable containing the possible path to a Julia executable. Defaults to `JULIA`. If a file
        is found at this path, then it is recorded.
    other_julia_installations : [list, str]
        A list of paths representing possible installation directories. When searching, only the first of
        these that is found will be recorded.
    post_question_hook: function
        A callback function to be executed prompting for whether to download and install Julia. This callback is
        executed only if the question is asked. The callback is executed after the question is asked, but before
        any action is taken to download or install. If find_julia is part of a larger procedure that requires other
        interactive input, this parameter may be used to ask all questions at once without intervening, time consuming
        operations.


    Examples
    --------
    Find a path to a Julia executable using defaults.

    julia_path = FindJulia().get_or_install_julia()


    Use only jill.py-installed julias of version 1.5 or 1.4.

    fj = find_julia.FindJulia(preferred_julia_versions = ['1.5, 1.4'],
               strict_preferred_julia_versions = True)

    julia_path = fj.get_or_install_julia(order=['jill'])


    Specify which jill.py versions are allowed, but allow any. Prefer julia specified by an environment variable
    before jill.py installation. Also allow julia on the user PATH variable.

    fj = find_julia.FindJulia(preferred_julia_versions = ['1.7, 1.6'],
               strict_preferred_julia_versions = False)

    julia_path = fj.get_or_install_julia(order=['env', 'jill', 'path'])
    """

    def __init__(self,
                 preferred_julia_versions = None,
                 strict_preferred_julia_versions = False,
                 version_to_install = None,
                 confirm_install=False,
                 julia_env_var=None,
                 other_julia_installations=None,
                 post_question_hook=None,
                 ):
        if preferred_julia_versions is None:
            self.preferred_julia_versions = ['1.7', '1.6', '1.5', 'latest']
        else:
            self.preferred_julia_versions = preferred_julia_versions
        if version_to_install is None:
            if self.preferred_julia_versions:
                self._version_to_install = self.preferred_julia_versions[0]
            else:
                self._version_to_install = 'latest'
        else:
            self._version_to_install = version_to_install
        if julia_env_var is None:
            self._julia_env_var = "JULIA"
        else:
            self._julia_env_var = julia_env_var
        if not isinstance(other_julia_installations, list) and other_julia_installations is not None:
            self._other_julia_installations = [other_julia_installations]
        else:
            self._other_julia_installations = other_julia_installations
        self._confirm_install = confirm_install
        self._strict_preferred_julia_versions = strict_preferred_julia_versions
        self._post_question_hook = post_question_hook
        self.results = JuliaResults()


    def get_preferred_bin_path(self):
        """
        Return the preferred jill-installed `julia`. The first of the preferred versions
        to be found is returned. If no preferred version is found, then the first jill-installed
        version is returned, unless `_strict_preferred_julia_versions` is `True`, in which case,
        `None` is returned.
        """
        self.results.jill_julia_bin_paths = get_installed_bin_paths()
        if not self.results.jill_julia_bin_paths:
            return None
        for pref in self.preferred_julia_versions:
            bin_path = self.results.jill_julia_bin_paths.get(pref)
            if bin_path:
                return bin_path
        if self._strict_preferred_julia_versions:
            return None
        return next(iter(self.results.jill_julia_bin_paths.values())) # Take the first one


    def find_julias(self):
        """
        Search for Julia exectuables in several locations and store the results of the search in
        an instance of `JuliaResults`.
        """
        # Julia executable in environment variable
        if self._julia_env_var:
            self.results.want_julia_env_var = True
            result = os.getenv(self._julia_env_var)
            if result:
                self.results.julia_env_var_set = True
                if os.path.isfile(result):
                    self.results.julia_env_var_file = result
                else:
                    raise FileNotFoundError(f"Executable {self._julia_env_var} = {result} does not exist.")

        # jill-installed julia executables
        self.results.preferred_jill_julia_executable = self.get_preferred_bin_path()

        # julia executable in user path
        self.results.julia_executable_in_path = shutil.which("julia")

        # Other specified julia installation
        if self._other_julia_installations:
            self.results.want_other_julia_installation = True
            for other_julia_installation in self._other_julia_installations:
                if os.path.isdir(other_julia_installation):
                    self.results.other_julia_installation = other_julia_installation
                    julia_path = os.path.join(other_julia_installation, "bin", "julia")
                    if os.path.isfile(julia_path):
                        self.results.other_julia_executable = julia_path
                        break
                elif os.path.exists(other_julia_installation):
                    self.results.exists_other_julia_not_installation = True


    def prompt_and_install_jill_julia(self, not_found=False):
        if (not self._confirm_install) and not_found:
            sys.stdout.write("No julia executable found. ")
        if not self._confirm_install:
            answer = jill.utils.query_yes_no(f"Would you like jill.py to download and install Julia version '{self._version_to_install}'?")
            if self._post_question_hook:
                self._post_question_hook()
        else:
            answer = True
        if answer:
            self.results.want_jill_install = True
            jill.install.install_julia(confirm=True, version=self._version_to_install)
            path = self.get_preferred_bin_path()
            if path is None:
                raise FileNotFoundError("jill.py installation of julia failed")
            self.results.new_jill_installed_executable = path
        else:
            self.results.want_jill_install = False


    def find_one_julia(self, order=None):
        """
        Search for installed julias in various locations and record the result including
        at most one jill.py installation and one from the list `other_julia_installations`.
        Then return one of these paths with preferences specified by `order`.


        Parameters
        ----------
        order : list
            Specification of preferred location for the julia executable. See the method
            `JuliaResults.get_julia_executable`.
        """
        self.find_julias()
        return self.results.get_julia_executable(order=order)


    def get_or_install_julia(self, order=None):
        julia_path = self.find_one_julia(order=order)
        if julia_path:
            return julia_path
        elif not self.results.preferred_jill_julia_executable:
            self.prompt_and_install_jill_julia(not_found=True)
            return self.results.new_jill_installed_executable
