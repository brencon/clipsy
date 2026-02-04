# Parse PDF into Semantic Knowledge Base

Parse and organize a PDF document: $ARGUMENTS

## Overview

This command transforms large PDF documents into semantically organized markdown knowledge bases that Claude Code can easily read and reference.

## Instructions

1. **Validate the input**: Check that the provided path is a valid PDF file

2. **Check dependencies**: Verify the pdf-parser requirements are installed:
   ```bash
   pip install -r scripts/pdf-parser/requirements.txt
   ```

3. **Check API key**: Verify ANTHROPIC_API_KEY or OPENAI_API_KEY is set in `.env`

4. **Run the parser**:
   ```bash
   python scripts/pdf-parser/parse_pdf.py "$ARGUMENTS"
   ```

   Or with custom output location:
   ```bash
   python scripts/pdf-parser/parse_pdf.py "$ARGUMENTS" --output docs/references/custom-name
   ```

5. **Report results**: After completion, inform the user of:
   - Output location
   - Number of files created
   - How to reference the content in CLAUDE.md

## Options

Pass additional flags after the PDF path:

- `--output PATH` or `-o PATH`: Custom output directory
- `--chunk-size N`: Tokens per chunk (default: 2000, lower for complex docs)
- `--provider anthropic|openai`: LLM provider to use
- `--quiet` or `-q`: Suppress progress output

## Examples

Basic usage:
```
/parse-pdf docs/references/api-spec.pdf
```

Custom output:
```
/parse-pdf technical-manual.pdf --output docs/references/manual
```

Using OpenAI:
```
/parse-pdf document.pdf --provider openai
```

## How It Works

The tool processes PDFs in three phases:

1. **Chunk Extraction**: Splits PDF into ~2000 token chunks, extracts images and tables
2. **Semantic Analysis**: LLM reads chunks sequentially, proposes folder/file structure
3. **Content Organization**: LLM writes organized markdown with proper formatting

## After Parsing

Once parsing completes, you can reference the content in CLAUDE.md:

```markdown
## Additional Context Files

- For API specification, see: @docs/references/api-spec/_index.md
```

Or read specific sections directly during the conversation.
