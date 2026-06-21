import argparse
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED
from rich.text import Text

from weather_cli.config import ConfigManager
from weather_cli.api import WeatherAPI
from weather_cli.formatter import WeatherFormatter

class WeatherCLI:
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()
        self.api = WeatherAPI()

    def get_formatter(self):
        return WeatherFormatter(unit=self.config_manager.get_unit())

    def run(self, args_list=None):
        parser = argparse.ArgumentParser(
            description="Beautiful CLI Weather Application",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

        # Current weather command
        current_parser = subparsers.add_parser("current", help="Fetch current weather details for a city")
        current_parser.add_argument("city", type=str, help="Name of the city")

        # Forecast command
        forecast_parser = subparsers.add_parser("forecast", help="Fetch multi-day weather forecast for a city")
        forecast_parser.add_argument("city", type=str, help="Name of the city")

        # Favorites command group
        favorites_parser = subparsers.add_parser("favorites", help="Manage favorite cities")
        fav_subparsers = favorites_parser.add_subparsers(dest="fav_command", help="Favorites subcommands")
        fav_subparsers.add_parser("list", help="List all saved favorite cities")
        add_fav_parser = fav_subparsers.add_parser("add", help="Add a city to favorites")
        add_fav_parser.add_argument("city", type=str, help="City name to add")
        remove_fav_parser = fav_subparsers.add_parser("remove", help="Remove a city from favorites")
        remove_fav_parser.add_argument("city", type=str, help="City name to remove")
        fav_subparsers.add_parser("weather", help="Show current weather for all favorite cities")

        # Config command group
        config_parser = subparsers.add_parser("config", help="View or update application configurations")
        config_parser.add_argument("--show", action="store_true", help="Show current configuration")
        config_parser.add_argument("--unit", type=str, choices=["C", "F", "c", "f"], help="Set temperature unit (C or F)")

        args = parser.parse_args(args_list)

        if not args.command:
            # Launch interactive UI
            self.interactive_loop()
        else:
            self.execute_command(args)

    def execute_command(self, args):
        if args.command == "current":
            self.show_current_weather(args.city)
        elif args.command == "forecast":
            self.show_forecast_weather(args.city)
        elif args.command == "favorites":
            if not args.fav_command or args.fav_command == "list":
                self.list_favorites()
            elif args.fav_command == "add":
                self.add_favorite(args.city)
            elif args.fav_command == "remove":
                self.remove_favorite(args.city)
            elif args.fav_command == "weather":
                self.show_favorites_weather()
        elif args.command == "config":
            if args.unit:
                unit = args.unit.upper()
                try:
                    self.config_manager.set_unit(unit)
                    self.console.print(f"[bold green]Success:[/bold green] Temperature unit updated to {unit}.")
                except ValueError as e:
                    self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
            else:
                self.show_config()

    def show_current_weather(self, city):
        with self.console.status(f"[bold green]Fetching current weather for {city}..."):
            res = self.api.fetch_weather_data(city)
        if res["success"]:
            formatter = self.get_formatter()
            panel = formatter.format_current(res["data"], city)
            self.console.print(panel)
        else:
            self.console.print(f"[bold red]Error:[/bold red] {res['error']}")

    def show_forecast_weather(self, city):
        with self.console.status(f"[bold green]Fetching weather forecast for {city}..."):
            res = self.api.fetch_weather_data(city)
        if res["success"]:
            formatter = self.get_formatter()
            table = formatter.format_forecast(res["data"], city)
            self.console.print(table)
        else:
            self.console.print(f"[bold red]Error:[/bold red] {res['error']}")

    def list_favorites(self):
        favs = self.config_manager.get_favorites()
        if not favs:
            self.console.print("[yellow]You have no favorite cities saved yet.[/yellow]")
            return
        
        table = Table(title="[bold green]Favorite Cities[/bold green]", box=ROUNDED, border_style="green")
        table.add_column("Index", justify="center", style="cyan")
        table.add_column("City Name", style="bold white")
        for i, city in enumerate(favs, 1):
            table.add_row(str(i), city)
        self.console.print(table)

    def add_favorite(self, city):
        success, msg = self.config_manager.add_favorite(city)
        if success:
            self.console.print(f"[bold green]Success:[/bold green] {msg}")
        else:
            self.console.print(f"[bold red]Error:[/bold red] {msg}")

    def remove_favorite(self, city):
        success, msg = self.config_manager.remove_favorite(city)
        if success:
            self.console.print(f"[bold green]Success:[/bold green] {msg}")
        else:
            self.console.print(f"[bold red]Error:[/bold red] {msg}")

    def show_favorites_weather(self):
        favs = self.config_manager.get_favorites()
        if not favs:
            self.console.print("[yellow]You have no favorite cities saved yet.[/yellow]")
            return
        
        table = Table(title="[bold green]Current Weather for Favorites[/bold green]", box=ROUNDED, border_style="green")
        table.add_column("City", style="cyan")
        table.add_column("Temp", justify="center")
        table.add_column("Condition", style="yellow")
        table.add_column("Humidity", justify="center", style="bright_magenta")
        table.add_column("Wind", style="bright_cyan")

        formatter = self.get_formatter()
        errors = []

        with self.console.status("[bold green]Fetching weather for favorite cities..."):
            for city in favs:
                res = self.api.fetch_weather_data(city)
                if res["success"]:
                    data = res["data"]
                    current = data["current_condition"][0]
                    temp_c = float(current.get("temp_C", 0))
                    temp_f = float(current.get("temp_F", 0))
                    
                    if formatter.unit == "C":
                        temp_str = f"{temp_c}°C"
                        temp_color = formatter.get_temp_color(temp_c)
                    else:
                        temp_str = f"{temp_f}°F"
                        temp_color = formatter.get_temp_color((temp_f - 32) * 5 / 9)

                    desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
                    humidity = f"{current.get('humidity', 'N/A')}%"
                    wind_speed = current.get("windspeedKmph", "N/A")
                    wind_dir = current.get("winddir16Point", "N/A")
                    wind_str = f"{wind_speed} km/h ({wind_dir})"

                    table.add_row(
                        city.title(),
                        Text(temp_str, style=temp_color),
                        desc,
                        humidity,
                        wind_str
                    )
                else:
                    errors.append(f"Could not fetch weather for '{city}': {res['error']}")
        
        self.console.print(table)
        for err in errors:
            self.console.print(f"[bold red]Note:[/bold red] {err}")

    def show_config(self):
        unit = self.config_manager.get_unit()
        fav_count = len(self.config_manager.get_favorites())
        
        text = Text()
        text.append("Temperature Unit: ", style="bold white")
        text.append(f"{unit}\n", style="cyan")
        text.append("Saved Favorites: ", style="bold white")
        text.append(f"{fav_count} cities\n", style="cyan")
        text.append("Config Location: ", style="bold white")
        text.append(f"{self.config_manager.filepath}", style="dim white")

        panel = Panel(
            text,
            title="[bold green]Weather CLI Configuration[/bold green]",
            border_style="green",
            box=ROUNDED,
            expand=False
        )
        self.console.print(panel)

    def interactive_loop(self):
        self.console.print(
            Panel(
                "[bold cyan]Welcome to the Beautiful Weather CLI Interactive Mode![/bold cyan]\n"
                "Explore real-time weather details and forecasts in style.",
                title="⛅ [bold yellow]Weather CLI[/bold yellow] ⛅",
                border_style="cyan",
                box=ROUNDED
            )
        )

        while True:
            self.console.print("\n[bold magenta]--- Main Menu ---[/bold magenta]")
            self.console.print("1. Get Current Weather")
            self.console.print("2. Get Weather Forecast")
            self.console.print("3. Manage Favorites")
            self.console.print("4. Settings (Unit System)")
            self.console.print("5. Exit")

            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"], default="1")

            if choice == "1":
                city = Prompt.ask("Enter city name")
                if city.strip():
                    self.show_current_weather(city)
            elif choice == "2":
                city = Prompt.ask("Enter city name")
                if city.strip():
                    self.show_forecast_weather(city)
            elif choice == "3":
                self.interactive_favorites()
            elif choice == "4":
                self.interactive_settings()
            elif choice == "5":
                self.console.print("[bold yellow]Goodbye![/bold yellow] ⛅")
                break

    def interactive_favorites(self):
        while True:
            self.console.print("\n[bold magenta]--- Favorites Menu ---[/bold magenta]")
            self.console.print("1. List Saved Favorites")
            self.console.print("2. Add Favorite City")
            self.console.print("3. Remove Favorite City")
            self.console.print("4. View Current Weather for All Favorites")
            self.console.print("5. Back to Main Menu")

            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"], default="1")

            if choice == "1":
                self.list_favorites()
            elif choice == "2":
                city = Prompt.ask("Enter city name to add")
                if city.strip():
                    self.add_favorite(city)
            elif choice == "3":
                city = Prompt.ask("Enter city name to remove")
                if city.strip():
                    self.remove_favorite(city)
            elif choice == "4":
                self.show_favorites_weather()
            elif choice == "5":
                break

    def interactive_settings(self):
        current_unit = self.config_manager.get_unit()
        self.console.print(f"\n[bold magenta]Current Unit: {current_unit}[/bold magenta]")
        choice = Prompt.ask("Select Temperature Unit", choices=["C", "F"], default="C" if current_unit == "F" else "F")
        try:
            self.config_manager.set_unit(choice)
            self.console.print(f"[bold green]Success:[/bold green] Unit changed to {choice}.")
        except ValueError as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
