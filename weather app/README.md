# Weather App (CLI)

A feature-rich, beautiful command-line weather application written in Python. It fetches current weather details and forecasts using the free `wttr.in` API and formats the output into stunning, color-coded tables and panels using the `rich` library.

## Features

- **Real-time Weather:** Fetch current conditions, temperature (with automated color-coding), humidity, wind speed, UV index, and observation time.
- **Weather Forecast:** Check a 3-day forecast with daily temperature range, expected conditions, and astronomical details (sunrise/sunset).
- **Favorites Management:** Add, remove, and list favorite locations. Fetch current weather for all favorites at once.
- **Configurable Settings:** Toggle temperature units between Celsius (`C`) and Fahrenheit (`F`).
- **Interactive UI:** Start a responsive menu system directly from the terminal.

---

## Project Structure

```
weather_cli_project/
├── requirements.txt
├── main.py
├── README.md
├── weather_cli/
│   ├── __init__.py
│   ├── cli.py
│   ├── api.py
│   ├── config.py
│   └── formatter.py
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_config.py
```

---

## Setup & Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App:**
   - Launch in **Interactive Menu Mode**:
     ```bash
     python main.py
     ```
   - Get current weather for a city:
     ```bash
     python main.py current London
     ```
   - Get 3-day forecast:
     ```bash
     python main.py forecast Tokyo
     ```
   - Change temperature unit to Fahrenheit:
     ```bash
     python main.py config --unit F
     ```
   - Manage favorites:
     ```bash
     python main.py favorites add "New York"
     python main.py favorites list
     python main.py favorites weather
     ```

---

## Running Tests

To run automated unit tests:
```bash
python -m unittest discover -s tests
```
