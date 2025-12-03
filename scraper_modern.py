"""
Modern elaws scraper - Unified interface for scraping Ontario legal documents.

This module provides a clean, modern API for scraping legal documents from
ontario.ca/laws, automatically handling different document structures and
producing consistent output format.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

from models import LegalDocument, DocumentType, SectionContent
from parsers import ParserFactory
from metadata import MetadataExtractor
from utils import setup_logging, sanitize_filename

logger = logging.getLogger(__name__)


class ELawsScraper:
    """
    Modern scraper for Ontario legal documents.

    This class provides a unified interface for scraping any legal document,
    automatically detecting the document structure and extracting all content
    and metadata.
    """

    def __init__(self, output_dir: str = "db", log_file: Optional[str] = None):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save scraped JSON files
            log_file: Optional log file path
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set up logging
        setup_logging(log_file=log_file)

    def scrape_document(self, url: str) -> LegalDocument:
        """
        Scrape a complete legal document.

        This method:
        1. Detects the document structure
        2. Extracts all metadata (act info, versions, etc.)
        3. Parses content using the appropriate parser
        4. Returns a unified LegalDocument object

        Args:
            url: The URL of the document to scrape

        Returns:
            LegalDocument object with all content and metadata

        Example:
            >>> scraper = ELawsScraper()
            >>> doc = scraper.scrape_document("https://www.ontario.ca/laws/statute/90i03")
            >>> print(doc.act_info.full_title)
        """
        logger.info(f"Starting to scrape document: {url}")

        try:
            # Extract metadata
            metadata_extractor = MetadataExtractor(url)
            metadata = metadata_extractor.extract_all_metadata()

            # Parse content using appropriate parser
            parser = ParserFactory.create_parser(url)
            content_list = parser.parse()

            # Convert content to SectionContent objects
            sections = []
            for item in content_list:
                section = SectionContent(
                    id=item.get('id', ''),
                    section=item.get('section'),
                    content=item.get('content', ''),
                    raw_html=item.get('raw_html', ''),
                    ahref_id=item.get('ahref_id'),
                    toc_id=item.get('TOCid'),
                    part_id=item.get('part_id'),
                    part_type=item.get('part_type')
                )
                sections.append(section)

            # Create LegalDocument object
            document = LegalDocument(
                document_type=metadata['document_type'],
                act_info=metadata.get('act_info'),
                reg_info=metadata.get('reg_info'),
                copyright=metadata.get('copyright'),
                versions=metadata.get('versions', []),
                current_regs=metadata.get('current_regs', []),
                revoked_regs=metadata.get('revoked_regs', []),
                content=sections
            )

            logger.info(f"Successfully scraped document with {len(sections)} sections")
            return document

        except Exception as e:
            logger.error(f"Error scraping document {url}: {e}", exc_info=True)
            raise

    def save_document(self, document: LegalDocument, filename: Optional[str] = None) -> str:
        """
        Save a document to JSON file.

        Args:
            document: LegalDocument to save
            filename: Optional custom filename (auto-generated if not provided)

        Returns:
            Path to the saved file
        """
        if filename is None:
            filename = document.get_filename()

        filename = sanitize_filename(filename)
        filepath = self.output_dir / filename

        logger.info(f"Saving document to {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Document saved successfully")
        return str(filepath)

    def scrape_and_save(self, url: str, filename: Optional[str] = None) -> str:
        """
        Scrape a document and save it to JSON.

        Convenience method that combines scrape_document() and save_document().

        Args:
            url: The URL of the document to scrape
            filename: Optional custom filename

        Returns:
            Path to the saved file
        """
        document = self.scrape_document(url)
        return self.save_document(document, filename)


def scrape_url(url: str, output_dir: str = "db") -> Dict[str, Any]:
    """
    Simple function to scrape a single URL.

    Args:
        url: The URL to scrape
        output_dir: Directory to save output

    Returns:
        Dictionary with document data

    Example:
        >>> data = scrape_url("https://www.ontario.ca/laws/statute/90i03")
        >>> print(data['act_info']['full_title'])
    """
    scraper = ELawsScraper(output_dir=output_dir)
    document = scraper.scrape_document(url)
    scraper.save_document(document)
    return document.to_dict()


def main():
    """
    Main entry point for command-line usage.
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scraper_modern.py <url> [output_dir]")
        print("\nExample:")
        print("  python scraper_modern.py https://www.ontario.ca/laws/statute/90i03")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "db"

    try:
        scraper = ELawsScraper(output_dir=output_dir, log_file="scraper.log")
        filepath = scraper.scrape_and_save(url)
        print(f"✓ Document scraped successfully: {filepath}")
    except Exception as e:
        print(f"✗ Error scraping document: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
