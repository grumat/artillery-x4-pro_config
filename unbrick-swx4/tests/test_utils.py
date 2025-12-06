
NORMAL = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"

def files_equal(file1_path: str, file2_path: str) -> bool:
	with open(file1_path, 'r', encoding='utf-8') as f1, \
		open(file2_path, 'r', encoding='utf-8') as f2:
		return f1.read() == f2.read()
