"""
Metadata extraction for legal documents.

This module handles extraction of document metadata including:
- Act/Regulation information
- Version history
- Current and revoked regulations
- Copyright information
"""

import logging
from typing import Optional, List, Tuple
from datetime import datetime
from bs4 import BeautifulSoup, Tag
import requests

from models import (
    ActInfo, RegulationInfo, CopyrightInfo,
    VersionInfo, RegulationReference, DocumentType
)
from utils import get_request_headers, clean_text

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Extracts metadata from legal document pages.
    """

    def __init__(self, url: str, soup: Optional[BeautifulSoup] = None):
        """
        Initialize the metadata extractor.

        Args:
            url: The URL of the document
            soup: Optional BeautifulSoup object (will fetch if not provided)
        """
        self.url = url
        self.soup = soup
        if self.soup is None:
            self.fetch_content()

    def fetch_content(self) -> None:
        """Fetch and parse the HTML content."""
        logger.info(f"Fetching content for metadata extraction from {self.url}")
        response = requests.get(self.url, headers=get_request_headers())
        response.raise_for_status()
        self.soup = BeautifulSoup(response.content, "lxml")

    def detect_document_type(self) -> DocumentType:
        """
        Detect whether this is a statute or regulation.

        Returns:
            DocumentType.STATUTE or DocumentType.REGULATION
        """
        # Check URL pattern
        if '/regulation/' in self.url.lower():
            return DocumentType.REGULATION

        # Check for regulation-specific elements
        if self.soup.find('div', class_='reg-info') or self.soup.find('p', class_='reg-name-text'):
            return DocumentType.REGULATION

        # Default to statute
        return DocumentType.STATUTE

    def extract_act_info(self) -> Optional[ActInfo]:
        """
        Extract Act/Statute metadata.

        Returns:
            ActInfo object or None if not an act
        """
        logger.info("Extracting Act information")

        # Find act name
        act_name_tag = self.soup.find('p', class_='act-name-text')
        if not act_name_tag:
            logger.warning("No act-name-text found")
            return None

        act_name_text = clean_text(act_name_tag.get_text())

        # Find citation
        citation_tag = self.soup.find('p', class_='citation')
        citation = clean_text(citation_tag.get_text()) if citation_tag else ""

        # Construct full title
        full_title = f"{act_name_text} {citation}".strip()

        return ActInfo(
            full_title=full_title,
            act_name_text=act_name_text,
            citation=citation,
            url=self.url
        )

    def extract_reg_info(self) -> Optional[RegulationInfo]:
        """
        Extract Regulation metadata.

        Returns:
            RegulationInfo object or None if not a regulation
        """
        logger.info("Extracting Regulation information")

        # Find regulation name
        reg_name_tag = self.soup.find('p', class_='reg-name-text')
        if not reg_name_tag:
            logger.warning("No reg-name-text found")
            return None

        reg_name_text = clean_text(reg_name_tag.get_text())

        # Find citation
        citation_tag = self.soup.find('p', class_='citation')
        citation = clean_text(citation_tag.get_text()) if citation_tag else ""

        # Find parent act
        act_under = None
        act_under_tag = self.soup.find('p', class_='act-under')
        if act_under_tag:
            act_link = act_under_tag.find('a')
            if act_link:
                act_under = clean_text(act_link.get_text())

        # Construct full title
        full_title = f"{reg_name_text} {citation}".strip()

        return RegulationInfo(
            full_title=full_title,
            reg_name_text=reg_name_text,
            citation=citation,
            url=self.url,
            act_under=act_under
        )

    def extract_copyright(self) -> Optional[CopyrightInfo]:
        """
        Extract copyright information.

        Returns:
            CopyrightInfo object or None if not found
        """
        logger.info("Extracting copyright information")

        # Look for copyright text
        copyright_tag = self.soup.find('p', class_='copyright')
        if not copyright_tag:
            # Try alternate locations
            copyright_tag = self.soup.find(string=lambda text: text and 'King\'s Printer' in text)
            if copyright_tag:
                copyright_text = clean_text(str(copyright_tag))
            else:
                # Default copyright
                current_year = datetime.now().year
                copyright_text = f"© King's Printer for Ontario, {current_year}."
        else:
            copyright_text = clean_text(copyright_tag.get_text())

        return CopyrightInfo(copyright_text=copyright_text)

    def extract_versions(self) -> List[VersionInfo]:
        """
        Extract version history.

        Returns:
            List of VersionInfo objects
        """
        logger.info("Extracting version history")

        versions = []

        # Find versions table or list
        versions_section = self.soup.find('div', id='versions')
        if not versions_section:
            versions_section = self.soup.find('table', class_='versions')

        if not versions_section:
            logger.warning("No versions section found")
            # Return default current version
            return [VersionInfo(
                a_href="/laws/about-e-laws#ccl",
                valid_from="unknown",
                valid_to="current"
            )]

        # Extract version rows
        rows = versions_section.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Extract dates
                valid_from = clean_text(cells[0].get_text()) or "unknown"
                valid_to = clean_text(cells[1].get_text()) or "current"

                # Extract href if available
                link = row.find('a', href=True)
                a_href = link['href'] if link else "/laws/about-e-laws#ccl"

                versions.append(VersionInfo(
                    a_href=a_href,
                    valid_from=valid_from,
                    valid_to=valid_to
                ))

        if not versions:
            # Return default if nothing found
            versions.append(VersionInfo(
                a_href="/laws/about-e-laws#ccl",
                valid_from="unknown",
                valid_to="current"
            ))

        logger.info(f"Found {len(versions)} versions")
        return versions

    def extract_current_regulations(self) -> List[RegulationReference]:
        """
        Extract current regulations (for Acts).

        Returns:
            List of RegulationReference objects
        """
        logger.info("Extracting current regulations")

        regulations = []

        # Find regulations section
        reg_anchor = self.soup.find('a', attrs={'name': 'regulations'})
        if not reg_anchor:
            reg_anchor = self.soup.find('a', href='#regulations')

        if not reg_anchor:
            logger.info("No current regulations section found")
            return regulations

        # Find the table or list following the anchor
        reg_section = reg_anchor.find_next('table') or reg_anchor.find_next('ul')
        if not reg_section:
            logger.warning("No regulations table/list found")
            return regulations

        # Extract regulation links
        links = reg_section.find_all('a', href=True)
        for link in links:
            href = link['href']
            if '/regulation/' in href:
                # Extract citation and title
                citation = clean_text(link.get_text()) or ""

                # Try to find title (usually in next sibling or parent)
                title = ""
                parent = link.find_parent('td') or link.find_parent('li')
                if parent:
                    title = clean_text(parent.get_text()).replace(citation, '').strip()

                regulations.append(RegulationReference(
                    a_href=href,
                    citation=citation,
                    title=title
                ))

        logger.info(f"Found {len(regulations)} current regulations")
        return regulations

    def extract_revoked_regulations(self) -> List[RegulationReference]:
        """
        Extract revoked regulations (for Acts).

        Returns:
            List of RegulationReference objects
        """
        logger.info("Extracting revoked regulations")

        regulations = []

        # Find revoked regulations section
        reg_anchor = self.soup.find('a', attrs={'name': 'revoked_regulations'})
        if not reg_anchor:
            reg_anchor = self.soup.find('a', href='#revoked_regulations')

        if not reg_anchor:
            logger.info("No revoked regulations section found")
            return regulations

        # Find the table or list following the anchor
        reg_section = reg_anchor.find_next('table') or reg_anchor.find_next('ul')
        if not reg_section:
            logger.warning("No revoked regulations table/list found")
            return regulations

        # Extract regulation links
        links = reg_section.find_all('a', href=True)
        for link in links:
            href = link['href']
            if '/regulation/' in href:
                citation = clean_text(link.get_text()) or ""

                title = ""
                parent = link.find_parent('td') or link.find_parent('li')
                if parent:
                    title = clean_text(parent.get_text()).replace(citation, '').strip()

                regulations.append(RegulationReference(
                    a_href=href,
                    citation=citation,
                    title=title
                ))

        logger.info(f"Found {len(regulations)} revoked regulations")
        return regulations

    def extract_all_metadata(self) -> dict:
        """
        Extract all metadata for the document.

        Returns:
            Dictionary with all metadata fields
        """
        doc_type = self.detect_document_type()

        metadata = {
            'document_type': doc_type,
            'copyright': self.extract_copyright(),
            'versions': self.extract_versions(),
        }

        if doc_type == DocumentType.STATUTE:
            metadata['act_info'] = self.extract_act_info()
            metadata['current_regs'] = self.extract_current_regulations()
            metadata['revoked_regs'] = self.extract_revoked_regulations()
            metadata['reg_info'] = None
        else:
            metadata['reg_info'] = self.extract_reg_info()
            metadata['act_info'] = None
            metadata['current_regs'] = []
            metadata['revoked_regs'] = []

        return metadata
