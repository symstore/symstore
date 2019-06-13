import unittest


class TestCase(unittest.TestCase):
    """
    used to handle the differences between python 2.7 and 3

    the assertion methods assertRaisesRegexp() and
    assertRegexpMatches() are deprecated in python 3,
    but they are missing in python 2.7
    """
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)

        # fall back to deprecated methods on python 2.7
        attrs = dir(self)
        if "assertRaisesRegex" not in attrs:
            self.assertRaisesRegex = self.assertRaisesRegexp

        if "assertRegex" not in attrs:
            self.assertRegex = self.assertRegexpMatches
