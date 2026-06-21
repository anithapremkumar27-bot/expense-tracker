import datetime

class Expense:
    """Represents an individual expense item in the tracker."""

    def __init__(self, expense_id: int, amount: float, category: str, description: str, date_str: str):
        self.id = expense_id
        self.amount = self.validate_amount(amount)
        self.category = self.validate_category(category)
        self.description = self.validate_description(description)
        self.date = self.validate_date(date_str)

    @staticmethod
    def validate_amount(amount: float) -> float:
        """Validates that the expense amount is positive."""
        try:
            val = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a numeric value.")
        if val <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(val, 2)

    @staticmethod
    def validate_category(category: str) -> str:
        """Validates and formats the expense category."""
        if not category or not isinstance(category, str):
            raise ValueError("Category cannot be empty and must be a string.")
        cleaned = category.strip()
        if not cleaned:
            raise ValueError("Category cannot be empty.")
        # Capitalize for visual consistency (e.g., 'food' -> 'Food')
        return cleaned.title()

    @staticmethod
    def validate_description(description: str) -> str:
        """Validates and formats the expense description."""
        if description is None:
            return ""
        if not isinstance(description, str):
            raise ValueError("Description must be a string.")
        return description.strip()

    @staticmethod
    def validate_date(date_str: str) -> str:
        """Validates that the date is in YYYY-MM-DD format and is a valid calendar date."""
        if not date_str or not isinstance(date_str, str):
            raise ValueError("Date cannot be empty and must be a string.")
        
        cleaned_date = date_str.strip()
        try:
            # Parse date to verify format and correctness (e.g. invalid days like Feb 30 are rejected)
            parsed_date = datetime.datetime.strptime(cleaned_date, "%Y-%m-%d").date()
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format (e.g. 2026-06-21).")

    def to_dict(self) -> dict:
        """Serializes the expense object to a dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Expense':
        """Deserializes a dictionary into an Expense object."""
        try:
            return cls(
                expense_id=int(data["id"]),
                amount=float(data["amount"]),
                category=str(data["category"]),
                description=str(data.get("description", "")),
                date_str=str(data["date"])
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid expense record data structure: {e}")

    def __repr__(self) -> str:
        return f"Expense(id={self.id}, amount={self.amount}, category='{self.category}', date='{self.date}')"
