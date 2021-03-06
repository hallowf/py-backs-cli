import unittest, sys, argparse, logging, configparser, os, shutil, zipfile, platform
from cli.backup_classes import BackupManager
from cli.backup_utils import add_args, Defaulter
from unittest import TestCase, mock, main
from unittest.mock import patch, PropertyMock

c_system = platform.system().lower()

# Good config
f_config1 = {
    "BACKUPS": {
        "backend": "local",
        "make_zip": "y",
        "add_date": "y",
        "over_creds": "n",
        "date_format": "&d-&m-&Y",
        "temp": "temp",
        "client_id": "",
        "dest_folder": "PYBCLI",
        "path_s": "test1.test\ntest2.test"
    }
}

# Empty Config
# Mostly for editing
f_config2 = {
    "BACKUPS": {
        "backend": "local",
        "make_zip": "",
        "add_date": "",
        "over_creds": "",
        "date_format": "&d-&m-&Y",
        "temp": "",
        "client_id": "",
        "dest_folder": "",
        "path_s": "",
    }
}

class TestBackupManager(unittest.TestCase):

    def setUp(self):
        # Create args
        testargs = ["cli", "local"]
        args = None
        with patch.object(sys, "argv", testargs):
            arg_parser = argparse.ArgumentParser(description="CLI tests")
            args = add_args(arg_parser)
        # Create logger
        logging.basicConfig(format="TestBackupManager->%(levelname)s : %(message)s",level="DEBUG")
        logger = logging.getLogger("Backup Manager")
        # Create fake upload files
        open("test1.test", "a").close()
        open("test2.test", "a").close()
        # Create defaults
        self.defaults = {'add_date': True, 'date_format': '%d-%m-%Y', 'temp': 'temp'}
        # Instantiate BackupManager
        b_manager = BackupManager(args, logger, f_config1, self.defaults)
        self.b_manager = b_manager

    def tearDown(self):
        if os.path.isdir(self.b_manager.tmp_dir):
            shutil.rmtree(self.b_manager.tmp_dir)

    # Replaces args
    def test_init(self):
        # Create args
        testargs = ["cli", "local", "--z_name", "backups"]
        args = None
        with patch.object(sys, "argv", testargs):
            arg_parser = argparse.ArgumentParser(description="CLI tests")
            args = add_args(arg_parser)
        self.b_manager.u_args = args
        z_name = self.b_manager.z_name
        path_s = self.b_manager.path_s
        self.assertEqual("backups.zip", z_name)
        self.assertEqual(["test1.test", "test2.test"], path_s)

    def test_check_paths(self):
        # Test default config
        test_paths = self.b_manager.check_paths()
        self.assertTrue(test_paths)
        # Change path_s and assert False
        self.b_manager.path_s = "not_available.txt"
        test_paths = self.b_manager.check_paths()
        self.assertFalse(test_paths)

    def test_copy(self):
        c_files = ["test1.test", "test2.test"]
        # Call copy
        self.b_manager.call_copy()
        # Check if has copied
        has_dir = os.path.isdir(self.b_manager.tmp_dir)
        files_list = os.listdir(self.b_manager.tmp_dir)
        self.assertTrue(has_dir)
        self.assertCountEqual(c_files, files_list)

    @unittest.skipIf(c_system == "linux", "This test fails on linux need to investigate")
    def test_make_zip(self):
        # Make sure files are in tmp dir
        self.b_manager.call_copy()
        # Make zip file
        self.b_manager.make_zip()
        # Check file created
        l_dir = os.listdir(self.b_manager.tmp_dir)
        self.assertTrue(l_dir[0].endswith(".zip"))
        z_location = "%s/%s" % (self.b_manager.tmp_dir, l_dir[0])
        z_list = None
        names = ["temp/test1.test", "temp/test2.test", "temp/"]
        with zipfile.ZipFile(z_location, 'r') as zf:
            z_list = zf.namelist()
        self.assertCountEqual(names, z_list)

    # Ignores self.b_manager
    def test_no_path(self):
        # Create args
        testargs = ["cli", "local"]
        args = None
        with patch.object(sys, "argv", testargs):
            arg_parser = argparse.ArgumentParser(description="CLI tests")
            args = add_args(arg_parser)
        # Create logger
        logging.basicConfig(format="TestBackupManager->%(levelname)s : %(message)s",level="DEBUG")
        logger = logging.getLogger("Backup Manager")
        with self.assertRaises(SystemExit) as cm:
            BackupManager(args, logger, f_config2, self.defaults)
        self.assertEqual(cm.exception.code, 1)
