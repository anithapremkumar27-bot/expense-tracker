import unittest
import os
import tempfile
from weather_cli.config import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary file path for config testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, ".weather_config_test.json")
        self.config_manager = ConfigManager(filepath=self.config_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_config(self):
        self.assertEqual(self.config_manager.get_unit(), "C")
        self.assertEqual(self.config_manager.get_favorites(), [])

    def test_set_unit(self):
        self.config_manager.set_unit("F")
        self.assertEqual(self.config_manager.get_unit(), "F")
        
        # Test case-insensitivity
        self.config_manager.set_unit("c")
        self.assertEqual(self.config_manager.get_unit(), "C")

        # Test invalid units
        with self.assertRaises(ValueError):
            self.config_manager.set_unit("K")

    def test_add_favorite(self):
        success, msg = self.config_manager.add_favorite("London")
        self.assertTrue(success)
        self.assertIn("London", self.config_manager.get_favorites())

        # Test adding duplicate (case-insensitive)
        success, msg = self.config_manager.add_favorite("london")
        self.assertFalse(success)
        self.assertEqual(len(self.config_manager.get_favorites()), 1)

        # Test empty city name
        success, msg = self.config_manager.add_favorite("   ")
        self.assertFalse(success)

    def test_remove_favorite(self):
        self.config_manager.add_favorite("Paris")
        self.config_manager.add_favorite("Tokyo")

        success, msg = self.config_manager.remove_favorite("paris")
        self.assertTrue(success)
        self.assertNotIn("Paris", self.config_manager.get_favorites())
        self.assertIn("Tokyo", self.config_manager.get_favorites())

        # Test removing non-existent city
        success, msg = self.config_manager.remove_favorite("New York")
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()
