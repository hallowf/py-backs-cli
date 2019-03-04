import unittest, sys, argparse, logging, configparser
from cli.backup_classes import BackupManager
from cli.backup_utils import add_args
from unittest import TestCase, mock, main
from unittest.mock import patch, PropertyMock


class TestBackupManager(unittest.TestCase):
    """docstring for TestLowestDate."""

    def setUp(self):
        # Create args
        testargs = ["cli", "db", "--z_name", "backups"]
        args = None
        with patch.object(sys, "argv", testargs):
            arg_parser = argparse.ArgumentParser(description="CLI tests")
            args = add_args(arg_parser)
        # Create logger
        logging.basicConfig(format="Testing->%(levelname)s : %(message)s",level="DEBUG")
        logger = logging.getLogger("Backup Manager")
        # Add fake configs
        self.f_config1 = {
        "BACKUPS": {
        "backend": "local",
        "make_zip": "y",
        "add_date": "y",
        "over_creds": "n",
        "date_format": "&d-&m-&Y",
        "temp": "temp",
        "client_id": "",
        "dest_folder": "PYBCLI",
        "path_s": "test1.txt\ntest2.txt"
        }
        }
        self.f_config2 = {
            "BACKUPS": {
                "backend": "local",
                "make_zip": "",
                "add_date": "",
                "over_creds": "",
                "date_format": "&d-&m-&Y",
                "temp": "",
                "client_id": "",
                "dest_folder": "Backups",
                "path_s": ""
            }
        }
        # Instantiate BackupManager
        b_manager = BackupManager(args, logger, self.f_config1)
        self.b_manager = b_manager

    def test_init(self):
        z_name = self.b_manager.z_name
        path_s = self.b_manager.path_s
        self.assertEqual("backups.zip", z_name)
        self.assertEqual(["test1.txt", "test2.txt"], path_s)



    def test_set_or_default(self):
        self.b_manager.config = self.f_config2
        add_date = self.b_manager.set_or_default("add_date")
        tmp_dir = self.b_manager.set_or_default("temp")
        date_format = self.b_manager.set_or_default("date_format")
        make_zip = self.b_manager.set_or_default("make_zip")
        over_creds = self.b_manager.set_or_default("over_creds")
        dest_folder = self.b_manager.set_or_default("dest_folder")
        self.assertEqual(False, add_date)
        self.assertEqual("temp", tmp_dir)
        self.assertEqual("&d-&m-&Y", date_format)
        self.assertEqual("y", make_zip)
        self.assertEqual("n", over_creds)
        self.assertEqual("Backups", dest_folder)
        self.b_manager.config = self.f_config1

    def test_check_paths(self):
        print(True)
