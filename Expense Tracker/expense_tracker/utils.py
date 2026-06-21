import datetime
import os
import sys

# Windows console virtual terminal setup to enable ANSI colors
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        # Fallback trick that often initializes ANSI sequences in Windows CMD
        os.system("")

# ANSI Color Codes
CLR_HEADER = "\033[95m"  # Magenta
CLR_BLUE = "\033[94m"    # Blue
CLR_CYAN = "\033[96m"    # Cyan
CLR_GREEN = "\033[92m"   # Green
CLR_YELLOW = "\033[93m"  # Yellow
CLR_RED = "\033[91m"     # Red
CLR_BOLD = "\033[1m"     # Bold
CLR_RESET = "\033[0m"    # Reset

def color_text(text: str, color_code: str) -> str:
    """Wraps text with ANSI color codes."""
    return f"{color_code}{text}{CLR_RESET}"

def safe_char(char: str, fallback: str) -> str:
    """Returns the character if supported by stdout's encoding, otherwise returns the fallback."""
    try:
        encoding = sys.stdout.encoding or 'ascii'
        char.encode(encoding)
        return char
    except Exception:
        return fallback

# Encoding-safe display constants
ICON_SUCCESS = safe_char("✔", "[OK]")
ICON_WARNING = safe_char("⚠", "[WARN]")
ICON_ERROR = safe_char("✖", "[ERROR]")
ICON_STAR = safe_char("★", "***")
CHAR_BLOCK = safe_char("█", "#")
CHAR_EMPTY = safe_char("░", "-")

BOX_TOP_L = safe_char("┌", "+")
BOX_TOP_M = safe_char("┬", "+")
BOX_TOP_R = safe_char("┐", "+")
BOX_MID_L = safe_char("├", "+")
BOX_MID_M = safe_char("┼", "+")
BOX_MID_R = safe_char("┤", "+")
BOX_BOT_L = safe_char("└", "+")
BOX_BOT_M = safe_char("┴", "+")
BOX_BOT_R = safe_char("┘", "+")
BOX_HOR = safe_char("─", "-")
BOX_VER = safe_char("│", "|")

def print_success(text: str):
    """Prints a green success message."""
    print(color_text(f"{ICON_SUCCESS} {text}", CLR_GREEN))

def print_warning(text: str):
    """Prints a yellow warning message."""
    print(color_text(f"{ICON_WARNING} {text}", CLR_YELLOW))

def print_error(text: str):
    """Prints a red error message."""
    print(color_text(f"{ICON_ERROR} {text}", CLR_RED))


def print_banner(title: str):
    """Prints a styled banner title."""
    bar = "=" * (len(title) + 8)
    print(color_text(bar, CLR_CYAN))
    print(color_text(f"==  {title}  ==", CLR_CYAN + CLR_BOLD))
    print(color_text(bar, CLR_CYAN))

def format_currency(amount: float) -> str:
    """Formats amount as currency."""
    return f"${amount:,.2f}"

def validate_date_input(date_str: str) -> str:
    """Validates date format and returns parsed YYYY-MM-DD, raising ValueError if invalid."""
    date_str = date_str.strip()
    if not date_str:
        return datetime.date.today().strftime("%Y-%m-%d")
    try:
        # Try parsing
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date. Must be in YYYY-MM-DD format.")

def validate_amount_input(amount_str: str) -> float:
    """Validates amount input and returns float, raising ValueError if invalid."""
    amount_str = amount_str.strip()
    try:
        amount = float(amount_str)
    except ValueError:
        raise ValueError("Amount must be a number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return round(amount, 2)

def print_table(headers: list, rows: list, alignments: list = None):
    """
    Prints a beautiful, custom ASCII table with border borders.
    - headers: List of column header names
    - rows: List of rows, where each row is a list of cell values
    - alignments: List of 'L' or 'R' representing Left or Right alignment for each column.
                  Defaults to Left alignment.
    """
    if not headers:
        return

    # Convert all cell values to string and clean them up
    str_rows = []
    for row in rows:
        str_rows.append([str(cell) for cell in row])

    # Determine default alignments (Right alignment for amounts/numeric fields if they look like currency or numbers)
    if not alignments:
        alignments = []
        for h in headers:
            h_lower = h.lower()
            if "amount" in h_lower or "budget" in h_lower or "spent" in h_lower or "id" == h_lower:
                alignments.append("R")
            else:
                alignments.append("L")

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    # Box Drawing Characters
    # Top: ┌ ─ ┬ ┐
    # Mid: ├ ─ ┼ ┤
    # Bot: └ ─ ┴ ┘
    # Ver: │
    
    # Generate borders
    top_border = BOX_TOP_L + BOX_TOP_M.join(BOX_HOR * (w + 2) for w in col_widths) + BOX_TOP_R
    mid_border = BOX_MID_L + BOX_MID_M.join(BOX_HOR * (w + 2) for w in col_widths) + BOX_MID_R
    bot_border = BOX_BOT_L + BOX_BOT_M.join(BOX_HOR * (w + 2) for w in col_widths) + BOX_BOT_R

    # Print Table
    # Top border
    print(color_text(top_border, CLR_BLUE))
    
    # Headers
    header_cells = []
    for i, h in enumerate(headers):
        w = col_widths[i]
        align = alignments[i]
        if align == "R":
            header_cells.append(h.rjust(w))
        else:
            header_cells.append(h.ljust(w))
    
    headers_str = color_text(BOX_VER, CLR_BLUE) + " " + (color_text(f" {BOX_VER} ", CLR_BLUE)).join(
        color_text(cell, CLR_CYAN + CLR_BOLD) for cell in header_cells
    ) + " " + color_text(BOX_VER, CLR_BLUE)
    print(headers_str)
    
    # Middle border
    print(color_text(mid_border, CLR_BLUE))
    
    # Rows
    if not str_rows:
        empty_msg = "No records found".center(sum(col_widths) + 3 * (len(col_widths) - 1) + 2)
        print(color_text(BOX_VER, CLR_BLUE) + empty_msg + color_text(BOX_VER, CLR_BLUE))
    else:
        for row in str_rows:
            row_cells = []
            for i, cell in enumerate(row):
                w = col_widths[i]
                align = alignments[i] if i < len(alignments) else "L"
                
                # Check if it is a number or currency to color
                cell_display = cell
                if i < len(headers) and "amount" in headers[i].lower() and cell.startswith("$"):
                    cell_display = color_text(cell, CLR_YELLOW)
                
                if align == "R":
                    padded = cell_display.rjust(w + (len(cell_display) - len(cell)))
                else:
                    padded = cell_display.ljust(w + (len(cell_display) - len(cell)))
                row_cells.append(padded)
                
            row_str = color_text(BOX_VER, CLR_BLUE) + " " + (color_text(f" {BOX_VER} ", CLR_BLUE)).join(row_cells) + " " + color_text(BOX_VER, CLR_BLUE)
            print(row_str)

    # Bottom border
    print(color_text(bot_border, CLR_BLUE))
