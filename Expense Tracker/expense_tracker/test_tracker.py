import unittest
import os
import tempfile
import json
import sys

# Ensure parent directory is in python path to handle running from different directories
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from expense_tracker.models import Expense
from expense_tracker.storage import Storage
from expense_tracker.tracker import ExpenseTracker


class TestExpenseModel(unittest.TestCase):
    """Test validation and structure of Expense class."""

    def test_valid_expense_creation(self):
        exp = Expense(1, 45.50, "food", "Lunch with client", "2026-06-21")
        self.assertEqual(exp.id, 1)
        self.assertEqual(exp.amount, 45.50)
        self.assertEqual(exp.category, "Food")  # Verify capitalization
        self.assertEqual(exp.description, "Lunch with client")
        self.assertEqual(exp.date, "2026-06-21")

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            Expense(1, -5.0, "Food", "Invalid amount", "2026-06-21")
        with self.assertRaises(ValueError):
            Expense(1, 0, "Food", "Invalid amount", "2026-06-21")
        with self.assertRaises(ValueError):
            Expense(1, "not-a-number", "Food", "Invalid amount", "2026-06-21")

    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            Expense(1, 10.0, "", "Empty category", "2026-06-21")
        with self.assertRaises(ValueError):
            Expense(1, 10.0, "   ", "Empty category spacing", "2026-06-21")

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            Expense(1, 10.0, "Food", "Bad date format", "21-06-2026")
        with self.assertRaises(ValueError):
            Expense(1, 10.0, "Food", "Invalid date value", "2026-02-30")
        with self.assertRaises(ValueError):
            Expense(1, 10.0, "Food", "Non-date string", "not-a-date")


class TestStorage(unittest.TestCase):
    """Test storage persistence, safety and reading/writing."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.storage = Storage(self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        if os.path.exists(f"{self.temp_file.name}.corrupted"):
            os.remove(f"{self.temp_file.name}.corrupted")

    def test_default_load_on_empty_file(self):
        # Empty file should load default structure
        expenses, budget = self.storage.load_expenses_and_budget()
        self.assertEqual(expenses, [])
        self.assertEqual(budget, 0.0)

    def test_save_and_load(self):
        expenses = [
            Expense(1, 20.0, "Food", "Dinner", "2026-06-20"),
            Expense(2, 50.0, "Travel", "Fuel", "2026-06-21")
        ]
        budget = 300.0
        success = self.storage.save_expenses_and_budget(expenses, budget)
        self.assertTrue(success)

        loaded_expenses, loaded_budget = self.storage.load_expenses_and_budget()
        self.assertEqual(loaded_budget, 300.0)
        self.assertEqual(len(loaded_expenses), 2)
        self.assertEqual(loaded_expenses[0].amount, 20.0)
        self.assertEqual(loaded_expenses[1].category, "Travel")

    def test_corrupted_file_handling(self):
        # Write corrupted JSON to the file
        with open(self.temp_file.name, "w") as f:
            f.write("{invalid json content}")
        
        expenses, budget = self.storage.load_expenses_and_budget()
        # Verify it handled corruption, loaded default empty list, and created a backup file
        self.assertEqual(expenses, [])
        self.assertEqual(budget, 0.0)
        self.assertTrue(os.path.exists(f"{self.temp_file.name}.corrupted"))


class TestExpenseTracker(unittest.TestCase):
    """Test expense operations: CRUD, filters, statistics and budgets."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.storage = Storage(self.temp_file.name)
        self.tracker = ExpenseTracker(self.storage)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_add_expense(self):
        exp = self.tracker.add_expense(25.50, "Entertainment", "Movie", "2026-06-20")
        self.assertEqual(exp.id, 1)
        self.assertEqual(len(self.tracker.expenses), 1)
        self.assertEqual(self.tracker.expenses[0].amount, 25.50)

        # ID should auto-increment
        exp2 = self.tracker.add_expense(10.0, "Food", "Coffee", "2026-06-21")
        self.assertEqual(exp2.id, 2)
        self.assertEqual(len(self.tracker.expenses), 2)

    def test_delete_expense(self):
        self.tracker.add_expense(25.50, "Entertainment", "Movie", "2026-06-20")
        self.tracker.add_expense(10.0, "Food", "Coffee", "2026-06-21")
        
        success = self.tracker.delete_expense(1)
        self.assertTrue(success)
        self.assertEqual(len(self.tracker.expenses), 1)
        self.assertEqual(self.tracker.expenses[0].id, 2)

        # Deleting non-existent expense should raise ValueError
        with self.assertRaises(ValueError):
            self.tracker.delete_expense(999)

    def test_edit_expense(self):
        self.tracker.add_expense(25.50, "Entertainment", "Movie", "2026-06-20")
        
        # Partially edit
        edited = self.tracker.edit_expense(1, amount=30.0, category="Hobby")
        self.assertEqual(edited.amount, 30.0)
        self.assertEqual(edited.category, "Hobby")
        self.assertEqual(edited.description, "Movie")  # Retained original description
        self.assertEqual(edited.date, "2026-06-20")    # Retained original date

        # Edit non-existent should raise ValueError
        with self.assertRaises(ValueError):
            self.tracker.edit_expense(999, amount=5.0)

    def test_get_filtered_expenses(self):
        self.tracker.add_expense(10.0, "Food", "Coffee", "2026-06-10")
        self.tracker.add_expense(50.0, "Travel", "Fuel", "2026-06-12")
        self.tracker.add_expense(20.0, "Food", "Lunch", "2026-06-15")
        self.tracker.add_expense(15.0, "Entertainment", "Game", "2026-05-20")

        # Category filter
        food_exp = self.tracker.get_filtered_expenses(category="food")
        self.assertEqual(len(food_exp), 2)

        # Month filter (2026-06)
        june_exp = self.tracker.get_filtered_expenses(month="2026-06")
        self.assertEqual(len(june_exp), 3)

        # Month filter (2026-05)
        may_exp = self.tracker.get_filtered_expenses(month="2026-05")
        self.assertEqual(len(may_exp), 1)

        # Date range filter
        ranged_exp = self.tracker.get_filtered_expenses(start_date="2026-06-11", end_date="2026-06-20")
        self.assertEqual(len(ranged_exp), 2)  # Fuel and Lunch
        self.assertEqual(ranged_exp[0].amount, 20.0)  # Chronologically sorted newest first (June 15, then June 12)

    def test_budget_calculations(self):
        self.tracker.set_budget(100.0)
        self.assertEqual(self.tracker.budget_limit, 100.0)

        # Add expenses
        self.tracker.add_expense(60.0, "Food", "Groceries", "2026-06-05")
        self.tracker.add_expense(30.0, "Travel", "Uber", "2026-06-10")

        # Monthly total
        self.assertEqual(self.tracker.get_monthly_total("2026-06"), 90.0)
        self.assertEqual(self.tracker.get_monthly_total("2026-05"), 0.0)

        # Budget status under limit
        status = self.tracker.get_budget_status("2026-06")
        self.assertEqual(status["spent"], 90.0)
        self.assertEqual(status["remaining"], 10.0)
        self.assertEqual(status["percentage"], 90.0)
        self.assertFalse(status["is_exceeded"])

        # Exceed budget limit
        self.tracker.add_expense(20.0, "Entertainment", "Gig", "2026-06-12")
        status_exceeded = self.tracker.get_budget_status("2026-06")
        self.assertEqual(status_exceeded["spent"], 110.0)
        self.assertEqual(status_exceeded["remaining"], -10.0)
        self.assertEqual(status_exceeded["percentage"], 110.0)
        self.assertTrue(status_exceeded["is_exceeded"])

    def test_category_summary(self):
        self.tracker.add_expense(20.0, "Food", "Lunch", "2026-06-05")
        self.tracker.add_expense(30.0, "Food", "Dinner", "2026-06-06")
        self.tracker.add_expense(50.0, "Travel", "Fuel", "2026-06-10")
        
        summary = self.tracker.get_category_summary(month="2026-06")
        # Should be sorted descending by amount: Travel (50.0), Food (50.0)
        self.assertEqual(len(summary), 2)
        self.assertEqual(summary["Travel"], (50.0, 50.0))
        self.assertEqual(summary["Food"], (50.0, 50.0))


if __name__ == "__main__":
    unittest.main()
