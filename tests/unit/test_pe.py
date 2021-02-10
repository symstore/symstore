from os import path
from tests import testcase
from tests.cli import util
from symstore import pe


# expected PE fields values
TIME_DATE_STAMP = 0xE914506E
SIZE_OF_IMAGE = 0xA000


class TestPE(testcase.TestCase):
    def test_fields(self):
        """
        test that we can correctly read TimeDateStamp and SizeOfImage fields
        from a PE file

        in particular, check that large TimeDateStamp are correctly read as
        unsigned integers, and don't become negative values
        """
        # parse the PE file
        pefile = pe.PEFile(path.join(util.SYMFILES_DIR, "u32_test.dll"))

        # check that we got expected values
        self.assertEqual(pefile.TimeDateStamp, TIME_DATE_STAMP)
        self.assertEqual(pefile.SizeOfImage, SIZE_OF_IMAGE)
