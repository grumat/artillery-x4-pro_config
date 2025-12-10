
NORMAL = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"

def files_equal(file1_path: str, file2_path: str) -> bool:
	with open(file1_path, 'r', encoding='utf-8') as f1, \
		open(file2_path, 'r', encoding='utf-8') as f2:
		return f1.read() == f2.read()

def expand_tabs(line: str, tab_size: int = 4) -> str:
    """
    Expands tabs in the input string to spaces, respecting tab stops.

    Args:
        line: The input string containing tabs.
        tab_size: The number of columns between tab stops (default: 4).

    Returns:
        The string with tabs replaced by the appropriate number of spaces.
    """
    result = []
    column = 0
    for char in line:
        if char == "\t":
            # Calculate how many spaces are needed to reach the next tab stop
            spaces_needed = tab_size - (column % tab_size)
            result.append(" " * spaces_needed)
            column += spaces_needed
        else:
            result.append(char)
            column += 1
    return "".join(result)
