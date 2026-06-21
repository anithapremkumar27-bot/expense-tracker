import sys
from weather_cli.cli import WeatherCLI

def main():
    try:
        cli = WeatherCLI()
        cli.run(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
