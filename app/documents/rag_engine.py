"""
AetherMind Multimodal AI — Document Intelligence & Parsing Engine (Phase 7)
Supports: PDF, DOCX, PPTX, TXT, CSV, Excel (XLSX, XLS), JSON, Markdown
Provides text extraction, metadata extraction, page navigation, chunking architecture, and in-document search.
"""

import os
import json
import csv
import io
from typing import Dict, Any, List, Optional
from app.logging.logger import logger

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pptx
except ImportError:
    pptx = None

try:
    import openpyxl
except ImportError:
    openpyxl = None


class DocumentParserEngine:
    """Document Intelligence Engine for text extraction, metadata parsing, chunking, and in-document search"""

    SUPPORTED_EXTENSIONS = [
        ".pdf", ".docx", ".pptx", ".txt", ".csv", ".xlsx", ".xls", ".json", ".md"
    ]

    async def parse_document(self, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """Parse uploaded document bytes and extract structured text content, pages, and metadata."""
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        
        extracted_text = ""
        pages_content: List[Dict[str, Any]] = []
        metadata: Dict[str, Any] = {
            "filename": filename,
            "extension": ext,
            "size_bytes": len(content_bytes),
            "pages": 1,
            "word_count": 0,
            "char_count": len(content_bytes),
            "tables_count": 0,
        }

        try:
            if ext in [".txt", ".md"]:
                text = content_bytes.decode("utf-8", errors="ignore")
                extracted_text = text
                pages_content.append({"page_number": 1, "text": text})
                metadata["pages"] = 1

            elif ext == ".json":
                try:
                    data = json.loads(content_bytes.decode("utf-8", errors="ignore"))
                    extracted_text = json.dumps(data, indent=2)
                except Exception:
                    extracted_text = content_bytes.decode("utf-8", errors="ignore")
                pages_content.append({"page_number": 1, "text": extracted_text})
                metadata["pages"] = 1

            elif ext == ".csv":
                text_content = content_bytes.decode("utf-8", errors="ignore")
                reader = csv.reader(io.StringIO(text_content))
                rows = list(reader)
                row_strings = []
                for row in rows:
                    row_strings.append(" | ".join(row))
                extracted_text = "\n".join(row_strings)
                pages_content.append({"page_number": 1, "text": extracted_text})
                metadata["pages"] = 1
                metadata["tables_count"] = 1
                metadata["total_rows"] = len(rows)

            elif ext in [".xlsx", ".xls"]:
                if openpyxl:
                    try:
                        wb = openpyxl.load_workbook(io.BytesIO(content_bytes), data_only=True)
                        sheet_texts = []
                        page_num = 1
                        for sheet in wb.sheetnames:
                            ws = wb[sheet]
                            sheet_str = f"--- Sheet: {sheet} ---\n"
                            for row in ws.iter_rows(values_only=True):
                                row_vals = [str(val) if val is not None else "" for val in row]
                                if any(row_vals):
                                    sheet_str += " | ".join(row_vals) + "\n"
                            sheet_texts.append(sheet_str)
                            pages_content.append({"page_number": page_num, "sheet": sheet, "text": sheet_str})
                            page_num += 1
                        extracted_text = "\n\n".join(sheet_texts)
                        metadata["pages"] = len(wb.sheetnames)
                        metadata["tables_count"] = len(wb.sheetnames)
                    except Exception as e:
                        logger.warning(f"openpyxl failed for {filename}: {e}")
                        extracted_text = content_bytes.decode("utf-8", errors="ignore")
                        pages_content.append({"page_number": 1, "text": extracted_text})
                else:
                    extracted_text = content_bytes.decode("utf-8", errors="ignore")
                    pages_content.append({"page_number": 1, "text": extracted_text})

            elif ext == ".pdf":
                if pypdf:
                    try:
                        reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                        metadata["pages"] = len(reader.pages)
                        pdf_texts = []
                        for idx, page in enumerate(reader.pages):
                            p_text = page.extract_text() or ""
                            pdf_texts.append(p_text)
                            pages_content.append({"page_number": idx + 1, "text": p_text})
                        extracted_text = "\n\n--- Page Break ---\n\n".join(pdf_texts)
                    except Exception as pdf_err:
                        logger.warning(f"pypdf extraction error for {filename}: {pdf_err}")
                        extracted_text = f"[PDF Document {filename} — Structured metadata extracted. Page count: {metadata['pages']}]"
                        pages_content.append({"page_number": 1, "text": extracted_text})
                else:
                    extracted_text = f"[PDF Document {filename}]"
                    pages_content.append({"page_number": 1, "text": extracted_text})

            elif ext == ".docx":
                if docx:
                    try:
                        doc = docx.Document(io.BytesIO(content_bytes))
                        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                        tables_text = []
                        for tbl in doc.tables:
                            for row in tbl.rows:
                                row_txt = " | ".join([cell.text.strip() for cell in row.cells])
                                tables_text.append(row_txt)
                        metadata["tables_count"] = len(doc.tables)
                        extracted_text = "\n".join(paragraphs) + ("\n\n--- Tables ---\n" + "\n".join(tables_text) if tables_text else "")
                        pages_content.append({"page_number": 1, "text": extracted_text})
                        # Rough page estimate
                        metadata["pages"] = max(1, len(extracted_text) // 2000)
                    except Exception as docx_err:
                        logger.warning(f"docx extraction error for {filename}: {docx_err}")
                        extracted_text = f"[Word Document {filename}]"
                        pages_content.append({"page_number": 1, "text": extracted_text})
                else:
                    extracted_text = f"[Word Document {filename}]"
                    pages_content.append({"page_number": 1, "text": extracted_text})

            elif ext == ".pptx":
                if pptx:
                    try:
                        prs = pptx.Presentation(io.BytesIO(content_bytes))
                        slide_texts = []
                        for idx, slide in enumerate(prs.slides):
                            s_txts = []
                            for shape in slide.shapes:
                                if hasattr(shape, "text") and shape.text:
                                    s_txts.append(shape.text)
                            slide_str = f"--- Slide {idx + 1} ---\n" + "\n".join(s_txts)
                            slide_texts.append(slide_str)
                            pages_content.append({"page_number": idx + 1, "text": slide_str})
                        extracted_text = "\n\n".join(slide_texts)
                        metadata["pages"] = len(prs.slides)
                    except Exception as pptx_err:
                        logger.warning(f"pptx extraction error for {filename}: {pptx_err}")
                        extracted_text = f"[PowerPoint Presentation {filename}]"
                        pages_content.append({"page_number": 1, "text": extracted_text})
                else:
                    extracted_text = f"[PowerPoint Presentation {filename}]"
                    pages_content.append({"page_number": 1, "text": extracted_text})

            else:
                extracted_text = content_bytes.decode("utf-8", errors="ignore")
                pages_content.append({"page_number": 1, "text": extracted_text})

        except Exception as e:
            logger.error(f"Error parsing document {filename}: {str(e)}")
            extracted_text = f"[Document content for {filename}]"
            pages_content = [{"page_number": 1, "text": extracted_text}]

        words = extracted_text.split()
        metadata["word_count"] = len(words)
        metadata["char_count"] = len(extracted_text)

        # Prepare RAG Chunks Architecture
        chunks = self.prepare_chunks(extracted_text, metadata, pages_content)
        metadata["chunks_count"] = len(chunks)

        return {
            "filename": filename,
            "extracted_text": extracted_text,
            "snippet": extracted_text[:350] + ("..." if len(extracted_text) > 350 else ""),
            "pages_content": pages_content,
            "chunks": chunks,
            "metadata": metadata
        }

    def prepare_chunks(
        self,
        extracted_text: str,
        metadata: Dict[str, Any],
        pages_content: List[Dict[str, Any]],
        chunk_size: int = 800,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """Chunk preparation architecture for future RAG compatibility"""
        chunks = []
        chunk_id = 0

        if not extracted_text:
            return []

        # If pages exist, chunk by pages or sliding window
        for page in pages_content:
            p_num = page.get("page_number", 1)
            text = page.get("text", "")
            if not text:
                continue

            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end]
                chunks.append({
                    "chunk_id": chunk_id,
                    "page_number": p_num,
                    "filename": metadata.get("filename"),
                    "start_char": start,
                    "end_char": end,
                    "text": chunk_text,
                    "token_count_estimate": max(1, len(chunk_text.split()))
                })
                chunk_id += 1
                if end == len(text):
                    break
                start += (chunk_size - chunk_overlap)

        return chunks

    def search_document_text(self, document_text: str, query: str, pages_content: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Search query inside document text with line/page numbers and snippet matches."""
        if not query or not document_text:
            return []

        results = []
        query_lower = query.lower()

        if pages_content:
            for page in pages_content:
                p_num = page.get("page_number", 1)
                lines = page.get("text", "").split("\n")
                for line_num, line in enumerate(lines, 1):
                    if query_lower in line.lower():
                        results.append({
                            "page_number": p_num,
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "query": query
                        })
                        if len(results) >= 20:
                            break
        else:
            lines = document_text.split("\n")
            for line_num, line in enumerate(lines, 1):
                if query_lower in line.lower():
                    results.append({
                        "page_number": 1,
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "query": query
                    })
                    if len(results) >= 20:
                        break

        return results


document_engine = DocumentParserEngine()
