"""PDF Chunk Extractor - Phase 1 of semantic decomposition.

Extracts content from PDFs into digestible chunks with images and tables.
No LLM calls - pure PDF processing.
"""

import hashlib
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # pymupdf
import tiktoken


@dataclass
class ImageInfo:
    """Metadata for an extracted image."""

    image_id: str
    page_number: int
    file_path: Path
    width: int
    height: int
    caption: str | None = None


@dataclass
class Chunk:
    """A content chunk extracted from the PDF."""

    chunk_id: int
    content: str
    start_page: int
    end_page: int
    token_count: int
    images: list[ImageInfo] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Complete extraction result from a PDF."""

    source_pdf: Path
    total_pages: int
    chunks: list[Chunk]
    all_images: list[ImageInfo]
    temp_dir: Path


class PDFExtractor:
    """Extracts content from PDFs into LLM-digestible chunks."""

    def __init__(
        self,
        chunk_size: int = 2000,
        chunk_overlap: int = 100,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.temp_dir: Path | None = None

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """Extract content from PDF into chunks.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            ExtractionResult with chunks, images, and metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.temp_dir = Path(tempfile.mkdtemp(prefix="pdf_parser_"))
        images_dir = self.temp_dir / "images"
        images_dir.mkdir(exist_ok=True)

        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        all_images: list[ImageInfo] = []
        page_contents: list[tuple[int, str, list[ImageInfo]]] = []

        for page_num in range(total_pages):
            page = doc[page_num]
            page_number = page_num + 1

            text = page.get_text("text")
            text = self._clean_text(text)

            page_images = self._extract_images(page, page_number, images_dir)
            all_images.extend(page_images)

            page_contents.append((page_number, text, page_images))

        doc.close()

        chunks = self._create_chunks(page_contents)

        return ExtractionResult(
            source_pdf=pdf_path,
            total_pages=total_pages,
            chunks=chunks,
            all_images=all_images,
            temp_dir=self.temp_dir,
        )

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"(\S)-\n(\S)", r"\1\2", text)
        return text.strip()

    def _extract_images(
        self, page: fitz.Page, page_number: int, images_dir: Path
    ) -> list[ImageInfo]:
        """Extract images from a page."""
        images = []
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = page.parent.extract_image(xref)
                if base_image:
                    image_bytes = base_image["image"]
                    image_ext = base_image.get("ext", "png")

                    img_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                    filename = f"page{page_number:03d}_img{img_index:02d}_{img_hash}.{image_ext}"
                    file_path = images_dir / filename

                    with open(file_path, "wb") as f:
                        f.write(image_bytes)

                    images.append(
                        ImageInfo(
                            image_id=f"p{page_number}_i{img_index}",
                            page_number=page_number,
                            file_path=file_path,
                            width=base_image.get("width", 0),
                            height=base_image.get("height", 0),
                        )
                    )
            except Exception:
                continue

        return images

    def _create_chunks(
        self, page_contents: list[tuple[int, str, list[ImageInfo]]]
    ) -> list[Chunk]:
        """Create token-limited chunks from page contents."""
        chunks: list[Chunk] = []
        current_content = ""
        current_start_page = 1
        current_images: list[ImageInfo] = []
        chunk_id = 0

        for page_number, text, page_images in page_contents:
            page_marker = f"\n\n[Page {page_number}]\n\n"
            potential_content = current_content + page_marker + text

            if self.count_tokens(potential_content) > self.chunk_size:
                if current_content:
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            content=current_content.strip(),
                            start_page=current_start_page,
                            end_page=page_number - 1,
                            token_count=self.count_tokens(current_content),
                            images=current_images.copy(),
                        )
                    )
                    chunk_id += 1

                    overlap_text = self._get_overlap_text(current_content)
                    current_content = overlap_text + page_marker + text
                    current_start_page = page_number
                    current_images = page_images.copy()
                else:
                    text_chunks = self._split_large_text(text, page_number)
                    for tc in text_chunks[:-1]:
                        chunks.append(
                            Chunk(
                                chunk_id=chunk_id,
                                content=tc,
                                start_page=page_number,
                                end_page=page_number,
                                token_count=self.count_tokens(tc),
                                images=[],
                            )
                        )
                        chunk_id += 1
                    current_content = text_chunks[-1] if text_chunks else ""
                    current_start_page = page_number
                    current_images = page_images.copy()
            else:
                current_content = potential_content
                current_images.extend(page_images)

        if current_content.strip():
            last_page = page_contents[-1][0] if page_contents else 1
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    content=current_content.strip(),
                    start_page=current_start_page,
                    end_page=last_page,
                    token_count=self.count_tokens(current_content),
                    images=current_images,
                )
            )

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of current content."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= self.chunk_overlap:
            return text
        overlap_tokens = tokens[-self.chunk_overlap :]
        return self.encoding.decode(overlap_tokens)

    def _split_large_text(self, text: str, page_number: int) -> list[str]:
        """Split text that exceeds chunk size."""
        chunks = []
        paragraphs = text.split("\n\n")
        current = f"[Page {page_number}]\n\n"

        for para in paragraphs:
            potential = current + para + "\n\n"
            if self.count_tokens(potential) > self.chunk_size:
                if current.strip():
                    chunks.append(current.strip())
                if self.count_tokens(para) > self.chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    current = ""
                    for sent in sentences:
                        if self.count_tokens(current + sent) > self.chunk_size:
                            if current.strip():
                                chunks.append(current.strip())
                            current = sent + " "
                        else:
                            current += sent + " "
                else:
                    current = para + "\n\n"
            else:
                current = potential

        if current.strip():
            chunks.append(current.strip())

        return chunks


def extract_pdf(
    pdf_path: str | Path,
    chunk_size: int = 2000,
    chunk_overlap: int = 100,
) -> ExtractionResult:
    """Convenience function to extract a PDF.

    Args:
        pdf_path: Path to the PDF file
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Token overlap between chunks

    Returns:
        ExtractionResult with chunks and images
    """
    extractor = PDFExtractor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return extractor.extract(Path(pdf_path))
