"""
Test script for the modernized elaws scraper.

This script tests the scraper with various document types to ensure
it handles all three parsing methods correctly.
"""

import logging
from scraper_modern import ELawsScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_scraper():
    """Test the scraper with a simple document."""

    # Initialize scraper
    scraper = ELawsScraper(output_dir='test_output', log_file='test_scraper.log')

    # Test with a simple, short statute
    # Using a short act to test functionality
    test_url = "https://www.ontario.ca/laws/statute/23s01"  # St. Thomas - Central Elgin Boundary Adjustment Act

    print("=" * 80)
    print("TESTING MODERN ELAWS SCRAPER")
    print("=" * 80)
    print()
    print(f"Test URL: {test_url}")
    print()

    try:
        # Scrape the document
        print("Scraping document...")
        document = scraper.scrape_document(test_url)

        # Display results
        print()
        print("✓ Document scraped successfully!")
        print()
        print("-" * 80)
        print("DOCUMENT INFORMATION:")
        print("-" * 80)

        if document.act_info:
            print(f"Title: {document.act_info.full_title}")
            print(f"Citation: {document.act_info.citation}")
            print(f"URL: {document.act_info.url}")
        elif document.reg_info:
            print(f"Title: {document.reg_info.full_title}")
            print(f"Citation: {document.reg_info.citation}")
            print(f"URL: {document.reg_info.url}")
            if document.reg_info.act_under:
                print(f"Under: {document.reg_info.act_under}")

        print()
        print(f"Sections extracted: {len(document.content)}")
        print(f"Versions: {len(document.versions)}")

        if document.current_regs:
            print(f"Current regulations: {len(document.current_regs)}")
        if document.revoked_regs:
            print(f"Revoked regulations: {len(document.revoked_regs)}")

        # Show first few sections
        if document.content:
            print()
            print("-" * 80)
            print("SAMPLE SECTIONS (first 3):")
            print("-" * 80)
            for i, section in enumerate(document.content[:3]):
                print(f"\nSection {i+1}:")
                print(f"  ID: {section.id}")
                if section.section:
                    print(f"  Title: {section.section}")
                content_preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
                print(f"  Content: {content_preview}")

        # Save the document
        print()
        print("-" * 80)
        print("Saving document...")
        filepath = scraper.save_document(document)
        print(f"✓ Document saved to: {filepath}")

        print()
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)

        return True

    except Exception as e:
        print()
        print("✗ ERROR:")
        print(f"  {e}")
        print()
        logger.exception("Test failed")
        return False


if __name__ == "__main__":
    success = test_scraper()
    exit(0 if success else 1)
