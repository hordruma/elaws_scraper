"""
Data models for the elaws scraper.

This module defines the data structures used throughout the scraper,
ensuring consistent output format regardless of parsing method.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    """Types of legal documents."""
    STATUTE = "statute"
    REGULATION = "regulation"


class StructureType(Enum):
    """Types of document structure detected."""
    TOC = "toc"  # Traditional table of contents
    LEFTHEAD = "lefthead"  # Left-aligned navigation sidebar
    NOTOC = "notoc"  # No table of contents
    UNKNOWN = "unknown"


@dataclass
class SectionContent:
    """Represents a single section of legal content."""
    id: str
    section: Optional[str] = None
    content: str = ""
    raw_html: str = ""
    ahref_id: Optional[str] = None
    toc_id: Optional[str] = None
    part_id: Optional[str] = None
    part_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, filtering out None values for cleaner output."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class VersionInfo:
    """Represents version information for a legal document."""
    a_href: str
    valid_from: str
    valid_to: str = "current"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "a_href": self.a_href,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to
        }


@dataclass
class RegulationReference:
    """Represents a reference to a regulation."""
    a_href: str
    citation: str
    title: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_reg_a_href": self.a_href,
            "current_reg_citation": self.citation,
            "current_reg_title": self.title
        }


@dataclass
class ActInfo:
    """Metadata for an Act/Statute."""
    full_title: str
    act_name_text: str
    citation: str
    url: str
    date_scraped: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RegulationInfo:
    """Metadata for a Regulation."""
    full_title: str
    reg_name_text: str
    citation: str
    url: str
    act_under: Optional[str] = None
    date_scraped: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        if result.get("act_under") is None:
            result.pop("act_under", None)
        return result


@dataclass
class CopyrightInfo:
    """Copyright information."""
    copyright_text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"Copyright": self.copyright_text}


@dataclass
class LegalDocument:
    """
    Unified data model for a legal document (Act or Regulation).

    This class ensures consistent output format regardless of the parsing
    method used to extract the data.
    """
    document_type: DocumentType
    act_info: Optional[ActInfo] = None
    reg_info: Optional[RegulationInfo] = None
    copyright: Optional[CopyrightInfo] = None
    versions: List[VersionInfo] = field(default_factory=list)
    current_regs: List[RegulationReference] = field(default_factory=list)
    revoked_regs: List[RegulationReference] = field(default_factory=list)
    content: List[SectionContent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary in the standard output format.

        Returns a dictionary that matches the existing JSON format used
        by the scraper, ensuring backward compatibility.
        """
        result = {}

        # Add act or regulation info
        if self.document_type == DocumentType.STATUTE and self.act_info:
            result["act_info"] = self.act_info.to_dict()
        elif self.document_type == DocumentType.REGULATION and self.reg_info:
            result["reg_info"] = self.reg_info.to_dict()

        # Add copyright
        if self.copyright:
            result["copyright"] = self.copyright.to_dict()

        # Add versions
        if self.versions:
            result["versions"] = [v.to_dict() for v in self.versions]

        # Add current regulations (for Acts only)
        if self.current_regs:
            result["current_regs"] = [r.to_dict() for r in self.current_regs]

        # Add revoked regulations (for Acts only)
        if self.revoked_regs:
            result["revoked_regs"] = [r.to_dict() for r in self.revoked_regs]

        # Add content
        result["content"] = [c.to_dict() for c in self.content]

        return result

    def get_filename(self) -> str:
        """
        Generate the filename for this document.

        Format: {full_title} + {valid_from} - {valid_to} + {timestamp}.json
        """
        # Get the appropriate info object
        info = self.act_info if self.document_type == DocumentType.STATUTE else self.reg_info
        if not info:
            raise ValueError("Document must have act_info or reg_info")

        # Get version info
        version_str = "unknown - current"
        if self.versions:
            latest = self.versions[0]  # Assuming first version is the current one
            version_str = f"{latest.valid_from} - {latest.valid_to}"

        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H%M%S")

        # Sanitize title for filename
        safe_title = "".join(c for c in info.full_title if c.isalnum() or c in (' ', '-', '_', '.')).strip()

        return f"{safe_title} + {version_str} + {timestamp}.json"
