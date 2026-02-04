"""Semantic Analyzer - Phase 2 of semantic decomposition.

Feeds chunks sequentially to an LLM to build understanding
and propose a semantic folder/file structure.
"""

import json
from dataclasses import dataclass

from .extractor import Chunk, ExtractionResult
from .llm import LLMProvider, get_provider


@dataclass
class FileSpec:
    """Specification for an output file."""

    path: str  # Relative path like "01-introduction/overview.md"
    title: str
    description: str
    chunk_ids: list[int]  # Which chunks contain relevant content


@dataclass
class StructureProposal:
    """Proposed folder/file structure for the document."""

    overview: str
    files: list[FileSpec]
    raw_json: dict


ANALYSIS_SYSTEM_PROMPT = """You are a document analyst. Your task is to read document chunks
and build a comprehensive understanding of the document's structure and content.

As you read each chunk, update your mental model of:
1. The main topics and themes
2. How information is organized
3. Key sections and their relationships
4. Important concepts and terminology

After reading all chunks, you will propose a logical folder/file structure."""


STRUCTURE_SYSTEM_PROMPT = """You are a document organizer. Based on your analysis of the document,
propose a semantic folder and file structure that organizes the content logically.

Requirements:
1. Create numbered top-level folders for major topics (e.g., "01-introduction", "02-authentication")
2. Within each folder, create markdown files for specific subtopics
3. Use kebab-case for all folder and file names
4. File names should be descriptive but concise
5. Each file should cover a focused, coherent topic
6. Maintain logical information flow (introduction before details, etc.)

Return your response as a JSON object with this structure:
{
    "overview": "Brief description of the document and its main purpose",
    "structure": [
        {
            "path": "01-introduction/overview.md",
            "title": "Introduction and Overview",
            "description": "High-level introduction to the system",
            "chunk_ids": [0, 1, 2]
        },
        ...
    ]
}

IMPORTANT:
- The chunk_ids array should contain the IDs of chunks that are relevant to each file
- A chunk can be relevant to multiple files if it contains content for multiple topics
- Ensure every chunk is assigned to at least one file
- Use your understanding of the content to make intelligent assignments"""


class SemanticAnalyzer:
    """Analyzes PDF chunks and proposes semantic structure."""

    def __init__(self, provider: LLMProvider | None = None, verbose: bool = True):
        self.provider = provider or get_provider()
        self.verbose = verbose
        self.conversation_history: list[dict] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def analyze(self, extraction: ExtractionResult) -> StructureProposal:
        """Analyze extracted chunks and propose a structure.

        Args:
            extraction: Result from PDFExtractor

        Returns:
            StructureProposal with recommended folder/file organization
        """
        self._log(f"Analyzing {len(extraction.chunks)} chunks from {extraction.source_pdf.name}")

        self._analyze_chunks(extraction.chunks)

        proposal = self._propose_structure(extraction)

        self._log(
            f"Analysis complete. Total tokens: {self.total_input_tokens} in, "
            f"{self.total_output_tokens} out"
        )

        return proposal

    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[Analyzer] {message}")

    def _analyze_chunks(self, chunks: list[Chunk]) -> None:
        """Feed chunks to LLM sequentially to build understanding."""
        self.conversation_history = []

        for i, chunk in enumerate(chunks):
            self._log(f"Processing chunk {i + 1}/{len(chunks)} (pages {chunk.start_page}-{chunk.end_page})")

            message = f"""Chunk {chunk.chunk_id} (Pages {chunk.start_page}-{chunk.end_page}):

{chunk.content}

---
Acknowledge this chunk and note any key topics, sections, or themes you observe."""

            self.conversation_history.append({"role": "user", "content": message})

            response = self.provider.complete(
                system=ANALYSIS_SYSTEM_PROMPT,
                messages=self.conversation_history,
                max_tokens=500,
            )

            self.total_input_tokens += response.input_tokens
            self.total_output_tokens += response.output_tokens

            self.conversation_history.append({"role": "assistant", "content": response.content})

            if len(self.conversation_history) > 20:
                summary_msg = self._summarize_history()
                self.conversation_history = [
                    {"role": "user", "content": summary_msg},
                    {"role": "assistant", "content": "I understand the document structure so far. Please continue with the remaining chunks."},
                ]

    def _summarize_history(self) -> str:
        """Create a summary of conversation history to manage context."""
        summary_request = """Based on our conversation so far, provide a brief summary of:
1. The document's main purpose and scope
2. Key topics covered so far
3. The overall structure you've observed

Be concise but comprehensive."""

        self.conversation_history.append({"role": "user", "content": summary_request})

        response = self.provider.complete(
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=self.conversation_history,
            max_tokens=1000,
        )

        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens

        return f"Summary of document analysis so far:\n\n{response.content}\n\nContinuing with remaining chunks..."

    def _propose_structure(self, extraction: ExtractionResult) -> StructureProposal:
        """Ask LLM to propose final structure based on analysis."""
        self._log("Generating structure proposal...")

        chunk_summary = "\n".join(
            f"- Chunk {c.chunk_id}: Pages {c.start_page}-{c.end_page} ({c.token_count} tokens)"
            for c in extraction.chunks
        )

        structure_request = f"""Based on your complete analysis of this document, propose a semantic
folder and file structure.

Document: {extraction.source_pdf.name}
Total pages: {extraction.total_pages}
Total images: {len(extraction.all_images)}

Available chunks:
{chunk_summary}

Provide your structure proposal as JSON following the format specified in your instructions."""

        self.conversation_history.append({"role": "user", "content": structure_request})

        response = self.provider.complete(
            system=STRUCTURE_SYSTEM_PROMPT,
            messages=self.conversation_history,
            max_tokens=4000,
        )

        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens

        try:
            content = response.content
            json_match = content
            if "```json" in content:
                json_match = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_match = content.split("```")[1].split("```")[0]

            structure_data = json.loads(json_match.strip())
        except (json.JSONDecodeError, IndexError) as e:
            self._log(f"Warning: Failed to parse JSON response, using fallback structure: {e}")
            structure_data = self._create_fallback_structure(extraction)

        files = [
            FileSpec(
                path=item["path"],
                title=item["title"],
                description=item.get("description", ""),
                chunk_ids=item.get("chunk_ids", []),
            )
            for item in structure_data.get("structure", [])
        ]

        if not files:
            self._log("Warning: No files in structure, using fallback")
            structure_data = self._create_fallback_structure(extraction)
            files = [
                FileSpec(
                    path=item["path"],
                    title=item["title"],
                    description=item.get("description", ""),
                    chunk_ids=item.get("chunk_ids", []),
                )
                for item in structure_data["structure"]
            ]

        return StructureProposal(
            overview=structure_data.get("overview", ""),
            files=files,
            raw_json=structure_data,
        )

    def _create_fallback_structure(self, extraction: ExtractionResult) -> dict:
        """Create a simple fallback structure if LLM response fails."""
        files = []
        chunks_per_file = max(1, len(extraction.chunks) // 5)

        for i in range(0, len(extraction.chunks), chunks_per_file):
            chunk_group = extraction.chunks[i : i + chunks_per_file]
            start_page = chunk_group[0].start_page
            end_page = chunk_group[-1].end_page
            file_num = (i // chunks_per_file) + 1

            files.append(
                {
                    "path": f"{file_num:02d}-section/content.md",
                    "title": f"Section {file_num}",
                    "description": f"Content from pages {start_page}-{end_page}",
                    "chunk_ids": [c.chunk_id for c in chunk_group],
                }
            )

        return {
            "overview": f"Document extracted from {extraction.source_pdf.name}",
            "structure": files,
        }


def analyze_extraction(
    extraction: ExtractionResult,
    provider: LLMProvider | None = None,
    verbose: bool = True,
) -> StructureProposal:
    """Convenience function to analyze an extraction.

    Args:
        extraction: Result from PDFExtractor
        provider: Optional LLM provider (auto-detected if not provided)
        verbose: Whether to print progress messages

    Returns:
        StructureProposal with recommended organization
    """
    analyzer = SemanticAnalyzer(provider=provider, verbose=verbose)
    return analyzer.analyze(extraction)
