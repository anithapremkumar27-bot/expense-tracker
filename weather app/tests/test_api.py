import unittest
from unittest.mock import patch, MagicMock
import requests
from weather_cli.api import WeatherAPI

class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        self.api = WeatherAPI()

    def test_fetch_weather_data_empty_city(self):
        res = self.api.fetch_weather_data("   ")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "City name cannot be empty.")

    @patch("requests.get")
    def test_fetch_weather_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_condition": [{"temp_C": "20", "weatherDesc": [{"value": "Sunny"}]}],
            "nearest_area": [{"areaName": [{"value": "London"}]}],
            "weather": []
        }
        mock_get.return_value = mock_response

        res = self.api.fetch_weather_data("London")
        self.assertTrue(res["success"])
        self.assertIn("current_condition", res["data"])
        mock_get.assert_called_once_with("https://wttr.in/London", params={"format": "j1"}, timeout=10)

    @patch("requests.get")
    def test_fetch_weather_data_invalid_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("JSON Decode Error")
        mock_get.return_value = mock_response

        res = self.api.fetch_weather_data("London")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Failed to parse JSON response from wttr.in.")

    @patch("requests.get")
    def test_fetch_weather_data_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        res = self.api.fetch_weather_data("UnknownCity")
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "City 'UnknownCity' not found.")

    @patch("requests.get")
    def test_fetch_weather_data_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        res = self.api.fetch_weather_data("London")
        self.assertFalse(res["success"])
        self.assertIn("timed out", res["error"])

if __name__ == "__main__":
    unittest.main()
