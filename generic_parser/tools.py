"""
Utility Tools
-------------

Provides utilities to use in other modules.
"""
import logging
import os
import sys
from contextlib import contextmanager
from io import StringIO

LOG = logging.getLogger(__name__)

_TC = {  # Tree Characters
    '|': u'\u2502',  # Horizontal
    '-': u'\u2500',  # Vertical
    'L': u'\u2514',  # L-Shape
    'S': u'\u251C',  # Split
}


# Additional Dictionary Classes and Functions ##################################


class DotDict(dict):
    """Make dict fields accessible by dot notation."""
    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)
        for key in self:
            if isinstance(self[key], dict):
                self[key] = DotDict(self[key])

    # __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, key):
        """Needed to raise the correct exceptions."""
        try:
            return super(DotDict, self).__getitem__(key)
        except KeyError as e:
            raise AttributeError(e).with_traceback(e.__traceback__) from e

    def get_subdict(self, keys, strict=True):
        """See ``get_subdict``."""
        return DotDict(get_subdict(self, keys, strict))


def print_dict_tree(dictionary, name='Dictionary', print_fun=LOG.info):
    """Prints a dictionary as a tree."""
    def print_tree(tree, level_char):
        for i, key in enumerate(sorted(tree.keys())):
            if i == len(tree) - 1:
                node_char = _TC['L'] + _TC['-']
                level_char_pp = level_char + '   '
            else:
                node_char = _TC['S'] + _TC['-']
                level_char_pp = level_char + _TC['|'] + '  '

            if isinstance(tree[key], dict):
                print_fun(f"{level_char:s}{node_char:s} {str(key):s}")
                print_tree(tree[key], level_char_pp)
            else:
                print_fun(f"{level_char:s}{node_char:s} {str(key):s}: {str(tree[key]):s}")

    print_fun('{:s}:'.format(name))
    print_tree(dictionary, '')


def get_subdict(full_dict, keys, strict=True):
    """
    Returns a sub-dictionary of ``full_dict`` containing only keys of ``keys``.

    Args:
        full_dict: Dictionary to extract from.
        keys: keys to extract.
        strict: If false it ignores keys not in full_dict. Otherwise it crashes on those.
            Defaults to ``True``.

    Returns:
        Extracted sub-dictionary.
    """
    if strict:
        return {k: full_dict[k] for k in keys}
    return {k: full_dict[k] for k in keys if k in full_dict}


# Contexts #####################################################################

@contextmanager
def log_out(stdout=sys.stdout, stderr=sys.stderr):
    """Temporarily changes sys.stdout and sys.stderr."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout
    sys.stderr = stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@contextmanager
def silence():
    """
    Suppress all console output. ``sys.stdout`` and ``sys.stderr`` are rerouted to ``devnull``.
    """
    devnull = open(os.devnull, "w")
    with log_out(stdout=devnull, stderr=devnull):
        try:
            yield
        finally:
            devnull.close()


@contextmanager
def unformatted_console_logging():
    """Log only to console and only unformatted."""

    root_logger = logging.getLogger("")
    old_handlers = list(root_logger.handlers)
    root_logger.handlers = []

    new_handler = logging.StreamHandler(sys.stdout)
    new_handler.setLevel(logging.NOTSET)
    new_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(new_handler)

    yield

    # root_logger.removeHandler(new_handler)
    root_logger.handlers = old_handlers


class TempStringLogger:
    """
    Temporarily log into a string that can be retrieved by ``get_log``.

    Args:
        module: module to log, defaults to the caller file.
        level: logging level, defaults to ``INFO``.
    """
    def __init__(self, module="", level=logging.INFO):
        self.stream = StringIO()
        self.handler = logging.StreamHandler(stream=self.stream)
        self.level = level
        self.log = logging.getLogger(module)

    def __enter__(self):
        self._propagate = self.log.propagate
        self._level = self.log.getEffectiveLevel()
        self.log.propagate = False
        self.log.setLevel(self.level)
        self.log.addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.log.removeHandler(self.handler)
        self.log.propagate = self._propagate
        self.log.setLevel(self._level)

    def get_log(self):
        """ Get the log as string. """
        return self.stream.getvalue()
