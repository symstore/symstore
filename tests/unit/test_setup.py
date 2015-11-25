import mock
import unittest


class TestSetup(unittest.TestCase):
    @mock.patch("setuptools.setup")
    def test_setup(self, setup_mock):
        import setup  # noqa

        setup_mock.assert_called_once_with(name="symstore",
                                           version=mock.ANY,
                                           packages=mock.ANY,
                                           scripts=mock.ANY,
                                           install_requires=mock.ANY,
                                           extras_require=mock.ANY)
