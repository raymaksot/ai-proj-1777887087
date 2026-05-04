import sys
import re

def strip_inline(text):
    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    # Remove links
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    return text

def get_underline(char, length):
    return char * length

def convert_md_to_text(md_text):
    lines = md_text.splitlines()
    output = []
    in_code_block = False
    code_fence = ''
    
    for line in lines:
        # Handle fenced code blocks
        if in_code_block:
            if line.strip() == code_fence:
                in_code_block = False
                output.append('```')
            else:
                output.append(line)
            continue
        
        stripped = line.strip()
        if stripped.startswith('```'):
            code_fence = stripped
            in_code_block = True
            output.append('```')
            continue
        
        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = strip_inline(heading_match.group(2))
            if level == 1:
                output.append(text)
                output.append(get_underline('=', len(text)))
            elif level == 2:
                output.append(text)
                output.append(get_underline('-', len(text)))
            else:
                output.append(text)
                output.append(get_underline('~', len(text)))
            continue
        
        # Blank line: preserve
        if stripped == '':
            output.append('')
            continue
        
        # Blockquote
        if line.lstrip().startswith('>'):
            quote_content = stripped[1:]
            if quote_content.startswith(' '):
                quote_content = quote_content[1:]
            quote_content = strip_inline(quote_content)
            output.append('> ' + quote_content)
            continue
        
        # List items
        list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)', line)
        if list_match:
            indent_spaces, marker, rest = list_match.groups()
            indent_level = len(indent_spaces) // 2 if indent_spaces else 0
            if re.match(r'\d+\.', marker):
                prefix = f'{marker} '
            else:
                prefix = '* '
            rest_clean = strip_inline(rest)
            output.append(' ' * (indent_level * 2) + prefix + rest_clean)
            continue
        
        # Regular paragraph line
        cleaned = strip_inline(line)
        output.append(cleaned)
    
    return '\n'.join(output)

def main():
    # Read from stdin if available, else use a sample
    if not sys.stdin.isatty():
        md_text = sys.stdin.read()
    else:
        md_text = (
            "# Title of Document\n\n"
            "Introduction paragraph with **bold** and *italic* text, and a [link](https://example.com).\n\n"
            "## Subheading\n\n"
            "Another paragraph with `inline code`.\n\n"
            "### Third-level heading\n\n"
            "- Unordered item 1\n"
            "- Unordered item 2\n"
            "  - Nested item\n"
            "    1. Ordered inside\n"
            "    2. Second ordered\n"
            "- Unordered item 3\n\n"
            "> Blockquote with *italic*.\n\n"
            "```\n"
            "print('Hello, world!')\n"
            "```\n\n"
            "Plain paragraph after code.\n\n"
            "1. First ordered item\n"
            "2. Second ordered item\n"
            "   with continuation line\n"
            "3. Third\n"
        )
    text = convert_md_to_text(md_text)
    print(text)

if __name__ == '__main__':
    main()