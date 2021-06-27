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


def no_gcab_namespace(name, *args):
    """
    Mock gi.require_version() to raise an ValueError to
    simulate that GCab bindings are not available.

    We mock importing the whole 'gi', so that this test
    can be run even when the 'gi' package is not available.
    """
    if name.startswith("gi"):
        m = mock.Mock()
        m.require_version.side_effect = ValueError

        return m
    return orig_import(name, *args)


class TestNoGcab(unittest.TestCase):
    def tearDown(self):
        # make sure we reload 'cab' module after the test,
        # so the true value of 'compression supported'
        # flag is restored, otherwise it will be stuck
        # in 'not supported' mode for subsequent tests
        import symstore.cab
        _reload(symstore.cab)

    @mock.patch(IMPORT_MODULE, side_effect=no_gi_import)
    def test_gi_import_error(self, _):
        """
        test the case when we can't import gi
        """
        import symstore.cab
        _reload(symstore.cab)
        self.assertIsNone(symstore.cab.compress)

    @mock.patch(IMPORT_MODULE, side_effect=no_gcab_namespace)
    def test_no_gcab_namespace(self, _):
        """
        test the case whan gi is available, but Gcab is not
        """
        import symstore.cab
        _reload(symstore.cab)
        self.assertIsNone(symstore.cab.compress)


class TestWinCab(unittest.TestCase):
    def test_import_win(self):
        """
        check that under windows, the 'makecab' implementation
        of cab compression is loaded
        """
        with mock.patch("os.name", "nt"):
            import symstore.cab
            _reload(symstore.cab)

            self.assertEqual(symstore.cab.compress,
                             symstore.cab._compress_makecab)

    @mock.patch("subprocess.run")
    def test_compress_makecab(self, run_mock):
        """
        check that _compress_makecab() invokes 'makecab.exe' with
        expected arguments
        """
        with mock.patch("os.name", "nt"):
            import symstore.cab
            _reload(symstore.cab)

            symstore.cab._compress_makecab("some.pdb", "some.pd_")

        run_mock.assert_called_once_with(
            ["makecab.exe", "/D", "CompressionType=LZX", "/D",
             "CompressionMemory=21", "some.pdb", "some.pd_"],
            check=True, capture_output=True)
