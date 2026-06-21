# CLI Expense Tracker

A modular, zero-dependency Command-Line Interface (CLI) Expense Tracker built in Python. This utility helps users organize their daily expenses, maintain a monthly budget, review category-wise statistics via ASCII graphs, and persist data in a structured JSON file.

## Features

- **Robust Expense Management**: Easily add, edit, delete, and list expenses.
- **Auto-Incrementing Referencing**: Assigns simple integer IDs (1, 2, 3...) to expenses, allowing quick and painless referencing during edits and deletions.
- **Dynamic Filtering**: Review expenditures filtered by Category, specific Month (`YYYY-MM`), or a custom Date Range (`YYYY-MM-DD` to `YYYY-MM-DD`).
- **Interactive Monthly Budgeting**: Set a budget limit. A clear, color-coded dashboard is displayed every time you load the app, warning you with status alerts when you are over or approaching budget.
- **Visual Statistics Reporting**: Generates a high-quality terminal summary showing total spent per category alongside an ASCII-rendered bar chart highlighting percentage distribution.
- **Safe JSON Storage**: Saves all records to `expenses.json`. Features automatic recovery backups if the JSON data is corrupted.
- **Premium Term Aesthetics**: Built with ANSI-colored menus, box-drawing layout tables, and clear status emojis.

---

## Directory Structure

```text
expense_tracker/
│
├── README.md             # Setup and feature documentation
├── main.py               # Application entry point & interactive menu loop
├── models.py             # Expense data model & object-level validation logic
├── tracker.py            # ExpenseTracker class (CRUD, stats, filtering, budget calculation)
├── storage.py            # JSON file storage management & corruption backups
├── utils.py              # CLI helper utilities (colors, custom ASCII tables, validations)
└── test_tracker.py       # Comprehensive unit test suite
```

---

## Setup & Running the Application

### Prerequisites
- Python 3.7 or higher installed on your machine.
- No external packages or third-party dependencies are required (e.g. `pip install` is unnecessary).

### Running the App
Navigate to the project root and execute `main.py` using Python:

```powershell
# From the parent directory (workspace root):
python expense_tracker/main.py

# Or navigate inside the folder and run:
cd expense_tracker
python main.py
```

---

## Running Unit Tests
A full suite of unit tests is included in `test_tracker.py`. To execute them:

```powershell
python -m unittest expense_tracker/test_tracker.py
```

---

## How to Use the Application

1. **Add Expense**: The app prompts you for the amount, category (select from predefined ones or type custom names), an optional description, and a date (presses Enter for today's date).
2. **View & Filter Expenses**: Choose to view all records, or filter using categories, months, or date ranges. They are displayed in a clean, auto-sizing terminal border table.
3. **Edit/Delete**: Simply type the ID of the expense you'd like to update or remove.
4. **Set Budget**: Set your desired monthly limit. If the total expenses in the current month exceed this threshold, the home dashboard displays a red warning banner.
5. **Statistics**: Display category distributions as absolute figures, percentage totals, and ASCII visual bars representing proportional budgets.
