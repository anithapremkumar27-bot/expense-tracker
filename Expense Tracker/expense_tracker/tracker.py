import datetime
from typing import List, Optional, Dict, Any, Tuple
from expense_tracker.models import Expense
from expense_tracker.storage import Storage

class ExpenseTracker:
    """Core logic to manage CRUD operations, filtering, and budget tracking for expenses."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.expenses: List[Expense] = []
        self.budget_limit: float = 0.0
        self.load_from_storage()

    def load_from_storage(self):
        """Loads expenses and budget limit from the persistent storage."""
        self.expenses, self.budget_limit = self.storage.load_expenses_and_budget()

    def save_to_storage(self) -> bool:
        """Saves current state of expenses and budget limit back to storage."""
        return self.storage.save_expenses_and_budget(self.expenses, self.budget_limit)

    def _generate_next_id(self) -> int:
        """Generates the next sequential integer ID."""
        if not self.expenses:
            return 1
        return max(expense.id for expense in self.expenses) + 1

    def add_expense(self, amount: float, category: str, description: str, date_str: str) -> Expense:
        """
        Creates, validates, and adds a new expense to the tracker.
        Saves changes to storage.
        """
        next_id = self._generate_next_id()
        # The Expense constructor will raise ValueError if validations fail
        new_expense = Expense(next_id, amount, category, description, date_str)
        self.expenses.append(new_expense)
        self.save_to_storage()
        return new_expense

    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """Finds and returns an expense by ID, or None if it doesn't exist."""
        for exp in self.expenses:
            if exp.id == expense_id:
                return exp
        return None

    def edit_expense(self, expense_id: int, amount: Optional[float] = None, 
                     category: Optional[str] = None, description: Optional[str] = None, 
                     date_str: Optional[str] = None) -> Expense:
        """
        Edits an existing expense with new values. Only non-None fields are updated.
        Validates modifications, updates storage, and returns the modified Expense.
        """
        expense = self.get_expense_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense with ID {expense_id} not found.")

        # Validate updates before applying them to prevent partial updates on failure
        new_amount = expense.amount if amount is None else Expense.validate_amount(amount)
        new_category = expense.category if category is None else Expense.validate_category(category)
        new_description = expense.description if description is None else Expense.validate_description(description)
        new_date = expense.date if date_str is None else Expense.validate_date(date_str)

        # Apply updates
        expense.amount = new_amount
        expense.category = new_category
        expense.description = new_description
        expense.date = new_date

        self.save_to_storage()
        return expense

    def delete_expense(self, expense_id: int) -> bool:
        """Deletes an expense by ID. Returns True if deleted successfully, raises ValueError otherwise."""
        expense = self.get_expense_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense with ID {expense_id} not found.")
        
        self.expenses.remove(expense)
        self.save_to_storage()
        return True

    def get_filtered_expenses(self, category: Optional[str] = None, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, 
                              month: Optional[str] = None) -> List[Expense]:
        """
        Retrieves expenses filtered by category, date range, or month.
        - category: case-insensitive category match.
        - start_date / end_date: YYYY-MM-DD format range (inclusive).
        - month: YYYY-MM format.
        """
        filtered = self.expenses

        # 1. Filter by category
        if category:
            cat_clean = category.strip().lower()
            filtered = [exp for exp in filtered if exp.category.lower() == cat_clean]

        # 2. Filter by month (YYYY-MM)
        if month:
            month_clean = month.strip()
            # Basic validation check for YYYY-MM format
            try:
                datetime.datetime.strptime(month_clean, "%Y-%m")
            except ValueError:
                raise ValueError("Month filter must be in YYYY-MM format (e.g. 2026-06).")
            filtered = [exp for exp in filtered if exp.date.startswith(month_clean)]

        # 3. Filter by date range (inclusive)
        if start_date or end_date:
            parsed_start = None
            parsed_end = None
            if start_date:
                try:
                    parsed_start = datetime.datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Start date must be in YYYY-MM-DD format.")
            if end_date:
                try:
                    parsed_end = datetime.datetime.strptime(end_date.strip(), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("End date must be in YYYY-MM-DD format.")

            results = []
            for exp in filtered:
                exp_date = datetime.datetime.strptime(exp.date, "%Y-%m-%d").date()
                if parsed_start and exp_date < parsed_start:
                    continue
                if parsed_end and exp_date > parsed_end:
                    continue
                results.append(exp)
            filtered = results

        # Sort expenses chronologically (newest first for UI listing)
        return sorted(filtered, key=lambda x: x.date, reverse=True)

    def set_budget(self, limit: float) -> float:
        """Sets the monthly budget limit. Raises ValueError if invalid."""
        if limit < 0:
            raise ValueError("Budget limit cannot be negative.")
        self.budget_limit = round(float(limit), 2)
        self.save_to_storage()
        return self.budget_limit

    def get_monthly_total(self, year_month: str) -> float:
        """Calculates the total spent in the given month (format YYYY-MM)."""
        total = 0.0
        for exp in self.expenses:
            if exp.date.startswith(year_month):
                total += exp.amount
        return round(total, 2)

    def get_budget_status(self, year_month: str) -> Dict[str, Any]:
        """
        Returns the budget status for a given month.
        Includes budget limit, spent amount, remaining amount, and alert status.
        """
        total_spent = self.get_monthly_total(year_month)
        remaining = self.budget_limit - total_spent
        percent_spent = (total_spent / self.budget_limit * 100) if self.budget_limit > 0 else 0.0
        
        return {
            "month": year_month,
            "limit": self.budget_limit,
            "spent": total_spent,
            "remaining": round(remaining, 2),
            "percentage": round(percent_spent, 1),
            "is_exceeded": total_spent > self.budget_limit and self.budget_limit > 0
        }

    def get_category_summary(self, month: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
        """
        Summarizes total spent and percentage of total spent per category.
        Returns a dictionary mapping: category -> (total_amount, percentage_of_total_spent)
        - month: Optional YYYY-MM filter.
        """
        expenses_to_sum = self.expenses
        if month:
            expenses_to_sum = [exp for exp in self.expenses if exp.date.startswith(month)]

        total_overall = sum(exp.amount for exp in expenses_to_sum)
        
        summary = {}
        for exp in expenses_to_sum:
            summary[exp.category] = summary.get(exp.category, 0.0) + exp.amount

        # Round sums and calculate percentages
        result = {}
        for cat, amt in summary.items():
            pct = (amt / total_overall * 100) if total_overall > 0 else 0.0
            result[cat] = (round(amt, 2), round(pct, 1))

        # Sort category summary by total amount descending
        return dict(sorted(result.items(), key=lambda x: x[1][0], reverse=True))
