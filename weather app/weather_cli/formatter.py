from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED

class WeatherFormatter:
    def __init__(self, unit: str = "C"):
        self.unit = unit.upper()
        self.console = Console()

    def get_temp_color(self, temp_c: float) -> str:
        if temp_c < 0:
            return "bold bright_blue"
        elif temp_c < 15:
            return "bold cyan"
        elif temp_c < 25:
            return "bold green"
        elif temp_c < 35:
            return "bold yellow"
        else:
            return "bold red"

    def format_current(self, data: dict, city_query: str):
        # Extract location info
        area_info = "Unknown Location"
        if "nearest_area" in data and data["nearest_area"]:
            area = data["nearest_area"][0]
            area_name = area["areaName"][0]["value"] if "areaName" in area else city_query
            country = area["country"][0]["value"] if "country" in area else ""
            region = area["region"][0]["value"] if "region" in area else ""
            parts = [p for p in [area_name, region, country] if p]
            area_info = ", ".join(parts)
        else:
            area_info = city_query.title()

        current = data["current_condition"][0]
        
        # Extract temps
        temp_c = float(current.get("temp_C", 0))
        temp_f = float(current.get("temp_F", 0))
        feels_c = float(current.get("FeelsLikeC", 0))
        feels_f = float(current.get("FeelsLikeF", 0))
        
        if self.unit == "C":
            temp_str = f"{temp_c}°C"
            feels_str = f"{feels_c}°C"
            temp_color = self.get_temp_color(temp_c)
        else:
            temp_str = f"{temp_f}°F"
            feels_str = f"{feels_f}°F"
            temp_color = self.get_temp_color((temp_f - 32) * 5 / 9)  # color based on Celsius equivalent

        desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
        humidity = current.get("humidity", "N/A")
        wind_speed = current.get("windspeedKmph", "N/A")
        wind_dir = current.get("winddir16Point", "N/A")
        uv_index = current.get("uvIndex", "N/A")
        obs_time = current.get("observation_time", "N/A")

        # Build card content
        text = Text()
        text.append(f"Location: ", style="bold white")
        text.append(f"{area_info}\n", style="cyan")
        text.append(f"Condition: ", style="bold white")
        text.append(f"{desc}\n", style="bold yellow")
        text.append(f"Temperature: ", style="bold white")
        text.append(f"{temp_str}\n", style=temp_color)
        text.append(f"Feels Like: ", style="bold white")
        text.append(f"{feels_str}\n", style="italic white")
        text.append(f"Humidity: ", style="bold white")
        text.append(f"{humidity}%\n", style="bright_magenta")
        text.append(f"Wind: ", style="bold white")
        text.append(f"{wind_speed} km/h ({wind_dir})\n", style="bright_cyan")
        text.append(f"UV Index: ", style="bold white")
        text.append(f"{uv_index}\n", style="orange3")
        text.append(f"Observation Time: ", style="bold white")
        text.append(f"{obs_time} (UTC)", style="dim white")

        panel = Panel(
            text,
            title="[bold green]Current Weather[/bold green]",
            border_style="green",
            box=ROUNDED,
            expand=False
        )
        return panel

    def format_forecast(self, data: dict, city_query: str):
        # Header/Location details
        if "nearest_area" in data and data["nearest_area"]:
            area = data["nearest_area"][0]
            area_name = area["areaName"][0]["value"] if "areaName" in area else city_query
            country = area["country"][0]["value"] if "country" in area else ""
            area_info = f"{area_name}, {country}" if country else area_name
        else:
            area_info = city_query.title()

        table = Table(
            title=f"[bold green]3-Day Forecast for {area_info}[/bold green]",
            box=ROUNDED,
            header_style="bold magenta",
            border_style="green"
        )
        
        table.add_column("Date", style="cyan", justify="center")
        table.add_column("Max Temp", justify="center")
        table.add_column("Min Temp", justify="center")
        table.add_column("Condition (Noon)", style="yellow")
        table.add_column("Sunrise", style="orange3", justify="center")
        table.add_column("Sunset", style="orange3", justify="center")

        weather_list = data.get("weather", [])
        for day in weather_list:
            date = day.get("date", "N/A")
            
            # Max/Min temps
            max_c = float(day.get("maxtempC", 0))
            max_f = float(day.get("maxtempF", 0))
            min_c = float(day.get("mintempC", 0))
            min_f = float(day.get("mintempF", 0))

            if self.unit == "C":
                max_str = f"{max_c}°C"
                min_str = f"{min_c}°C"
                max_color = self.get_temp_color(max_c)
                min_color = self.get_temp_color(min_c)
            else:
                max_str = f"{max_f}°F"
                min_str = f"{min_f}°F"
                max_color = self.get_temp_color((max_f - 32) * 5 / 9)
                min_color = self.get_temp_color((min_f - 32) * 5 / 9)

            # Get description from noon (index 4 out of 8 3-hourly blocks, representing 12:00 PM)
            hourly = day.get("hourly", [])
            condition = "N/A"
            if len(hourly) > 4:
                condition = hourly[4].get("weatherDesc", [{}])[0].get("value", "N/A")
            elif len(hourly) > 0:
                condition = hourly[0].get("weatherDesc", [{}])[0].get("value", "N/A")

            # Astronomy
            astronomy = day.get("astronomy", [{}])[0]
            sunrise = astronomy.get("sunrise", "N/A")
            sunset = astronomy.get("sunset", "N/A")

            table.add_row(
                date,
                Text(max_str, style=max_color),
                Text(min_str, style=min_color),
                condition,
                sunrise,
                sunset
            )

        return table
