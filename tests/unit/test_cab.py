import mock
import importlib
import unittest


orig_import = __import__


#
# handle differences between python 2.7 and 3
#

# 'builtins' used to be named '__builtin__' in python 2.7
try:
    import builtins  # noqa
    IMPORT_MODULE = "builtins.__import__"
except ImportError:
    IMPORT_MODULE = "__builtin__.__import__"

# reload() used to be in the root module
if hasattr(importlib, "reload"):
    _reload = importlib.reload
else:
    _reload = reload  # noqa


def no_gi_import(name, *args):
    """
    Mocked import, that emulates that 'gi,*' modules do not exist
    """
    if name.startswith("gi"):
        raise ImportError("test")
    return orig_import(name, *args)


class TestNoGcab(unittest.TestCase):
    """
    test the case when we can't import gi.repository.Gcab
    """
    @mock.patch(IMPORT_MODULE, side_effect=no_gi_import)
    def test_gi_import_error(self, _):
        import symstore.cab
        _reload(symstore.cab)
        self.assertFalse(symstore.cab.compression_supported)
