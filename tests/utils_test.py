import unittest, sys, argparse
from unittest.mock import patch

from cli.backup_utils import Defaulter, add_args

class TestDefaulter(unittest.TestCase):

    def setUp(self):
        testargs = ["cli", "local"]
        args = None
        with patch.object(sys, "argv", testargs):
            arg_parser = argparse.ArgumentParser(description="CLI tests")
            args = add_args(arg_parser)
        self.defaulter = Defaulter(args)

    def test_set_or_default(self):
        add_date = self.defaulter.set_or_default("add_date")
        temp = self.defaulter.set_or_default("temp")
        date_format = self.defaulter.set_or_default("date_format")
        make_zip = self.defaulter.set_or_default("make_zip")
        over_creds = self.defaulter.set_or_default("over_creds")
        dest_folder = self.defaulter.set_or_default("dest_folder")
        self.assertTrue(add_date)
        self.assertEqual(temp, "temp")
        self.assertEqual(date_format, "&d-&m-&Y")
        self.assertEqual(make_zip, "y")
        self.assertEqual(over_creds, "n")
        self.assertEqual(dest_folder, "PYBCLI")

    # this test relies on the test above
    def test_return_defaults(self):
        defaults = {'add_date': True, 'date_format': '%d-%m-%Y', 'temp': 'temp'}
        obtained = self.defaulter.return_defaults()
        self.assertEqual(obtained, defaults)
