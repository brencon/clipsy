"""Content Organizer - Phase 3 of semantic decomposition.

Takes the proposed structure and chunks, uses LLM to write
organized markdown files with proper formatting and images.
"""

import re
import shutil
from pathlib import Path

from .analyzer import FileSpec, StructureProposal
from .extractor import Chunk, ExtractionResult, ImageInfo
from .llm import LLMProvider, get_provider


ORGANIZE_SYSTEM_PROMPT = """You are a technical writer organizing document content into well-structured markdown files.

Your task is to take raw extracted content and transform it into clean, readable markdown.

Guidelines:
1. Preserve all important information from the source content
2. Improve formatting: add proper headings, lists, and structure
3. Convert any tables to proper markdown table format
4. Reference images using the provided image paths
5. Add a metadata comment at the top with source PDF and page numbers
6. Write clear, professional prose
7. Do NOT add information that wasn't in the original content
8. Do NOT omit important details from the source

Output format:
- Start with HTML comment: <!-- Source: {pdf_name} | Pages: {pages} -->
- Add a title as H1
- Organize content with appropriate heading levels
- Include image references where relevant: ![Description](images/filename.png)"""


class ContentOrganizer:
    """Organizes extracted content into semantic markdown files."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        verbose: bool = True,
    ):
        self.provider = provider or get_provider()
        self.verbose = verbose
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def organize(
        self,
        extraction: ExtractionResult,
        proposal: StructureProposal,
        output_dir: Path,
    ) -> Path:
        """Organize content into the proposed structure.

        Args:
            extraction: Original extraction with chunks and images
            proposal: Semantic structure proposal from analyzer
            output_dir: Base directory for output

        Returns:
            Path to the output directory
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        self._log(f"Organizing content into {output_dir}")

        chunk_map = {c.chunk_id: c for c in extraction.chunks}

        for file_spec in proposal.files:
            self._create_file(
                file_spec=file_spec,
                chunk_map=chunk_map,
                extraction=extraction,
                output_dir=output_dir,
            )

        self._create_index(
            proposal=proposal,
            extraction=extraction,
            output_dir=output_dir,
        )

        self._copy_images(extraction, output_dir)

        self._log(
            f"Organization complete. Total tokens: {self.total_input_tokens} in, "
            f"{self.total_output_tokens} out"
        )

        return output_dir

    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[Organizer] {message}")

    def _create_file(
        self,
        file_spec: FileSpec,
        chunk_map: dict[int, Chunk],
        extraction: ExtractionResult,
        output_dir: Path,
    ) -> None:
        """Create a single markdown file from chunks."""
        self._log(f"Creating {file_spec.path}")

        relevant_chunks = [
            chunk_map[cid]
            for cid in file_spec.chunk_ids
            if cid in chunk_map
        ]

        if not relevant_chunks:
            self._log(f"  Warning: No chunks found for {file_spec.path}, skipping")
            return

        combined_content = "\n\n---\n\n".join(
            f"[Chunk {c.chunk_id}, Pages {c.start_page}-{c.end_page}]\n\n{c.content}"
            for c in relevant_chunks
        )

        start_page = min(c.start_page for c in relevant_chunks)
        end_page = max(c.end_page for c in relevant_chunks)

        relevant_images = self._get_relevant_images(
            relevant_chunks, extraction.all_images
        )
        image_info = ""
        if relevant_images:
            image_list = "\n".join(
                f"- {img.file_path.name} (page {img.page_number})"
                for img in relevant_images
            )
            image_info = f"\n\nAvailable images to reference:\n{image_list}"

        file_path = output_dir / file_spec.path
        relative_image_path = self._get_relative_image_path(file_path, output_dir)

        prompt = f"""Create a well-organized markdown file for: {file_spec.title}

Description: {file_spec.description}

Source PDF: {extraction.source_pdf.name}
Pages covered: {start_page}-{end_page}
Image path prefix: {relative_image_path}
{image_info}

Raw content from these pages:

{combined_content}

Transform this into clean, well-structured markdown. Remember to:
1. Start with the metadata comment
2. Add proper headings and structure
3. Reference images where appropriate using the path prefix
4. Preserve all important information"""

        response = self.provider.complete(
            system=ORGANIZE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
        )

        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.content)

    def _get_relevant_images(
        self, chunks: list[Chunk], all_images: list[ImageInfo]
    ) -> list[ImageInfo]:
        """Get images relevant to the given chunks."""
        page_range = set()
        for chunk in chunks:
            for page in range(chunk.start_page, chunk.end_page + 1):
                page_range.add(page)

        return [img for img in all_images if img.page_number in page_range]

    def _get_relative_image_path(self, file_path: Path, output_dir: Path) -> str:
        """Calculate relative path from file to images directory."""
        file_dir = file_path.parent
        images_dir = output_dir / "images"

        try:
            rel_path = Path(images_dir).relative_to(file_dir)
            return str(rel_path)
        except ValueError:
            depth = len(file_path.relative_to(output_dir).parts) - 1
            return "../" * depth + "images"

    def _create_index(
        self,
        proposal: StructureProposal,
        extraction: ExtractionResult,
        output_dir: Path,
    ) -> None:
        """Create the _index.md file with navigation."""
        self._log("Creating _index.md")

        file_list = []
        for file_spec in proposal.files:
            file_list.append(f"- [{file_spec.title}]({file_spec.path})")
            if file_spec.description:
                file_list.append(f"  - {file_spec.description}")

        index_content = f"""<!-- Source: {extraction.source_pdf.name} | Generated by pdf-parser -->

# {extraction.source_pdf.stem}

{proposal.overview}

## Document Information

- **Source**: {extraction.source_pdf.name}
- **Total Pages**: {extraction.total_pages}
- **Images Extracted**: {len(extraction.all_images)}

## Contents

{chr(10).join(file_list)}

---

*This knowledge base was automatically generated from {extraction.source_pdf.name} using semantic decomposition.*
"""

        index_path = output_dir / "_index.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

    def _copy_images(self, extraction: ExtractionResult, output_dir: Path) -> None:
        """Copy extracted images to output directory."""
        if not extraction.all_images:
            return

        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        self._log(f"Copying {len(extraction.all_images)} images")

        for img in extraction.all_images:
            if img.file_path.exists():
                dest = images_dir / img.file_path.name
                shutil.copy2(img.file_path, dest)


def organize_content(
    extraction: ExtractionResult,
    proposal: StructureProposal,
    output_dir: str | Path,
    provider: LLMProvider | None = None,
    verbose: bool = True,
) -> Path:
    """Convenience function to organize extracted content.

    Args:
        extraction: Result from PDFExtractor
        proposal: Structure proposal from SemanticAnalyzer
        output_dir: Where to write the organized content
        provider: Optional LLM provider
        verbose: Whether to print progress

    Returns:
        Path to the output directory
    """
    organizer = ContentOrganizer(provider=provider, verbose=verbose)
    return organizer.organize(extraction, proposal, Path(output_dir))
