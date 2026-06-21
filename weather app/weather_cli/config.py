import os
import json

CONFIG_FILENAME = ".weather_config.json"

class ConfigManager:
    def __init__(self, filepath=None):
        if filepath is None:
            home = os.path.expanduser("~")
            self.filepath = os.path.join(home, CONFIG_FILENAME)
        else:
            self.filepath = filepath
        self.config = self._load_default_config()
        self.load()

    def _load_default_config(self):
        return {
            "unit": "C",       # Default to Celsius
            "favorites": []    # List of favorite cities
        }

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge with default config to ensure all keys exist
                    defaults = self._load_default_config()
                    for key, val in defaults.items():
                        if key not in data:
                            data[key] = val
                    self.config = data
            except (json.JSONDecodeError, OSError):
                # Fallback to default config if file is corrupted
                self.config = self._load_default_config()
        else:
            self.config = self._load_default_config()

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except OSError:
            return False

    def get_unit(self):
        return self.config.get("unit", "C")

    def set_unit(self, unit):
        unit = unit.upper()
        if unit not in ["C", "F"]:
            raise ValueError("Unit must be either 'C' or 'F'")
        self.config["unit"] = unit
        return self.save()

    def get_favorites(self):
        return self.config.get("favorites", [])

    def add_favorite(self, city):
        city_clean = city.strip()
        if not city_clean:
            return False, "City name cannot be empty"
        favorites = self.get_favorites()
        # Case insensitive check
        exists = any(c.lower() == city_clean.lower() for c in favorites)
        if exists:
            return False, f"'{city_clean}' is already in favorites."
        favorites.append(city_clean)
        self.config["favorites"] = favorites
        success = self.save()
        if success:
            return True, f"Added '{city_clean}' to favorites."
        return False, "Failed to save configuration."

    def remove_favorite(self, city):
        city_clean = city.strip()
        favorites = self.get_favorites()
        new_favorites = [c for c in favorites if c.lower() != city_clean.lower()]
        if len(favorites) == len(new_favorites):
            return False, f"'{city_clean}' was not found in favorites."
        self.config["favorites"] = new_favorites
        success = self.save()
        if success:
            return True, f"Removed '{city_clean}' from favorites."
        return False, "Failed to save configuration."
