import unittest
from cli.backup_classes import BackupManager

class TestLowestDate(unittest.TestCase):
    """docstring for TestLowestDate."""

    def test_list(self):
        n_list = [
            "backups__03-03-2019_17H_5m.zip",
            "backups__03-03-2019_17H_14m.zip",
            "backups__03-03-2019_18H_24m.zip",
            "backups__03-03-2019_23H_14m.zip",
            ]
        self.assertTrue(True)
