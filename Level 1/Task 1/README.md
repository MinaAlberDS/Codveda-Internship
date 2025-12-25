# Real Estate Web Scraper

This project contains a web scraper for collecting real estate data from realestate.gov.eg.

## Project Structure

```
.
├── data/
│   ├── raw/                    # Raw scraped links
│   │   ├── Links.json          # Initial links file (504 links)
│   │   └── Links(1720 row).json # Extended links file (1720 links)
│   └── processed/              # Processed data files
│       ├── real_estates_data.json              # Main JSON data file
│       ├── real_estates_data.csv               # Main CSV export
│       ├── real_estates_data_except_2025.csv   # Data excluding 2025 properties
│       ├── old_real_estates.csv                # Legacy data file
│       ├── real_estates_data(1).csv            # Additional data batch
│       ├── real_estates_data(2).csv            # Additional data batch
│       └── real_estates_data(new).csv          # Combined new data
├── notebooks/
│   └── Web_scrapping.ipynb     # Main scraping notebook
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Quick Start

1. Create a virtual environment and install dependencies:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Open and run the notebook:

   - Navigate to `notebooks/Web_scrapping.ipynb`
   - The notebook is configured to use the organized folder structure
   - Links are read from `data/raw/Links.json`
   - Output is saved to `data/processed/real_estates_data.json`

## Data Files

- **Raw Data**: Link files stored in `data/raw/`
- **Processed Data**: All scraped and processed data in `data/processed/`
  - JSON format: `real_estates_data.json`
  - CSV formats: Various versions and filtered datasets

## Notes

- The scraper includes rate limiting (0.5s delay between requests)
- Data collection supports filtering by year (e.g., excluding 2025 properties)
- All data has been preserved during organization - no files were deleted

