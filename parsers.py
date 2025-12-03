"""
Unified parsing framework for elaws documents.

This module provides a modern, object-oriented architecture for parsing
Ontario legal documents. It uses abstract base classes to define a common
interface, with specialized parsers for different document structures.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd
from bs4 import BeautifulSoup, Tag
import requests

from models import SectionContent, StructureType
from utils import (
    process_section,
    remove_trailing_zero,
    get_section_classes,
    build_css_selector,
    extract_table_by_class,
    is_part_heading,
    extract_ahref_from_span,
    get_request_headers
)

logger = logging.getLogger(__name__)


class DocumentParser(ABC):
    """
    Abstract base class for all document parsers.

    This class defines the common interface that all parsers must implement.
    It ensures consistent output format regardless of the document structure.
    """

    def __init__(self, url: str):
        """
        Initialize the parser.

        Args:
            url: The URL of the document to parse
        """
        self.url = url
        self.soup: Optional[BeautifulSoup] = None
        self._content_cache: Optional[List[SectionContent]] = None

    def fetch_content(self) -> BeautifulSoup:
        """
        Fetch and parse the HTML content from the URL.

        Returns:
            BeautifulSoup object of the page

        Raises:
            requests.RequestException: If the request fails
        """
        logger.info(f"Fetching content from {self.url}")
        response = requests.get(self.url, headers=get_request_headers())
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, "lxml")
        return self.soup

    @abstractmethod
    def extract_toc(self) -> Optional[pd.DataFrame]:
        """
        Extract table of contents information.

        Returns:
            DataFrame with TOC information, or None if no TOC exists
        """
        pass

    @abstractmethod
    def extract_sections(self) -> List[Dict[str, Any]]:
        """
        Extract section content from the document.

        Returns:
            List of dictionaries containing section data
        """
        pass

    def parse(self) -> List[Dict[str, Any]]:
        """
        Main parsing method that orchestrates the extraction process.

        Returns:
            List of dictionaries with complete section information
        """
        if self.soup is None:
            self.fetch_content()

        logger.info(f"Parsing document with {self.__class__.__name__}")

        # Extract TOC and sections
        toc_df = self.extract_toc()
        sections = self.extract_sections()

        # Merge and return
        return self.merge_data(toc_df, sections)

    def merge_data(
        self,
        toc_df: Optional[pd.DataFrame],
        sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge TOC metadata with section content.

        Args:
            toc_df: DataFrame with TOC information
            sections: List of section dictionaries

        Returns:
            Merged list of dictionaries
        """
        if toc_df is None or toc_df.empty:
            # No TOC, return sections as-is
            return sections

        # Convert sections to DataFrame for merging
        sections_df = pd.DataFrame(sections)

        # Merge based on ahref_id
        if 'ahref_id' in sections_df.columns and 'ahref_id' in toc_df.columns:
            merged = toc_df.merge(sections_df, how="left", on="ahref_id")
        else:
            # Fallback: just return sections
            logger.warning("Cannot merge TOC and sections - missing ahref_id")
            return sections

        # Convert back to list of dicts
        return merged.to_dict(orient='records')

    def _extract_all_sections(self) -> List[Dict[str, Any]]:
        """
        Extract all section elements using standard CSS selectors.

        Returns:
            List of section data dictionaries
        """
        sections = []
        section_classes = get_section_classes()
        selector = build_css_selector(section_classes)

        for section_tag in self.soup.select(selector):
            section_data = process_section(section_tag)
            sections.append(section_data)

        logger.info(f"Extracted {len(sections)} sections")
        return sections


class TOCParser(DocumentParser):
    """
    Parser for documents with traditional table of contents.

    This parser handles documents with structured TOC tables that map
    TOC IDs to section content.
    """

    def extract_toc(self) -> Optional[pd.DataFrame]:
        """
        Extract traditional table of contents.

        Returns:
            DataFrame with columns: ahref_id, TOCid, section, part_id, part_type
        """
        logger.info("Extracting traditional TOC")

        # Find the TOC table
        toc_table = extract_table_by_class(self.soup, 'MsoNormalTable')
        if not toc_table:
            logger.warning("No MsoNormalTable found")
            return None

        # Extract parts ahref pointers from spans
        tocspans = toc_table.find_all('span')
        parts_ahref_pointers = {}
        for span in tocspans:
            span_text = span.text
            ahref = extract_ahref_from_span(span)
            if ahref:
                parts_ahref_pointers[span_text] = ahref

        # Read tables with pandas
        dfs = pd.read_html(self.url)

        # Determine which table is the TOC based on document structure
        toc_index = self._determine_toc_index()
        if toc_index >= len(dfs):
            logger.warning(f"TOC index {toc_index} out of range")
            return None

        toc = dfs[toc_index]

        # Create DataFrame
        leginfo = pd.DataFrame({
            'TOCid': toc[0],
            'section': toc[1]
        })

        # Remove trailing zeroes from TOC IDs
        leginfo['TOCid'] = leginfo['TOCid'].apply(remove_trailing_zero)

        # Extract ahref_id for each TOC entry
        leginfo['ahref_id'] = leginfo['TOCid'].apply(
            lambda x: self._find_ahref_for_tocid(x)
        )

        # Fill in PART entries from parts_ahref_pointers
        self._populate_parts(leginfo, parts_ahref_pointers)

        # Add part_id and part_type based on PART entries
        self._associate_parts(leginfo)

        return leginfo

    def _determine_toc_index(self) -> int:
        """
        Determine which table index contains the TOC.

        Returns:
            Index of the TOC table
        """
        # Check for specific anchors to determine table position
        has_revoked = bool(self.soup.find('a', href="#revoked_regulations"))
        has_current = bool(self.soup.find('a', href="#regulations"))

        if has_revoked and has_current:
            return 3
        elif has_current or has_revoked:
            return 2
        else:
            return 1

    def _find_ahref_for_tocid(self, tocid: str) -> Optional[str]:
        """
        Find the ahref for a given TOC ID.

        Args:
            tocid: The TOC ID to search for

        Returns:
            The ahref string (with #) or None
        """
        ahref_tag = self.soup.find('a', string=tocid, href=True)
        if ahref_tag:
            return ahref_tag['href']
        return None

    def _populate_parts(self, df: pd.DataFrame, parts_dict: Dict[str, str]) -> None:
        """
        Populate PART entries in the DataFrame.

        Args:
            df: DataFrame to populate
            parts_dict: Dictionary mapping part names to hrefs
        """
        next_pointer = 0
        for index, row in df.iterrows():
            if pd.isna(row['ahref_id']) and next_pointer < len(parts_dict):
                new_ahref = list(parts_dict.values())[next_pointer]
                tocid = list(parts_dict.keys())[next_pointer]
                df.at[index, 'ahref_id'] = new_ahref
                df.at[index, 'TOCid'] = tocid
                next_pointer += 1

    def _associate_parts(self, df: pd.DataFrame) -> None:
        """
        Associate sections with their parent PART.

        Args:
            df: DataFrame to update with part_id and part_type
        """
        df['part_id'] = None
        df['part_type'] = None

        current_part_id = None
        current_part_type = None

        for index, row in df.iterrows():
            tocid = str(row['TOCid'])
            if is_part_heading(tocid):
                current_part_id = tocid
                current_part_type = row['section']
            else:
                df.at[index, 'part_id'] = current_part_id
                df.at[index, 'part_type'] = current_part_type

    def extract_sections(self) -> List[Dict[str, Any]]:
        """
        Extract sections for TOC-based documents.

        Returns:
            List of section data dictionaries
        """
        return self._extract_all_sections()


class LeftHeadParser(DocumentParser):
    """
    Parser for documents with left-aligned navigation sidebar.

    This parser handles documents where the TOC uses a left-head bearing
    layout with different column structure.
    """

    def extract_toc(self) -> Optional[pd.DataFrame]:
        """
        Extract left-head style table of contents.

        Returns:
            DataFrame with TOC information
        """
        logger.info("Extracting left-head TOC")

        # Find the TOC table
        toc_table = extract_table_by_class(self.soup, 'MsoNormalTable')
        if not toc_table:
            logger.warning("No MsoNormalTable found")
            return None

        # Extract parts ahref pointers
        tocspans = toc_table.find_all('span')
        parts_ahref_pointers = {}
        for span in tocspans:
            span_text = span.text
            ahref = extract_ahref_from_span(span)
            if ahref:
                parts_ahref_pointers[span_text] = ahref

        # Read tables with pandas
        dfs = pd.read_html(self.url)
        if len(dfs) < 2:
            logger.warning("Not enough tables found")
            return None

        toc = dfs[1]  # LeftHead typically uses second table

        # Create DataFrame with 3-column structure
        leginfo = pd.DataFrame({
            'TOCid': toc[0],
            'section1': toc[1],
            'section2': toc[2]
        })

        # Extract ahref_id based on section1
        leginfo['ahref_id'] = leginfo['section1'].apply(
            lambda x: self._find_ahref_for_text(x)
        )

        # Populate PART entries
        self._populate_parts(leginfo, parts_ahref_pointers)

        # Fill NaN values
        leginfo = leginfo.fillna('None')

        # Associate parts
        self._associate_parts(leginfo)

        return leginfo

    def _find_ahref_for_text(self, text: str) -> Optional[str]:
        """
        Find ahref for given text.

        Args:
            text: Text to search for

        Returns:
            The ahref string or None
        """
        ahref_tag = self.soup.find('a', string=text, href=True)
        if not ahref_tag:
            # Try with -e suffix
            ahref_tag = self.soup.find('a', string=f"{text}-e", href=True)
        if ahref_tag:
            return ahref_tag['href']
        return None

    def _populate_parts(self, df: pd.DataFrame, parts_dict: Dict[str, str]) -> None:
        """Populate PART entries (same as TOC parser)."""
        next_pointer = 0
        for index, row in df.iterrows():
            if pd.isna(row['ahref_id']) and next_pointer < len(parts_dict):
                new_ahref = list(parts_dict.values())[next_pointer]
                tocid = list(parts_dict.keys())[next_pointer]
                df.at[index, 'ahref_id'] = new_ahref
                df.at[index, 'TOCid'] = tocid
                next_pointer += 1

    def _associate_parts(self, df: pd.DataFrame) -> None:
        """Associate sections with PART (same as TOC parser)."""
        df['part_id'] = None

        current_part_id = None
        for index, row in df.iterrows():
            tocid = row['TOCid']
            if is_part_heading(str(tocid)):
                current_part_id = tocid
            else:
                df.at[index, 'part_id'] = current_part_id

    def extract_sections(self) -> List[Dict[str, Any]]:
        """
        Extract sections for left-head documents.

        Returns:
            List of section data dictionaries
        """
        return self._extract_all_sections()


class NoTOCParser(DocumentParser):
    """
    Parser for documents without a table of contents.

    This parser handles simpler documents that lack formal TOC structure
    and directly extracts section content.
    """

    def extract_toc(self) -> Optional[pd.DataFrame]:
        """
        No TOC to extract.

        Returns:
            None
        """
        logger.info("No TOC extraction for NoTOC documents")
        return None

    def extract_sections(self) -> List[Dict[str, Any]]:
        """
        Extract sections directly without TOC.

        Returns:
            List of section data dictionaries
        """
        logger.info("Extracting sections without TOC")
        return self._extract_all_sections()


class ParserFactory:
    """
    Factory class for creating appropriate parsers based on document structure.
    """

    @staticmethod
    def detect_structure(soup: BeautifulSoup) -> StructureType:
        """
        Detect the document structure type.

        Args:
            soup: BeautifulSoup object of the document

        Returns:
            The detected structure type
        """
        # Look for TOC table
        toc_table = extract_table_by_class(soup, 'MsoNormalTable')

        if not toc_table:
            logger.info("No TOC table found - using NoTOC parser")
            return StructureType.NOTOC

        # Check for left-head markers
        if toc_table.find('p', class_='TOCheadLeft'):
            logger.info("Left-head TOC detected")
            return StructureType.LEFTHEAD

        # Check for traditional TOC markers
        if toc_table.find('p', class_='TOCid') or toc_table.find('p', class_='TOCid-e'):
            logger.info("Traditional TOC detected")
            return StructureType.TOC

        # Default to TOC if table exists
        logger.info("TOC table found - using TOC parser")
        return StructureType.TOC

    @staticmethod
    def create_parser(url: str, structure_type: Optional[StructureType] = None) -> DocumentParser:
        """
        Create the appropriate parser for a document.

        Args:
            url: The URL of the document
            structure_type: Optional - specify structure type, or auto-detect

        Returns:
            An instance of the appropriate parser
        """
        # Auto-detect if not specified
        if structure_type is None:
            response = requests.get(url, headers=get_request_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")
            structure_type = ParserFactory.detect_structure(soup)

        # Create the appropriate parser
        if structure_type == StructureType.TOC:
            return TOCParser(url)
        elif structure_type == StructureType.LEFTHEAD:
            return LeftHeadParser(url)
        elif structure_type == StructureType.NOTOC:
            return NoTOCParser(url)
        else:
            logger.warning(f"Unknown structure type {structure_type}, defaulting to NoTOC")
            return NoTOCParser(url)


def parse_document(url: str) -> List[Dict[str, Any]]:
    """
    High-level function to parse any document.

    This function automatically detects the document structure and uses
    the appropriate parser to extract content.

    Args:
        url: The URL of the document to parse

    Returns:
        List of dictionaries with section content

    Example:
        >>> content = parse_document("https://www.ontario.ca/laws/statute/90i03")
    """
    parser = ParserFactory.create_parser(url)
    return parser.parse()
