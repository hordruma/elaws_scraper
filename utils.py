"""
Utility functions for the elaws scraper.

This module contains shared functions used across different parsers.
"""

import re
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


def remove_trailing_zero(toc_id: str) -> str:
    """
    Remove trailing '.0' from TOC IDs.

    Args:
        toc_id: The TOC ID string

    Returns:
        The TOC ID with trailing '.0' removed

    Example:
        >>> remove_trailing_zero("1.0")
        "1"
        >>> remove_trailing_zero("1.5")
        "1.5"
    """
    if not isinstance(toc_id, str):
        toc_id = str(toc_id)

    # Remove trailing .0
    if toc_id.endswith('.0'):
        return toc_id[:-2]
    return toc_id


def process_section(section_tag: Tag) -> Dict[str, Any]:
    """
    Process a section HTML element and extract its content.

    Args:
        section_tag: BeautifulSoup Tag representing a section element

    Returns:
        Dictionary containing:
            - id: Section ID (from anchor or element ID)
            - section: Section title (if present)
            - content: Full text content
            - raw_html: Raw HTML string
            - ahref_id: Anchor reference ID (with # prefix)
    """
    section_data = {
        'id': None,
        'section': None,
        'content': '',
        'raw_html': str(section_tag),
        'ahref_id': None
    }

    # Extract ID from anchor tag or element ID
    anchor = section_tag.find('a', class_='anchor')
    if anchor and anchor.get('id'):
        section_data['id'] = anchor.get('id')
        section_data['ahref_id'] = f"#{anchor.get('id')}"
    elif section_tag.get('id'):
        section_data['id'] = section_tag.get('id')
        section_data['ahref_id'] = f"#{section_tag.get('id')}"

    # Extract section title from <b> tag or class_="secttitle"
    title_tag = section_tag.find('b') or section_tag.find(class_='secttitle')
    if title_tag:
        section_data['section'] = title_tag.get_text(strip=True)

    # Extract full text content
    section_data['content'] = section_tag.get_text(strip=True)

    return section_data


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        A safe filename string
    """
    # Remove or replace invalid filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Limit length to avoid filesystem issues
    max_length = 255
    if len(sanitized) > max_length:
        # Keep the extension if present
        parts = sanitized.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            max_name_length = max_length - len(ext) - 1
            sanitized = f"{name[:max_name_length]}.{ext}"
        else:
            sanitized = sanitized[:max_length]

    return sanitized


def get_section_classes() -> list:
    """
    Get the list of CSS classes used for sections.

    Returns:
        List of section class names
    """
    return ['section', 'section-e']


def get_headnote_classes() -> list:
    """
    Get the list of CSS classes used for headnotes.

    Returns:
        List of headnote class names
    """
    return ['headnote', 'headnote-e']


def get_definition_classes() -> list:
    """
    Get the list of CSS classes used for definitions.

    Returns:
        List of definition class names
    """
    return ['definition', 'definition-e']


def build_css_selector(classes: list) -> str:
    """
    Build a CSS selector string for multiple classes.

    Args:
        classes: List of CSS class names

    Returns:
        CSS selector string (e.g., "p.section, p.section-e")
    """
    return ', '.join(f'p.{cls}' for cls in classes)


def extract_table_by_class(soup: BeautifulSoup, class_name: str) -> Optional[Tag]:
    """
    Find a table element by class name.

    Args:
        soup: BeautifulSoup object
        class_name: Class name to search for

    Returns:
        Table Tag if found, None otherwise
    """
    tables = soup.find_all('table')
    for table in tables:
        if class_name in table.get('class', []):
            return table
    return None


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Clean and normalize text content.

    Args:
        text: Text to clean

    Returns:
        Cleaned text or None if input was None
    """
    if text is None:
        return None

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text if text else None


def is_part_heading(toc_id: str) -> bool:
    """
    Check if a TOC ID represents a PART heading.

    Args:
        toc_id: The TOC ID to check

    Returns:
        True if it's a PART heading, False otherwise
    """
    if not toc_id:
        return False
    return str(toc_id).upper().startswith("PART")


def extract_ahref_from_span(span: Tag) -> Optional[str]:
    """
    Extract href value from a span element.

    Args:
        span: BeautifulSoup span Tag

    Returns:
        The href value if found, None otherwise
    """
    ahref = span.find('a', href=True)
    if ahref:
        return ahref['href']
    return None


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def get_request_headers() -> Dict[str, str]:
    """
    Get standard HTTP request headers.

    Returns:
        Dictionary of HTTP headers
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
