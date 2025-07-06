import ast
import tokenize
import io
from typing import List, Tuple, Set

def minify_python_code(filepath: str, output_filepath: str = None) -> str:
    """
    Minifies a Python source file by removing:
    - All single-line comments (#...)
    - All docstrings (triple-quoted strings at the start of modules, classes, functions)
    - Excess blank lines (reduces multiple blank lines to a single one)

    Args:
        filepath: The path to the input Python file.
        output_filepath: Optional path to save the minified code.
                         If None, the minified code is returned as a string.

    Returns:
        The minified code as a string, if output_filepath is None.
    """
    with open(filepath, 'rt', encoding='utf-8') as f:
        source_code_lines = f.readlines()

    # 1. Identify lines containing docstrings using AST
    docstring_line_ranges: List[Tuple[int, int]] = []
    try:
        tree = ast.parse("".join(source_code_lines))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, (ast.Constant)) # ast.Str for <PY3.8, ast.Constant for >=3.8
                    and isinstance(node.body[0].value.value, str) # Ensure it's a string literal
                ):
                    # AST line numbers are 1-based, convert to 0-based index
                    docstring_start_line_idx = node.body[0].lineno - 1
                    docstring_end_line_idx = node.body[0].end_lineno - 1
                    docstring_line_ranges.append((docstring_start_line_idx, docstring_end_line_idx))
    except SyntaxError as e:
        print(f"Warning: Syntax error in {filepath} at line {e.lineno}, column {e.offset}. Docstring removal might be incomplete. Error: {e.msg}")
        # If AST parsing fails, we can't reliably identify docstrings.
        # Proceed without docstring removal, or raise an error.
        docstring_line_ranges = []


    # 2. Process code line by line using tokenize to remove comments and identify lines to skip
    lines_to_keep: Set[int] = set(range(len(source_code_lines))) # All lines initially
    
    # Store ranges of lines that are part of comments or docstrings to remove
    lines_to_remove_from_comments: Set[int] = set()

    source_code_bytes = "".join(source_code_lines).encode('utf-8')
    try:
        for tok_type, tok_str, (srow, scol), (erow, ecol), line_str in tokenize.tokenize(io.BytesIO(source_code_bytes).readline):
            # Convert 1-based tokenize line numbers to 0-based list indices
            sline_idx = srow - 1
            eline_idx = erow - 1

            if tok_type == tokenize.COMMENT:
                # Mark all lines covered by this comment token for removal
                for i in range(sline_idx, eline_idx + 1):
                    lines_to_remove_from_comments.add(i)

            elif tok_type == tokenize.STRING:
                # Check if this string token is a docstring (within identified AST ranges)
                is_docstring = False
                for ds_start, ds_end in docstring_line_ranges:
                    if ds_start <= sline_idx <= ds_end: # Check if start of string is within a docstring range
                        is_docstring = True
                        break
                
                if is_docstring:
                    # Mark all lines covered by this docstring for removal
                    for i in range(sline_idx, eline_idx + 1):
                        lines_to_remove_from_comments.add(i)

    except tokenize.TokenError as e:
        print(f"Warning: Tokenization error in {filepath} at line {e.lineno}, column {e.offset}. Some comments/docstrings might be missed. Error: {e.msg}")

    # Build the minified code
    minified_lines = []
    previous_line_was_blank_or_removed = True # Used to collapse multiple blank lines

    for i, original_line in enumerate(source_code_lines):
        if i in lines_to_remove_from_comments:
            previous_line_was_blank_or_removed = True
            continue # Skip this line as it's a comment or docstring

        # Remove trailing comments after code (e.g., `x = 10 # comment`)
        # This is safe because tokenize already handled string contents
        cleaned_line = original_line.split('#', 1)[0].rstrip() # split on first #, take left part, rstrip whitespace

        if not cleaned_line.strip(): # Check if line is now effectively blank
            if not previous_line_was_blank_or_removed:
                minified_lines.append("") # Append a single blank line
                previous_line_was_blank_or_removed = True
        else:
            minified_lines.append(cleaned_line)
            previous_line_was_blank_or_removed = False

    minified_code = "\n".join(minified_lines)

    if output_filepath:
        with open(output_filepath, 'wt', encoding='utf-8', newline='\n') as f:
            f.write(minified_code)
        return f"Minified code saved to {output_filepath}"
    else:
        return minified_code


minify_python_code("edit_cfg.py", "edit_cfg_mini.py")
