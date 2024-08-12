import markdown
import click
import re
import base64
from pathlib import Path

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$']],
        displayMath: [['$$', '$$']]
      }},
      svg: {{
        fontCache: 'global'
      }}
    }};
  </script>
  <script id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    @page {{
      size: A4 {orientation};
      margin: 0.125in;
    }}
    body {{
      text-align: left;
      font-family: Georgia, sans-serif;
      font-size: 8px;
      margin: 0;
      padding: 0;
    }}
    .page {{
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      page-break-after: always;
      column-gap: 0;
      column-fill: auto;
    }}
    .landscape .page {{
      width: 100%;
      height: calc(100% - 1in);
    }}
    .portrait .page {{
      width: 100%;
      height: calc(100% - 1in);
    }}
    .columns-2 {{
      column-count: 2;
    }}
    .columns-3 {{
      column-count: 3;
    }}
    .columns-4 {{
      column-count: 4;
    }}
    p, ul {{
        margin: 0.3em 0;
        padding: 0;
    }}
    h1, h2, h3, h4, h5, h6 {{
      margin: 0.25em 0;
      padding: 0;
    }}
    h1 {{
      font-size: 1.5em;
    }}
    h2 {{
      font-size: 1.25em;
    }}
    h3 {{
      font-size: 1.15em;
    }}
    h4 {{
      font-size: 1.1em;
    }}
    h5 {{
      font-size: 1em;
    }}
    h6 {{
      font-size: 0.9em;
    }}
    ul, ol {{
      margin-left: 10px;
      padding-left: 10px;
    }}
    li {{
      margin: 0;
      padding: 0;
    }}
    img {{
      max-width: 100%;
      height: auto;
    }}
    .section {{
      white-space: pre-wrap;
      background-color: #fff;
      padding: 0.4em;
      border: 1px solid #ddd;
    }}
    .page-break {{
      page-break-before: always;
    }}
    blockquote {{
      border-left: 1px solid #000;
      padding: 0 10px;
      margin: 5px 0;
      font-style: italic;
    }}
    mjx-container[display="true"] {{
       margin: .4em 0 ! important
    }}
  </style>
</head>
<body class="content {orientation} {columns}">
  <div class="page">
    {content}
  </div>
</body>
</html>
"""

def strip_frontmatter(content):
    """Remove YAML frontmatter from the content."""
    return re.sub(r'^---[\s\S]*?---\n', '', content, flags=re.MULTILINE)

def strip_dataview(content):
    """Remove Dataview code sections from the content."""
    return re.sub(r'```dataview[\s\S]*?```', '', content, flags=re.MULTILINE)

def remove_local_file_links(content):
    """Remove local file links from the content."""
    # Remove links of the form [text](#section)
    content = re.sub(r'\[([^\]]+)\]\([^\#\)]+#([^\)]+)\)', r'\2', content)
    # Remove links of the form [text](localfile)
    content = re.sub(r'\[([^\]]+)\]\((?!http|https|ftp|ftps)[^\)]+\)', r'\1', content)
    # Remove links of the form [[#section]]
    content = re.sub(r'\[\[#([^\]]+)\]\]', r'\1', content)
    return content

def process_markdown_file(file_path, base_path):
    """Process the markdown file: strip frontmatter, convert links, embed images, and handle LaTeX."""
    with open(file_path, 'r') as f:
        content = f.read()

    content = strip_frontmatter(content)
    content = strip_dataview(content)
    content = remove_local_file_links(content)
    content = convert_obsidian_links(content, base_path)
    content = embed_images(content, base_path)
    content = convert_section(content)
    content = convert_callouts_and_quotes(content)
    return content

def convert_obsidian_links(content, base_path):
    """Convert Obsidian links to bold or underline and embed linked files."""
    def replace_link(match):
        link_text = match.group(1)
        link_target = match.group(2)
        target_path = base_path / f"{link_target}.md"
        if target_path.exists():
            linked_content = process_markdown_file(target_path, base_path)  # Process linked content
            return f"<b>{link_text}</b><br>{markdown.markdown(linked_content)}"
        return f"<b>{link_text}</b>"

    content = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', replace_link, content)

    # Handle inline documents
    def replace_inline_doc(match):
        link_target = match.group(1)
        if link_target.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
            return match.group(0)  # Return the original string for images
        target_path = base_path / f"{link_target}.md"
        if target_path.exists():
            linked_content = process_markdown_file(target_path, base_path)  # Process linked content
            return markdown.markdown(linked_content)
        return match.group(0)
    content = re.sub(r'\[\[([^\#\]]+)\]\]', replace_inline_doc, content)
    content = re.sub(r'\[\[([^\#\]]+)\#([^\]]+)\]\]', r'\2', content)
    return content

def convert_section(content):
    """Convert sections to HTML with preserved newlines."""
    def replace_section(match):
        section_text = match.group(1)
        return f'<div class="section">{section_text}</div>'
    return re.sub(r'```(?:[^\n]*)\n([\s\S]*?)\n```', replace_section, content)

def embed_images(content, base_path):
    """Embed images as base64 in the HTML content."""
    def replace_image(match):
        image_path = base_path / match.group(1)
        if image_path.exists():
            with open(image_path, 'rb') as img:
                image_data = base64.b64encode(img.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{image_data}" />'
        return match.group(0)
    return re.sub(r'!\[\[([^\]]+)\]\]', replace_image, content)

def convert_callouts_and_quotes(content):
    """Convert callouts and quotes to HTML divs with specific classes."""
    content = re.sub(r'::: callout\n([\s\S]+?)\n:::', r'<div class="callout">\1</div>', content)
    content = re.sub(r'::: quote\n([\s\S]+?)\n:::', r'<div class="quote">\1</div>', content)
    return content

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--orientation', default='portrait', help='Page orientation: portrait or landscape')
@click.option('--columns', default='columns-2', help='Number of columns: columns-2, columns-3, or columns-4')
def convert(input_file, output_file, orientation, columns):
    """Convert Markdown to PDF with specified orientation and columns."""
    base_path = Path(input_file).parent
    md_content = process_markdown_file(input_file, base_path)
    html_content = markdown.markdown(md_content)
    html = TEMPLATE.format(title="Document", orientation=orientation, columns=columns, content=html_content)

    with open(output_file, 'w') as f:
        f.write(html)

if __name__ == '__main__':
    convert()

