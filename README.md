# Ontario E-Laws Scraper - Modern Edition

A modern, unified scraper for extracting Ontario legal documents from [ontario.ca/laws](https://www.ontario.ca/laws).

## Overview

This tool scrapes statutes and regulations from the Ontario e-laws website and saves them as structured JSON files. The modernized version uses a unified architecture that **automatically detects document structure** and produces **consistent output regardless of input format**.

### Key Features

✨ **Unified Parsing** - One interface handles all document types (TOC, LeftHead, NoTOC)
🎯 **Automatic Detection** - Intelligently detects document structure
📦 **Type-Safe** - Modern Python with type hints and dataclasses
🔄 **Consistent Output** - Same JSON format regardless of parsing method
📝 **Comprehensive Logging** - Full visibility into scraping process
🧩 **Modular Design** - Clean separation of concerns

## What's New in the Modern Version

### Before (Original scraper.py)

- ❌ **6 separate parsing functions** (scrape_TOC_law, scrape_TOC_reg, scrape_lefthead_law, etc.)
- ❌ **Duplicate code** - Same logic repeated across functions
- ❌ **Hard to maintain** - Changes needed in multiple places
- ❌ **Manual selection** - Had to know which parser to use

### After (Modern Architecture)

- ✅ **Single unified interface** - `scraper.scrape_document(url)`
- ✅ **Automatic structure detection** - Chooses right parser automatically
- ✅ **DRY principle** - Shared utilities, no duplication
- ✅ **Object-oriented design** - Abstract base classes, polymorphism
- ✅ **Easy to extend** - Add new parsers without touching existing code

## Architecture

```
elaws_scraper/
├── models.py           # Data structures (ActInfo, RegulationInfo, etc.)
├── utils.py            # Shared utilities (process_section, etc.)
├── parsers.py          # Unified parsing framework
│   ├── DocumentParser (ABC)
│   ├── TOCParser      - Traditional table of contents
│   ├── LeftHeadParser - Left-aligned navigation
│   ├── NoTOCParser    - Simple documents without TOC
│   └── ParserFactory  - Auto-detection and parser creation
├── metadata.py         # Metadata extraction (versions, regulations, etc.)
├── scraper_modern.py   # Modern scraper with clean API
├── scraper.py         # Original scraper (kept for reference)
├── error-checker.py   # Validation tool
└── de-duplicator.py   # Deduplication utility
```

## Installation

```bash
# Clone the repository
git clone git@github.com:hordruma/elaws_scraper.git
cd elaws_scraper

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Simple Usage

```python
from scraper_modern import ELawsScraper

# Initialize scraper
scraper = ELawsScraper(output_dir="db")

# Scrape and save a document (automatic structure detection!)
scraper.scrape_and_save("https://www.ontario.ca/laws/statute/90a08")
```

### Command Line

```bash
# Scrape a single document
python scraper_modern.py https://www.ontario.ca/laws/statute/90a08

# Specify custom output directory
python scraper_modern.py https://www.ontario.ca/laws/statute/90a08 my_output
```

## Components

### 1. scraper_modern.py ⭐ NEW!

The modern scraper with unified architecture.

**Features:**
- Automatic structure detection
- Unified parsing interface
- Type-safe data models
- Comprehensive logging

**Usage:**
```python
from scraper_modern import ELawsScraper

scraper = ELawsScraper(output_dir="db", log_file="scraper.log")

# Scrape document (returns LegalDocument object)
document = scraper.scrape_document("https://www.ontario.ca/laws/statute/90a08")

# Access metadata
print(f"Title: {document.act_info.full_title}")
print(f"Sections: {len(document.content)}")

# Save to file
filepath = scraper.save_document(document)
```

### 2. scraper.py (Original)

The original scraper with 6 separate parsing functions.

**Note:** Kept for backward compatibility and reference. **Use scraper_modern.py for new projects!**

**Usage:**
```bash
python scraper.py
```

### 3. error-checker.py

Validates the integrity of scraped data.

**Features:**
- Checks for empty or incomplete data entries
- Identifies missing regulations
- Generates rescrape list

**Usage:**
```bash
python error-checker.py
```

**Requirements:** `laws_and_regs.csv` file in the same directory.

### 4. de-duplicator.py

Removes duplicate entries from scraped data.

**Features:**
- Detection based on `full_title` and `url`
- Options to keep newest or oldest version

**Usage:**
```bash
python de-duplicator.py
```

## Detailed Usage

### Scraping a Single Document

```python
from scraper_modern import ELawsScraper

scraper = ELawsScraper(output_dir="db", log_file="scraper.log")

# Scrape document
document = scraper.scrape_document("https://www.ontario.ca/laws/statute/90a08")

# Access metadata
print(f"Title: {document.act_info.full_title}")
print(f"Citation: {document.act_info.citation}")
print(f"Sections: {len(document.content)}")
print(f"Versions: {len(document.versions)}")

# Access content
for section in document.content[:5]:
    print(f"Section {section.id}: {section.section}")
    print(f"  {section.content[:100]}...")

# Save to file
filepath = scraper.save_document(document)
print(f"Saved to: {filepath}")
```

### Batch Processing

```python
from scraper_modern import ELawsScraper
import pandas as pd

# Load list of laws
laws_df = pd.read_csv("laws_and_regs.csv")

scraper = ELawsScraper(output_dir="db", log_file="batch_scrape.log")

for index, row in laws_df.iterrows():
    try:
        scraper.scrape_and_save(row['url'])
        print(f"✓ Scraped: {row['title']}")
    except Exception as e:
        print(f"✗ Failed: {row['title']} - {e}")
```

### Using the Parser Factory Directly

```python
from parsers import ParserFactory, parse_document

# High-level function (auto-detects and parses)
content = parse_document("https://www.ontario.ca/laws/regulation/990191")

# Or use factory for more control
parser = ParserFactory.create_parser(url)
content = parser.parse()
```

## Output Format

The scraper produces JSON files with this structure:

```json
{
  "act_info": {
    "full_title": "Aggregate Resources Act R.S.O. 1990 c. A.8",
    "act_name_text": "Aggregate Resources Act",
    "citation": "R.S.O. 1990, c. A.8",
    "url": "https://www.ontario.ca/laws/statute/90a08",
    "date_scraped": "2025-12-03 05:00:00"
  },
  "copyright": {
    "Copyright": "© King's Printer for Ontario, 2025."
  },
  "versions": [
    {
      "a_href": "/laws/about-e-laws#ccl",
      "valid_from": "June 1, 2021",
      "valid_to": "current"
    }
  ],
  "current_regs": [...],
  "content": [
    {
      "id": "1",
      "section": "Definitions",
      "content": "In this Act...",
      "raw_html": "<p class='section'>...</p>"
    }
  ]
}
```

**Note:** The output format is **100% backward compatible** with the original scraper.

## How It Works

### Automatic Structure Detection

The modern scraper automatically detects three document types:

1. **TOC (Table of Contents)** - Traditional documents with structured TOC tables
2. **LeftHead** - Documents with left-aligned navigation sidebar
3. **NoTOC** - Simple documents without formal table of contents

```python
# Detection happens automatically!
scraper = ELawsScraper()
document = scraper.scrape_document(url)  # Auto-detects structure
```

### Unified Parsing Interface

All parsers inherit from `DocumentParser` base class:

```python
class DocumentParser(ABC):
    @abstractmethod
    def extract_toc(self) -> Optional[pd.DataFrame]:
        """Extract table of contents"""
        pass

    @abstractmethod
    def extract_sections(self) -> List[Dict[str, Any]]:
        """Extract section content"""
        pass

    def parse(self) -> List[Dict[str, Any]]:
        """Orchestrate extraction and merging"""
        toc_df = self.extract_toc()
        sections = self.extract_sections()
        return self.merge_data(toc_df, sections)
```

## Comparison: Old vs New

### Scraping a Document

**Old Way (scraper.py):**
```python
# Had to manually choose the right function
if has_toc and not is_lefthead:
    if is_regulation:
        content = scrape_TOC_reg(url)
    else:
        content = scrape_TOC_law(url)
elif is_lefthead:
    # ... more manual selection
```

**New Way (scraper_modern.py):**
```python
# Automatic detection and parsing
scraper = ELawsScraper()
document = scraper.scrape_document(url)
```

### Code Maintenance

**Old Way:**
- Change in section processing → Update 6 functions
- New document structure → Add 2 more functions
- Bug fix → Fix in multiple places

**New Way:**
- Change in section processing → Update `utils.process_section()`
- New document structure → Add 1 parser class
- Bug fix → Fix in one place

## Migration from Original Scraper

The modern scraper is **100% backward compatible** with the old scraper's output format.

### What You Can Do:

✅ Use new scraper with existing data processing code
✅ Mix old and new scraped files in the same directory
✅ Migrate gradually - no need to rescrape existing data

### Migration Example:

```python
# OLD: scraper.py
from scraper import scrape_TOC_law
content = scrape_TOC_law(url)

# NEW: scraper_modern.py
from scraper_modern import ELawsScraper
scraper = ELawsScraper()
document = scraper.scrape_document(url)
content = document.content  # Same format!
```

## Advanced Usage

### Custom Parser

```python
from parsers import DocumentParser

class CustomParser(DocumentParser):
    """Handle custom document structure"""

    def extract_toc(self):
        # Your custom TOC extraction
        pass

    def extract_sections(self):
        # Your custom section extraction
        pass

# Use your parser
parser = CustomParser(url)
content = parser.parse()
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

scraper = ELawsScraper(log_file="detailed.log")
scraper.scrape_document(url)
```

## Error Handling

```python
from scraper_modern import ELawsScraper
import logging

logger = logging.getLogger(__name__)
scraper = ELawsScraper()

try:
    document = scraper.scrape_document(url)
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e}")
except Exception as e:
    logger.error(f"Scraping failed: {e}", exc_info=True)
```

## Testing

```bash
# Run test script
python test_scraper.py

# Test specific URL
python scraper_modern.py https://www.ontario.ca/laws/statute/90a08 test_output
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Make your changes or improvements
3. Submit a pull request with a clear description

### Adding a New Parser:

1. Create a new class inheriting from `DocumentParser`
2. Implement `extract_toc()` and `extract_sections()`
3. Add detection logic to `ParserFactory.detect_structure()`
4. Register in `ParserFactory.create_parser()`

## Performance

The modern architecture has **similar performance** to the original:
- Same number of HTTP requests
- Same parsing logic (extracted from original)
- Slightly more overhead from OOP (~negligible)

**Benefits:**
- Easier to optimize (change one place)
- Better error recovery
- More detailed logging

## Troubleshooting

### Import Errors

```bash
pip install -r requirements.txt
```

### Scraping Fails

Check logs:
```python
scraper = ELawsScraper(log_file="debug.log")
# Check debug.log for errors
```

### Different Output

The new scraper should produce identical output. If you notice differences:
- Check same URL and version
- Review log files for warnings
- Compare JSON structures

## License

This tool is for research and educational purposes. The scraped legal documents are © King's Printer for Ontario.

## Summary

The modernized elaws scraper provides:

✅ **Same output format** - 100% backward compatible
✅ **Automatic detection** - No manual parser selection
✅ **Clean code** - No duplication, easy to maintain
✅ **Type safety** - Modern Python with type hints
✅ **Extensible** - Easy to add new parsers
✅ **Well-tested** - Comprehensive logging and error handling

**Use the new scraper for all future scraping tasks!**
