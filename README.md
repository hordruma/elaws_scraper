# Web Scraping Toolkit

## Overview

This repository contains a set of Python scripts designed for web scraping, error checking, and data deduplication. The toolkit is intended to facilitate efficient and robust data extraction from web pages.

The scraper is offered in both python and jupyter notebook versions

## Components

### 1. scraper.py

- **Description**: Dynamic web scraping script using `selenium`, `BeautifulSoup`, and `pandas`.
- **Key Features**:
  - Dynamic data scraping.
  - HTML parsing.
  - Data manipulation and storage.

### 2. error-checker.py

- **Description**: Validates the integrity of scraped data.
- **Key Features**:
  - Checks for empty or incomplete data entries.
  - Ensures data integrity.

### 3. de-duplicator.py

- **Description**: Removes duplicate entries from scraped data.
- **Key Features**:
  - Detection and removal of duplicate data.

## Installation

Clone the repository and install the required dependencies:

```bash
git clone git@github.com:hordruma/elaws_scraper.git
```


Create a new python virtual environment and install dependencies using the command below.

```bash
pip install -r requirements.txt
```

## Usage

### 1. scraper.py

- **Requirements**: Utilizes Selenium and BeautifulSoup for web scraping. Restartable & uses last successful scrape as start point.
- **Functionality**: Designed to scrape data from web pages. It navigates db table of contents pages, extracts desired data for each act/reg, and saves it in a specified format.
- **Usage Note**: Ensure target URLs, data extraction, and parsing logic are configured to match the structure of the web pages you're scraping. Install all necessary libraries and the web driver for Selenium before execution. Script will save laws_and_regs.csv containing a list of items to be scraped and metadata, as well as save_state sets last successful item.

### 2. error-checker.py

- **Requirements**: Requires a CSV file `laws_and_regs.csv` in the same directory. This file is generated when running the scraper.
- **Functionality**: Checks JSON files for errors like empty content or certain missing elements, ensuring the integrity of scraped data.
- **Usage Note**: Verify that the `db_folder` path is set correctly and the `laws_and_regs.csv` file is present. This script is typically run after the scraping process to validate the extracted data.

### 3. de-duplicator.py

- **Requirements**: Intended for removing duplicate JSON files. Duplicates may occur if the scraper encounters an error while running, as it will re-attempt the last successful item.
- **Functionality**: Identifies and removes duplicates based on unique combinations of `full_title` and `url` within JSON files.
- **Usage Note**: Define the folder containing the JSON files to be processed. This tool is useful for cleaning up data post-scraping, ensuring uniqueness in your dataset.

Run each script independently as needed:

```bash
python scraper.py
```

```bash
python error-checker.py
```

```bash
python de-duplicator.py
```

## Contributing

Contributions to this project are very welcome! Together we can create some awesome new stuff. To contribute:

1. Fork the repository.
2. Make your changes or improvements.
3. Submit a pull request with a clear description of the changes.

Your contributions will be reviewed and merged appropriately.
