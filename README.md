# ObsidianPrintify

ObsidianPrintify is a command-line tool to convert Obsidian-flavored Markdown files into multi-column HTML files, which can then be easily saved as PDFs using the browser and printed.

This tool handles the following:

1. Stripping YAML frontmatter and Dataview sections.
2. Converting inlined Obsidian links to HTML.
3. Embedding images as base64.
4. Handling LaTeX math with MathJax.
5. Creating a multi-column HTML layout.
6. Saving the HTML file, which can be printed to PDF via the browser.

## Installation

To install ObsidianPrintify, clone this repo and run the command:

```bash
pip install -e .
```

## Usage

Use the `obsprint` command to convert Markdown files:

```bash
obsprint input.md output.html --orientation portrait --columns columns-2
```

### Options

- `input_file`: Path to the input Markdown file.
- `output_file`: Path to the output PDF file.
- `--orientation`: Page orientation (`portrait` or `landscape`). Default is `portrait`.
- `--columns`: Number of columns (`columns-2`, `columns-3`, or `columns-4`). Default is `columns-2`.

## Project Structure

```
obsidian_printify/
├── obsidian_printify
│   ├── __init__.py
│   └── cli.py
└── setup.py
```

