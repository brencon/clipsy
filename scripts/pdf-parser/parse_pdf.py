#!/usr/bin/env python3
"""PDF Semantic Decomposition Tool.

Transforms large PDFs into semantically organized markdown knowledge bases.

Usage:
    python parse_pdf.py input.pdf
    python parse_pdf.py input.pdf --output docs/references/my-doc
    python parse_pdf.py input.pdf --chunk-size 1500 --provider openai

The tool processes PDFs in three phases:
1. Chunk Extraction - Split PDF into digestible chunks, extract images
2. Semantic Analysis - LLM reads chunks and proposes folder/file structure
3. Content Organization - LLM writes organized markdown with images
"""

import argparse
import shutil
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Transform PDFs into semantically organized markdown knowledge bases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s document.pdf
    %(prog)s spec.pdf --output docs/references/api-spec
    %(prog)s large.pdf --chunk-size 1500 --provider openai

Environment variables:
    ANTHROPIC_API_KEY - Required for Anthropic provider (default)
    OPENAI_API_KEY    - Required for OpenAI provider
        """,
    )

    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the PDF file to process",
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory (default: docs/references/{pdf-name})",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=2000,
        help="Maximum tokens per chunk (default: 2000)",
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Token overlap between chunks (default: 100)",
    )

    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="LLM provider to use (default: anthropic)",
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary extraction directory",
    )

    args = parser.parse_args()

    if not args.pdf_path.exists():
        print(f"Error: PDF not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    if not args.pdf_path.suffix.lower() == ".pdf":
        print(f"Error: File must be a PDF: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_dir = args.output
    else:
        output_dir = Path("docs/references") / args.pdf_path.stem

    verbose = not args.quiet

    if verbose:
        print(f"PDF Semantic Decomposition Tool")
        print(f"================================")
        print(f"Input:  {args.pdf_path}")
        print(f"Output: {output_dir}")
        print()

    try:
        from .extractor import extract_pdf
        from .analyzer import analyze_extraction
        from .organizer import organize_content
        from .llm import get_provider
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from extractor import extract_pdf
        from analyzer import analyze_extraction
        from organizer import organize_content
        from llm import get_provider

    try:
        provider = get_provider(args.provider)
        if verbose:
            print(f"Using LLM provider: {args.provider}")
            print()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print("Phase 1: Extracting content from PDF...")
        print("-" * 40)

    extraction = extract_pdf(
        args.pdf_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    if verbose:
        print(f"  Pages: {extraction.total_pages}")
        print(f"  Chunks: {len(extraction.chunks)}")
        print(f"  Images: {len(extraction.all_images)}")
        print()

    if verbose:
        print("Phase 2: Analyzing content semantically...")
        print("-" * 40)

    proposal = analyze_extraction(
        extraction,
        provider=provider,
        verbose=verbose,
    )

    if verbose:
        print()
        print(f"Proposed structure: {len(proposal.files)} files")
        for f in proposal.files:
            print(f"  - {f.path}")
        print()

    if verbose:
        print("Phase 3: Organizing content into markdown...")
        print("-" * 40)

    final_output = organize_content(
        extraction,
        proposal,
        output_dir,
        provider=provider,
        verbose=verbose,
    )

    if not args.keep_temp and extraction.temp_dir and extraction.temp_dir.exists():
        shutil.rmtree(extraction.temp_dir)

    if verbose:
        print()
        print("=" * 40)
        print(f"Complete! Output: {final_output}")
        print()
        print("Files created:")
        for f in sorted(final_output.rglob("*.md")):
            rel_path = f.relative_to(final_output)
            print(f"  - {rel_path}")

        images_dir = final_output / "images"
        if images_dir.exists():
            image_count = len(list(images_dir.iterdir()))
            print(f"  - images/ ({image_count} files)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
