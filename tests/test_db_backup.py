import os
import unittest
import tempfile
from ..app.utils.db_utils import backup_database


class TestBackupDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test.db")
        self.backup_dir = os.path.join(self.test_dir.name, "backup")

        with open(self.db_path, "w") as f:
            f.write("Test database content")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_backup_successful(self):
        backup_path = backup_database(self.db_path, self.backup_dir)
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))

    def test_backup_fails_when_db_missing(self):
        with self.assertRaises(FileNotFoundError):
            backup_database("/non/existing/path.db", self.backup_dir)
