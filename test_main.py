import pytest
from main import convert_md_to_text

def test_basic_headings():
    md = "# Title\n\n## Sub\n\n### Minor\n\n#### Low\n"
    result = convert_md_to_text(md)
    lines = result.splitlines()
    # Title (level 1)
    assert lines[0] == "Title"
    assert lines[1] == "=" * len("Title")
    # Sub (level 2)
    assert lines[3] == "Sub"
    assert lines[4] == "-" * len("Sub")
    # Minor (level 3)
    assert lines[6] == "Minor"
    assert lines[7] == "~" * len("Minor")
    # Low (level 4)
    assert lines[9] == "Low"
    assert lines[10] == "~" * len("Low")

def test_inline_formatting():
    md = "A **bold** move, *italic* idea, `code` snippet, [link](url), ![img](img.jpg)"
    plain = convert_md_to_text(md)
    assert "bold" in plain
    assert "italic" in plain
    assert "code" in plain
    assert "link" in plain
    assert "img" in plain
    assert "**" not in plain
    assert "*" not in plain
    assert "`" not in plain
    assert "[" not in plain
    assert "]" not in plain
    assert "(" not in plain  # img url removed, link url removed

def test_blockquotes():
    md = "> Quote line\n> Another\nno quote"
    result = convert_md_to_text(md)
    lines = result.splitlines()
    assert lines[0] == "> Quote line"
    assert lines[1] == "> Another"
    assert lines[2] == "no quote"

def test_unordered_lists():
    md = "- First\n- Second\n  - Nested"
    result = convert_md_to_text(md)
    lines = result.splitlines()
    assert lines[0] == "* First"
    assert lines[1] == "* Second"
    assert lines[2] == "  * Nested"

def test_ordered_lists():
    md = "1. Apples\n2. Oranges\n   1. Sub-ordered"
    result = convert_md_to_text(md)
    lines = result.splitlines()
    assert lines[0] == "1. Apples"
    assert lines[1] == "2. Oranges"
    assert lines[2] == "  1. Sub-ordered"  # indent 3 spaces? Let's check logic: for ordered, indent_level = len(indent_spaces)//2, e.g., spaces = "   " -> len=3, //2 = 1, prefix "1. ", then indent = spaces(1*2) = "  " + prefix -> "  1. "? Actually code: ' ' * (indent_level * 2) + prefix, prefix is f'{marker} '. For ordered, indent_spaces = "   " (3 spaces), indent_level = 1, so "  " + "1. " = "  1. ". So output has 2 spaces indent then "1. "? Wait, that's 3 spaces total (2 + "1. "). Let's manually compute: indent_level = 1, so indent_str = ' ' * (1*2) = "  " (2 spaces). Prefix = "1. ". Combined: "  1. "? Actually "  " + "1. " = "  1. " (that's 3 spaces before 1). But in the original, the markdown has "   1. Sub-ordered" (4 spaces indent then 1.). The regex match groups: indent_spaces = "   " (3 leading spaces) because r'^(\s*)([-*+]|\d+\.)\s+(.*)' will capture 3 spaces, then marker "1." then space then "Sub-ordered". So indent_spaces = "   " (len 3), indent_level = 1, output = "  " + "1. Sub-ordered" = "  1. Sub-ordered" (3 spaces then 1.). So indeed output is "  1. Sub-ordered". That's correct.

def test_code_blocks():
    md = "```\nprint('hello')\nmore code\n```\noutside"
    result = convert_md_to_text(md)
    lines = result.splitlines()
    assert lines[0] == "```"
    assert lines[1] == "print('hello')"
    assert lines[2] == "more code"
    assert lines[3] == "```"
    assert lines[4] == "outside"

def test_empty_input():
    assert convert_md_to_text("") == ""
    assert convert_md_to_text("\n\n") == "\n\n"  # two blank lines -> output contains two blank lines? Check: splitlines gives ['', '', ''], each stripped='' -> append '' -> join with newline yields "\n\n". So yes.

def test_nested_lists():
    md = "- A\n  - B\n    1. C\n        - D"
    result = convert_md_to_text(md)
    # Verify indentation
    lines = result.splitlines()
    assert lines[0] == "* A"
    assert lines[1] == "  * B"
    assert lines[2] == "    1. C"  # indent 4 spaces (2*2) for level 2? Actually B indent is 2 spaces (level1). For C: indent_spaces = "    " (4 spaces) => indent_level = 2, output indent = 4 spaces, prefix "1. ", so "    1. C" (4 spaces then "1. " gives 6 characters before C, but the string "    1. C" has 4 spaces, then "1. ", total 7 chars? Let's compute: "    " + "1. " + "C" -> "    1. C". The string "    1. C" has 4 spaces + "1." + space + "C" = 4+2+1+1 = 8? Actually "1." is two chars, then space, then C. So "    1. C" length: 4 spaces, then '1', '.', ' ', 'C' -> 4+4=8. But the assertion string "    1. C" is 4 spaces, then 1, then ., then space, then C. So correct. Then D: indent_spaces = "        " (8 spaces) => indent_level=4, output "        * D". Yes.
    assert lines[3] == "        * D"

def test_regular_paragraph_with_inline():
    md = "This is a **bold** and *em* text with code `x` and [link](url)."
    result = convert_md_to_text(md)
    expected = "This is a bold and em text with code x and link."
    assert result == expected

def test_mixed_blockquote_and_code():
    md = "> Quote with `code`\n\n```\nsome code\n```"
    result = convert_md_to_text(md)
    # Should render blockquote with inline code removal, then code block
    assert "> Quote with code" in result
    assert "```" in result
    assert "some code" in result

def test_code_block_with_inner_backticks():
    # Code block containing a line that looks like the fence (exact same) will close early
    md = "```\nhello\n```\nstill code?\n```\noutside"
    result = convert_md_to_text(md)
    lines = result.splitlines()
    assert lines == ["```", "hello", "```", "still code?", "```", "outside"]

def test_strip_inline_standalone():
    from main import strip_inline
    assert strip_inline("**bold**") == "bold"
    assert strip_inline("__bold__") == "bold"
    assert strip_inline("*italic*") == "italic"
    assert strip_inline("_italic_") == "italic"
    assert strip_inline("`code`") == "code"
    assert strip_inline("[text](url)") == "text"
    assert strip_inline("![img](img.jpg)") == "img"