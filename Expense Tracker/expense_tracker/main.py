import datetime
import os
import sys

# Ensure parent directory is in python path to handle running from different directories
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from expense_tracker.models import Expense
from expense_tracker.storage import Storage
from expense_tracker.tracker import ExpenseTracker
from expense_tracker.utils import (
    CLR_HEADER, CLR_BLUE, CLR_CYAN, CLR_GREEN, CLR_YELLOW, CLR_RED, CLR_BOLD, CLR_RESET,
    color_text, print_success, print_warning, print_error, print_banner,
    format_currency, validate_date_input, validate_amount_input, print_table,
    ICON_STAR, CHAR_BLOCK, CHAR_EMPTY
)

DEFAULT_CATEGORIES = ["Food", "Travel", "Utilities", "Entertainment", "Housing", "Others"]

def display_budget_alert(tracker: ExpenseTracker):
    """Displays current month's budget status and warnings if exceeded."""
    current_month = datetime.date.today().strftime("%Y-%m")
    status = tracker.get_budget_status(current_month)
    
    if status["limit"] <= 0:
        return
        
    print("\n" + color_text("--- BUDGET STATUS FOR THIS MONTH ---", CLR_BLUE))
    print(f"Limit:      {format_currency(status['limit'])}")
    print(f"Spent:      {format_currency(status['spent'])}")
    
    if status["is_exceeded"]:
        remaining_str = format_currency(abs(status["remaining"]))
        percent_str = f"{status['percentage']}%"
        print(color_text(f"Status:     OVER BUDGET by {remaining_str} ({percent_str})", CLR_RED + CLR_BOLD))
        print(color_text(f"{ICON_STAR} WARNING: You have exceeded your budget for this month! {ICON_STAR}", CLR_RED + CLR_BOLD))
    else:
        remaining_str = format_currency(status["remaining"])
        percent_str = f"{status['percentage']}%"
        print(color_text(f"Status:     Within Budget. Remaining: {remaining_str} ({percent_str} spent)", CLR_GREEN))
    print(color_text("-" * 36, CLR_BLUE))

def prompt_category() -> str:
    """Prompts the user to select or enter a category."""
    print(f"\nSelect a Category:")
    for idx, cat in enumerate(DEFAULT_CATEGORIES, start=1):
        print(f"  {idx}. {cat}")
    print(f"  {len(DEFAULT_CATEGORIES) + 1}. Enter a custom category")
    
    while True:
        choice = input(color_text("Enter choice (1-7): ", CLR_CYAN)).strip()
        if not choice:
            # Default to Others
            return "Others"
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(DEFAULT_CATEGORIES):
                return DEFAULT_CATEGORIES[choice_num - 1]
            elif choice_num == len(DEFAULT_CATEGORIES) + 1:
                custom = input("Enter custom category name: ").strip()
                if custom:
                    return custom
                print_error("Custom category cannot be empty.")
            else:
                print_error(f"Please enter a number between 1 and {len(DEFAULT_CATEGORIES) + 1}.")
        except ValueError:
            # Treat as custom text category if it's not a number
            return choice

def handle_add_expense(tracker: ExpenseTracker):
    """Handles adding a new expense item."""
    print_banner("ADD NEW EXPENSE")
    
    # 1. Amount
    while True:
        amount_input = input("Enter Amount (e.g. 15.50): ").strip()
        try:
            amount = validate_amount_input(amount_input)
            break
        except ValueError as e:
            print_error(str(e))
            
    # 2. Category
    category = prompt_category()
    
    # 3. Description
    description = input("Enter Description (optional): ").strip()
    
    # 4. Date
    while True:
        date_input = input("Enter Date (YYYY-MM-DD, press Enter for Today): ").strip()
        try:
            date_str = validate_date_input(date_input)
            break
        except ValueError as e:
            print_error(str(e))
            
    try:
        # Add to tracker
        expense = tracker.add_expense(amount, category, description, date_str)
        print_success(f"Expense added successfully! (ID: {expense.id})")
    except ValueError as e:
        print_error(f"Failed to add expense: {e}")

def handle_list_expenses(tracker: ExpenseTracker):
    """Handles listing expenses with optional filtering."""
    print_banner("VIEW / FILTER EXPENSES")
    print("Filter Options:")
    print("  1. View All Expenses")
    print("  2. Filter by Category")
    print("  3. Filter by Month")
    print("  4. Filter by Date Range")
    
    choice = input(color_text("Enter choice (1-4, default 1): ", CLR_CYAN)).strip()
    
    category_filter = None
    month_filter = None
    start_date = None
    end_date = None
    
    try:
        if choice == "2":
            category_filter = input("Enter Category Name: ").strip()
        elif choice == "3":
            month_filter = input("Enter Month (YYYY-MM, e.g. 2026-06): ").strip()
        elif choice == "4":
            start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
            end_date = input("Enter End Date (YYYY-MM-DD): ").strip()
            
        expenses = tracker.get_filtered_expenses(
            category=category_filter,
            month=month_filter,
            start_date=start_date,
            end_date=end_date
        )
        
        # Display results in a table
        headers = ["ID", "Date", "Category", "Description", "Amount"]
        rows = []
        total_amount = 0.0
        for exp in expenses:
            rows.append([
                exp.id,
                exp.date,
                exp.category,
                exp.description if exp.description else "-",
                format_currency(exp.amount)
            ])
            total_amount += exp.amount
            
        print_table(headers, rows)
        print(f"\nTotal Matching Expenses: {color_text(format_currency(total_amount), CLR_YELLOW + CLR_BOLD)} ({len(expenses)} items)")
        
    except ValueError as e:
        print_error(str(e))

def handle_edit_expense(tracker: ExpenseTracker):
    """Handles editing an existing expense."""
    print_banner("EDIT EXPENSE")
    
    id_input = input("Enter Expense ID to edit: ").strip()
    if not id_input:
        return
        
    try:
        expense_id = int(id_input)
    except ValueError:
        print_error("Invalid ID format.")
        return
        
    expense = tracker.get_expense_by_id(expense_id)
    if not expense:
        print_error(f"Expense with ID {expense_id} not found.")
        return
        
    print(f"\nEditing Expense Details (Press Enter to keep current values):")
    print(f"Current Date:        {expense.date}")
    print(f"Current Category:    {expense.category}")
    print(f"Current Description: {expense.description or '-'}")
    print(f"Current Amount:      {format_currency(expense.amount)}")
    print("-" * 40)
    
    # 1. Date
    new_date = None
    while True:
        date_input = input("Enter New Date (YYYY-MM-DD): ").strip()
        if not date_input:
            break
        try:
            new_date = validate_date_input(date_input)
            break
        except ValueError as e:
            print_error(str(e))
            
    # 2. Category
    print("\nChange category?")
    print("  1. Keep current")
    print("  2. Select/Enter new category")
    cat_choice = input("Enter choice (1-2): ").strip()
    new_category = None
    if cat_choice == "2":
        new_category = prompt_category()
        
    # 3. Description
    desc_input = input("Enter New Description: ").strip()
    new_description = desc_input if desc_input else None
    
    # 4. Amount
    new_amount = None
    while True:
        amount_input = input("Enter New Amount: ").strip()
        if not amount_input:
            break
        try:
            new_amount = validate_amount_input(amount_input)
            break
        except ValueError as e:
            print_error(str(e))
            
    try:
        edited = tracker.edit_expense(
            expense_id=expense_id,
            amount=new_amount,
            category=new_category,
            description=new_description,
            date_str=new_date
        )
        print_success(f"Expense {edited.id} updated successfully!")
    except ValueError as e:
        print_error(f"Failed to edit expense: {e}")

def handle_delete_expense(tracker: ExpenseTracker):
    """Handles deleting an expense."""
    print_banner("DELETE EXPENSE")
    
    id_input = input("Enter Expense ID to delete: ").strip()
    if not id_input:
        return
        
    try:
        expense_id = int(id_input)
    except ValueError:
        print_error("Invalid ID format.")
        return
        
    expense = tracker.get_expense_by_id(expense_id)
    if not expense:
        print_error(f"Expense with ID {expense_id} not found.")
        return
        
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete Expense {expense_id} ({format_currency(expense.amount)} for '{expense.category}')? (y/N): ").strip().lower()
    if confirm == "y":
        try:
            tracker.delete_expense(expense_id)
            print_success(f"Expense {expense_id} deleted successfully.")
        except ValueError as e:
            print_error(f"Failed to delete expense: {e}")
    else:
        print_warning("Deletion cancelled.")

def handle_set_budget(tracker: ExpenseTracker):
    """Handles setting the monthly budget limit."""
    print_banner("SET MONTHLY BUDGET")
    print(f"Current Monthly Budget: {format_currency(tracker.budget_limit)}")
    
    budget_input = input("Enter New Monthly Budget (0 to clear): ").strip()
    if not budget_input:
        return
        
    try:
        limit = float(budget_input)
        if limit < 0:
            print_error("Budget limit cannot be negative.")
            return
            
        tracker.set_budget(limit)
        print_success(f"Monthly budget has been updated to {format_currency(limit)}")
    except ValueError:
        print_error("Budget must be a numeric value.")

def handle_category_summary(tracker: ExpenseTracker):
    """Handles printing statistics and category summary tables/charts."""
    print_banner("EXPENSE STATISTICS")
    print("Summary Range:")
    print("  1. All Time Summary")
    print("  2. Monthly Summary")
    
    choice = input("Enter choice (1-2, default 2): ").strip()
    
    month_filter = None
    if choice != "1":
        month_input = input("Enter Month (YYYY-MM, press Enter for current month): ").strip()
        if not month_input:
            month_filter = datetime.date.today().strftime("%Y-%m")
        else:
            month_filter = month_input
            
    try:
        summary = tracker.get_category_summary(month=month_filter)
        
        # Display Table
        title = f"Category Summary for {month_filter}" if month_filter else "All-Time Category Summary"
        print(f"\n{color_text(title, CLR_CYAN + CLR_BOLD)}")
        
        headers = ["Category", "Total Spent", "Percentage"]
        rows = []
        total_spent = 0.0
        for cat, (amt, pct) in summary.items():
            rows.append([
                cat,
                format_currency(amt),
                f"{pct}%"
            ])
            total_spent += amt
            
        print_table(headers, rows)
        print(f"Total spent in selected range: {color_text(format_currency(total_spent), CLR_YELLOW + CLR_BOLD)}\n")
        
        # Progress Bar Chart
        if summary:
            print(color_text("--- Visual Spending Distribution ---", CLR_CYAN))
            for cat, (amt, pct) in summary.items():
                # Generate a premium look bar chart: 20 blocks total
                num_blocks = int(round(pct / 5))
                bar = CHAR_BLOCK * num_blocks + CHAR_EMPTY * (20 - num_blocks)
                print(f"  {cat.ljust(15)} [{color_text(bar, CLR_CYAN)}] {pct:>5}% ({format_currency(amt)})")
            print()
            
    except ValueError as e:
        print_error(str(e))

def main_menu():
    """Main application loop."""
    # Data storage setup
    storage = Storage("expenses.json")
    tracker = ExpenseTracker(storage)
    
    while True:
        print("\n" * 2)
        print_banner("CLI EXPENSE TRACKER")
        display_budget_alert(tracker)
        
        print(f"  1. {color_text('Add Expense', CLR_BOLD)}")
        print(f"  2. View & Filter Expenses")
        print(f"  3. Edit Expense")
        print(f"  4. Delete Expense")
        print(f"  5. Set Monthly Budget")
        print(f"  6. Category Summary & Statistics")
        print(f"  7. {color_text('Exit', CLR_RED)}")
        print("-" * 40)
        
        choice = input(color_text("Select an option (1-7): ", CLR_CYAN)).strip()
        
        if choice == "1":
            handle_add_expense(tracker)
        elif choice == "2":
            handle_list_expenses(tracker)
        elif choice == "3":
            handle_edit_expense(tracker)
        elif choice == "4":
            handle_delete_expense(tracker)
        elif choice == "5":
            handle_set_budget(tracker)
        elif choice == "6":
            handle_category_summary(tracker)
        elif choice == "7":
            print(color_text("\nThank you for using Expense Tracker! Goodbye.\n", CLR_GREEN + CLR_BOLD))
            sys.exit(0)
        else:
            print_error("Invalid option. Please try again.")
            
        input("\nPress Enter to return to the Main Menu...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(color_text("\n\nSession interrupted. Goodbye!", CLR_RED + CLR_BOLD))
        sys.exit(0)
