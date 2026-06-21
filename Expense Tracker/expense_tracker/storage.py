import json
import os
import shutil
from typing import List, Dict, Any, Tuple
from expense_tracker.models import Expense

class Storage:
    """Handles JSON file data persistence for expenses and budget configuration."""

    def __init__(self, file_path: str = "expenses.json"):
        self.file_path = file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Ensures that the directory containing the storage file exists."""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load_data(self) -> Dict[str, Any]:
        """Loads data from the JSON file. Returns a default dictionary if file is missing/invalid."""
        default_data = {
            "budget": {
                "monthly_limit": 0.0
            },
            "expenses": []
        }

        if not os.path.exists(self.file_path):
            return default_data

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Basic schema validation
                if not isinstance(data, dict):
                    return default_data
                if "budget" not in data or not isinstance(data["budget"], dict):
                    data["budget"] = default_data["budget"]
                if "expenses" not in data or not isinstance(data["expenses"], list):
                    data["expenses"] = default_data["expenses"]
                
                return data
        except (json.JSONDecodeError, IOError) as e:
            # Corrupted JSON handling: backup the corrupted file and return empty defaults
            backup_path = f"{self.file_path}.corrupted"
            try:
                shutil.copy2(self.file_path, backup_path)
                print(f"\n[Warning] Data file was corrupted. Backed up to '{backup_path}' and initialized a new one.")
            except Exception:
                print(f"\n[Warning] Data file was corrupted and could not be backed up. Initializing a new one.")
            return default_data

    def save_data(self, data: Dict[str, Any]) -> bool:
        """Saves data dict to the JSON file safely."""
        self._ensure_directory_exists()
        temp_file = f"{self.file_path}.tmp"
        try:
            # Write to a temporary file first, then replace to avoid partial writes or loss on crash
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(temp_file, self.file_path)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            print(f"\n[Error] Failed to save data: {e}")
            return False

    def load_expenses_and_budget(self) -> Tuple[List[Expense], float]:
        """Loads and parses the expenses and budget from the file."""
        data = self.load_data()
        
        expenses = []
        corrupted_found = False
        
        for item in data.get("expenses", []):
            try:
                expenses.append(Expense.from_dict(item))
            except Exception:
                corrupted_found = True
        
        if corrupted_found:
            print("\n[Warning] Some expense records were malformed and skipped during load.")
            
        budget_limit = float(data.get("budget", {}).get("monthly_limit", 0.0))
        return expenses, budget_limit

    def save_expenses_and_budget(self, expenses: List[Expense], budget_limit: float) -> bool:
        """Saves expenses and budget back to the JSON file."""
        data = {
            "budget": {
                "monthly_limit": round(float(budget_limit), 2)
            },
            "expenses": [expense.to_dict() for expense in expenses]
        }
        return self.save_data(data)
