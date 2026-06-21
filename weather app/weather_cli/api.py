import requests

class WeatherAPI:
    BASE_URL = "https://wttr.in"

    def fetch_weather_data(self, city: str):
        """
        Fetches the complete weather and forecast JSON from wttr.in.
        """
        city_clean = city.strip()
        if not city_clean:
            return {"success": False, "error": "City name cannot be empty."}

        # Encode the city name for URLs safely
        url = f"{self.BASE_URL}/{requests.utils.quote(city_clean)}"
        params = {"format": "j1"}

        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # wttr.in can sometimes return generic pages or empty arrays for unknown locations
                    if "current_condition" not in data or not data["current_condition"]:
                        return {"success": False, "error": f"City '{city_clean}' not found or invalid response."}
                    return {"success": True, "data": data}
                except ValueError:
                    return {"success": False, "error": "Failed to parse JSON response from wttr.in."}
            elif response.status_code == 404:
                return {"success": False, "error": f"City '{city_clean}' not found."}
            else:
                return {"success": False, "error": f"Weather API returned status code {response.status_code}."}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Connection timed out while fetching weather data."}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
