import urllib
import json
import julia_semver
from . import _jill
from . import util


_ALL_JULIA_VERSIONS = None
# Pretty heavy, this every release and rc, etc. since the beginning
_JULIA_VERSIONS_URL = 'https://julialang-s3.julialang.org/bin/versions.json'


# From https://github.com/cjdoris/pyjuliapkg
def _all_julia_versions():
    global _ALL_JULIA_VERSIONS
    if _ALL_JULIA_VERSIONS is None:
        url = _JULIA_VERSIONS_URL
        util.log(f'Querying Julia versions from {url}')
        with urllib.request.urlopen(url) as fp:
            _ALL_JULIA_VERSIONS = json.load(fp)
    return _ALL_JULIA_VERSIONS


def _best_version(version_spec=None):
    if version_spec is None:
        version_spec = julia_semver.semver_spec("^1")
    if isinstance(version_spec, str): # else assume it is created by semver_spec
        version_spec = julia_semver.semver_spec(version_spec)
    version_info = _all_julia_versions()
    maxv = julia_semver.version("0.0.0")
    for version in version_info.keys():
        vers = julia_semver.version(version)
        if julia_semver.match(version_spec, vers) and vers > maxv:
            maxv = vers
    if maxv == julia_semver.version("0.0.0"):
        raise Exception(f"No julia version satisfying '{str(version_spec)}' available for download.")
    return maxv


# API of juliaup is not developed enough for this yet
# def install_from_juliaup():

# What should this return ?
def prompt_and_install(
        version_spec=None, answer_yes=False, install_func=None, post_question_hook=None
):
    """
    Download and install julia, optionally prompting, and running a hook after prompting.

    Parameters:
    version_spec - Julia version specification string or object. Default: "^1".
    answer_yes - if `True`, then ask no questions, assume answers are "yes".
    install_func - A function to call that installs julia. The function must accept
        two arguments, `answer_yes`, and `version`. Default : _jill.install_from_jill.
    post_question_hook - a function to run if and after the consumer is asked whether
        to install Julia. This can be used to ask and record more questions rather
        than waiting till after the download. Default: None
    """
    if version_spec is None:
        version_spec = "^1"
    version = str(_best_version(version_spec=version_spec))
    if not answer_yes:
        answer = util.query_yes_no(
            f"Would you like to download and install Julia version '{version}'?"
        )
        if post_question_hook:
            post_question_hook()
        if not answer:
            return False
    if install_func is None:
        install_func = _jill.install_from_jill
    return install_func(answer_yes=answer_yes, version=version)
