"""
i working on a md to whatsapp format converter, but iam having some problems, run the file code to se the
tests that it fails them fix it. atention to the lost of breaklines

here the table of convertions that iam following

| Formatting Style | Markdown Syntax | WhatsApp Syntax | Supported by WhatsApp |
| --- | --- | --- | :---: |
| **Bold** | `**text**` or `__text__` | `*text*` | Yes |
| **Italic** | `*text*` or `_text_` | `_text_` | Yes |
| **Strikethrough** | `~~text~~` | `~text~` | Yes |
| **Monospace/Code** | ` ```text``` ` (block) or `` `text` `` (inline) | ` ```text``` ` or `` `text` `` | Yes  |
| **Bulleted List** | `- text` or `* text` | `- text` or `* text` | Yes  |
| **Numbered List** | `1. text` | `1. text` | Yes |
| **Blockquote** | `> text` | `> text` | Yes  |
| **Inline Link** | `[Link Text](https://www.example.com)` | `https://www.example.com` | No (Shows as plain text) |
| **Reference Link** | `[Link Text][1]`<br>`[1]: https://www.example.com` | Not Supported | No |
| **Table** | See syntax below | convert to a perfect aling table | No  |
| **Footnote** | `text[^1]`<br>`[^1]: Footnote text.` | add to the end of the message| No |
| **Task List** | `- [x] Completed task`<br>`- [ ] Incomplete task` | convert to a list | No |
"""

import re


def markdown_to_whatsapp(text):
    """
    Convert Markdown formatting to WhatsApp-compatible syntax with improved handling of:
    - Newlines in block elements
    - Lists and blockquotes
    - Footnotes
    - Tables
    - Code blocks
    """
    # Preserve code blocks and inline code
    code_blocks = []

    def preserve_code(match):
        code_blocks.append(match.group(0))
        return f"__CODE_PLACEHOLDER_{len(code_blocks)-1}__"

    converted_text = re.sub(r"```[\s\S]*?```|`[^`\n]+`", preserve_code, text)

    # Process footnotes (collect definitions and replace markers)
    footnote_defs = {}
    footnote_map = {}
    footnote_counter = 1

    def collect_footnote_def(match):
        key = match.group(1)
        value = match.group(2).strip()
        footnote_defs[key] = value
        return ""

    converted_text = re.sub(
        r"^\[\^([^\]]+)\]:\s*(.*)$",
        collect_footnote_def,
        converted_text,
        flags=re.MULTILINE,
    )

    def replace_footnote_marker(match):
        nonlocal footnote_counter, footnote_map
        key = match.group(1)
        if key in footnote_defs:
            if key not in footnote_map:
                footnote_map[key] = footnote_counter
                footnote_counter += 1
            return f"[{footnote_map[key]}]"
        return ""

    converted_text = re.sub(r"\[\^([^\]]+)\]", replace_footnote_marker, converted_text)

    # Text formatting conversions
    # Strikethrough: ~~text~~ -> ~text~
    converted_text = re.sub(r"~~(.*?)~~", r"~\1~", converted_text)

    # Italic: *text* -> _text_
    converted_text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"_\1_", converted_text)

    # Bold: **text** or __text__ -> *text*
    converted_text = re.sub(r"\*\*(\*?[^*\n]+)\*\*", r"*\1*", converted_text)
    converted_text = re.sub(r"__([^_\n]+)__", r"*\1*", converted_text)

    # Headers: # text -> *text* (bold)
    converted_text = re.sub(
        r"^(\s*)#+\s+(.+)", r"\1*\2*", converted_text, flags=re.MULTILINE
    )

    # Blockquotes: preserve > and maintain newlines
    def convert_blockquotes(match):
        lines = match.group(0).split("\n")
        return "\n".join([line.rstrip() for line in lines]) + "\n\n"

    converted_text = re.sub(
        r"(^>.*\n?)+", convert_blockquotes, converted_text, flags=re.MULTILINE
    )

    # Lists: preserve newlines between items
    def convert_lists(match):
        list_text = match.group(0)
        # Preserve newlines within list
        return re.sub(r"\n{2,}", "\n", list_text)

    converted_text = re.sub(
        r"((^[\s]*[-*+]\s+.*\n?)+)|((^[\s]*\d+\.\s+.*\n?)+)",
        convert_lists,
        converted_text,
        flags=re.MULTILINE,
    )

    # Inline links: [Link Text](URL) -> URL
    converted_text = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", r"\2", converted_text)

    # Images: ![Alt Text](url) -> [Image: Alt Text]
    converted_text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"[Image: \1]", converted_text)

    # Remove horizontal rules
    converted_text = re.sub(
        r"^\s*[-*_]{3,}\s*$", "", converted_text, flags=re.MULTILINE
    )

    # Tables: convert to aligned text
    def convert_table(match):
        table = match.group(0).strip()
        lines = [line.strip() for line in table.split("\n") if line.strip()]

        # Filter out separator lines
        content_lines = [line for line in lines if not re.match(r"^[\s|:-]+$", line)]

        # Format each row
        formatted = []
        for line in content_lines:
            # Split and clean cells
            cells = [cell.strip() for cell in line.split("|") if cell.strip()]
            formatted.append(" | ".join(cells))
        return "\n".join(formatted) + "\n\n"

    converted_text = re.sub(
        r"(^[\s]*\|.*\|[\s]*\n?)+", convert_table, converted_text, flags=re.MULTILINE
    )

    # Task lists: - [x] task -> - task
    converted_text = re.sub(
        r"^(\s*[-*+])\s*\[[ xX]\]\s+", r"\1 ", converted_text, flags=re.MULTILINE
    )

    # Restore preserved code blocks
    for i, code_block in enumerate(code_blocks):
        converted_text = converted_text.replace(f"__CODE_PLACEHOLDER_{i}__", code_block)

    # Clean up whitespace
    converted_text = re.sub(
        r"\n{3,}", "\n\n", converted_text
    )  # Reduce multiple newlines
    converted_text = re.sub(
        r"[ \t]+$", "", converted_text, flags=re.MULTILINE
    )  # Trailing whitespace
    converted_text = converted_text.strip()

    # Append collected footnotes
    if footnote_map:
        footnotes = "\n\nFootnotes:\n"
        for key, num in sorted(footnote_map.items(), key=lambda x: x[1]):
            footnotes += f"[{num}] {footnote_defs[key]}\n"
        converted_text += footnotes

    return converted_text


# --- Comprehensive Test Cases ---
def run_tests():
    """Run comprehensive tests to validate the converter."""
    test_cases = [
        # Basic formatting tests
        {
            "name": "Bold formatting (asterisk)",
            "input": "**Bold text** and **another bold**",
            "expected_contains": ["*Bold text*", "*another bold*"],
        },
        {
            "name": "Bold formatting (underscore)",
            "input": "__Bold text__ and __another bold__",
            "expected_contains": ["*Bold text*", "*another bold*"],
        },
        {
            "name": "Italic formatting (asterisk)",
            "input": "*Italic text* and *another italic*",
            "expected_contains": ["_Italic text_", "_another italic_"],
        },
        {
            "name": "Italic formatting (underscore)",
            "input": "_Italic text_ and _another italic_",
            "expected_contains": ["_Italic text_", "_another italic_"],
        },
        {
            "name": "Mixed bold and italic",
            "input": "**Bold** with *italic* text",
            "expected_contains": ["*Bold*", "_italic_"],
        },
        {
            "name": "Complex mixed formatting",
            "input": "**Bold** and *italic* and __more bold__ and _more italic_",
            "expected_contains": ["*Bold*", "_italic_", "*more bold*", "_more italic_"],
        },
        {
            "name": "Strikethrough",
            "input": "~~strikethrough text~~",
            "expected_contains": ["~strikethrough text~"],
        },
        {
            "name": "Headers to bold",
            "input": "# Header 1\n## Header 2\n### Header 3",
            "expected_contains": ["*Header 1*", "*Header 2*", "*Header 3*"],
        },
        {
            "name": "Links extraction",
            "input": "Visit [Google](https://google.com) for search",
            "expected_contains": ["https://google.com"],
        },
        {
            "name": "Image conversion",
            "input": "![Alt text](image.png)",
            "expected_contains": ["[Image: Alt text]"],
        },
        {
            "name": "Inline code preservation",
            "input": "`inline code` and more text",
            "expected_contains": ["`inline code`"],
        },
        {
            "name": "Code block preservation",
            "input": "```\ncode block\nwith multiple lines\n```",
            "expected_contains": ["```\ncode block\nwith multiple lines\n```"],
        },
        {
            "name": "Mixed code types",
            "input": "`inline code` and ```\ncode block\n```",
            "expected_contains": ["`inline code`", "```\ncode block\n```"],
        },
        {
            "name": "Code with formatting around it",
            "input": "Some **bold** and `code` and *italic*",
            "expected_contains": ["*bold*", "`code`", "_italic_"],
        },
        # Edge cases
        {
            "name": "Empty bold/italic",
            "input": "**bold** and ** ** and *italic* and * *",
            "expected_contains": ["*bold*", "*italic*"],
        },
        {
            "name": "Nested formatting attempt",
            "input": "**bold *and italic* together**",
            "expected_contains": ["*bold _and italic_ together*"],
        },
        {
            "name": "Adjacent formatting",
            "input": "**bold***italic**more bold**",
            "expected_contains": ["*bold*", "_italic_", "*more bold*"],
        },
        {
            "name": "Formatting in headers",
            "input": "# Header with **bold** and *italic*",
            "expected_contains": ["*Header with *bold* and _italic_*"],
        },
        {
            "name": "Code in formatting",
            "input": "**bold with `code` inside** and *italic with `code`*",
            "expected_contains": ["*bold with `code` inside*", "_italic with `code`_"],
        },
        {
            "name": "Multiple consecutive formatting",
            "input": "**bold1** **bold2** *italic1* *italic2*",
            "expected_contains": ["*bold1*", "*bold2*", "_italic1_", "_italic2_"],
        },
        # Original test cases from your example
        {
            "name": "Basic mixed",
            "input": "**Bold text** and *italic text*",
            "expected_contains": ["*Bold text*", "_italic text_"],
        },
        {
            "name": "Underscore variations",
            "input": "__Another bold__ and _another italic_",
            "expected_contains": ["*Another bold*", "_another italic_"],
        },
        {
            "name": "Complex mixed with code and strike",
            "input": "**Bold** with *italic* and ~~strikethrough~~ and `code`",
            "expected_contains": ["*Bold*", "_italic_", "~strikethrough~", "`code`"],
        },
        {
            "name": "List with formatting",
            "input": "List with formatting:\n* **Bold item**\n* *Italic item*\n* `Code item`",
            "expected_contains": ["*Bold item*", "_Italic item_", "`Code item`"],
        },
        {
            "name": "Complex document structure",
            "input": "# Header\n\nSome **bold** and *italic* text.\n\n> Quote here\n\n* List item 1\n* List item 2\n\n```\ncode block\n```",
            "expected_contains": [
                "*Header*",
                "*bold*",
                "_italic_",
                "```\ncode block\n```",
            ],
        },
    ]

    print("=== RUNNING COMPREHENSIVE VALIDATION TESTS ===\n")

    passed_tests = 0
    for i, test in enumerate(test_cases, 1):
        result = markdown_to_whatsapp(test["input"])
        passed = all(expected in result for expected in test["expected_contains"])

        if passed:
            passed_tests += 1

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{i:2d}. {test['name']}: {status}")
        # if not passed:
        print(f"     Input:    {repr(test['input'])}")
        print(f"     Output:   {repr(result)}")
        print(f"     Expected: {test['expected_contains']}")
        missing = [exp for exp in test["expected_contains"] if exp not in result]
        print(f"     Missing:  {missing}")
        print()

    print(
        f"=== TEST SUMMARY: {passed_tests}/{len(test_cases)} PASSED ({passed_tests/len(test_cases)*100:.1f}%) ===\n"
    )


# --- Example Usage ---
advanced_markdown = """
### Report Summary

This is a test of the advanced converter. It includes **bold**, *italic*, and ~~strikethrough~~.

---

Here is a table of our quarterly results:

| Month    | Revenue | Expenses | Profit |
|----------|---------|----------|--------|
| January  | 10,000  | 8,000    | 2,000  |
| February | 12,000  | 9,000    | 3,000  |
| March    | 15,000  | 10,000   | 5,000  |

Please review this data. Here is an important image: ![Company Logo](logo.png).

#### Action Items
- [x] Review the report.
- [ ] Prepare feedback for the team.

The main conclusion[^1] is that we are growing steadily. More details can be found on our [official website](https://example.com).

[^1]: Based on Q1 2024 data.
"""


def demo_conversion():
    """Demonstrate the conversion with various markdown examples."""
    print("--- Advanced Example ---")
    whatsapp_output = markdown_to_whatsapp(advanced_markdown)
    print(whatsapp_output)
    print("\n" + "=" * 50 + "\n")


def demo_unit_tests():
    """Run the original unit test cases."""
    test_cases = [
        # Basic formatting
        "**Bold text** and *italic text*",
        "__Another bold__ and _another italic_",
        "~~Strikethrough text~~",
        "`inline code`",
        # Code blocks
        "```\ncode block\nwith multiple lines\n```",
        "```python\ndef hello():\n    print('world')\n```",
        # Headers
        "# Main Header",
        "## Sub Header",
        "### Small Header",
        # Lists
        "* First item\n* Second item\n* Third item",
        "- Another list\n- With dashes\n- Multiple items",
        "1. Numbered list\n2. Second item\n3. Third item",
        # Quotes
        "> This is a quote\n> Multiple lines\n> In the quote",
        # Mixed formatting
        "**Bold** with *italic* and ~~strikethrough~~ and `code`",
        "List with formatting:\n* **Bold item**\n* *Italic item*\n* `Code item`",
        # Complex examples
        "# Header\n\nSome **bold** and *italic* text.\n\n> Quote here\n\n* List item 1\n* List item 2\n\n```\ncode block\n```",
    ]

    print("--- Original Unit Test Cases ---")
    for i, test in enumerate(test_cases, 1):
        converted = markdown_to_whatsapp(test)
        print(f"{i:2d}. Original: {repr(test)}")
        print(f"    Result:   {repr(converted)}")
        print(f"    Display:\n{converted}")
        print("-" * 50)


if __name__ == "__main__":
    # Run validation tests first
    run_tests()

    # Then run the demo
    demo_conversion()

    # Optionally run original unit tests
    # demo_unit_tests()
