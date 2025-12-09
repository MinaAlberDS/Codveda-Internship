# Web Scraper (refactored)

This folder contains a refactored version of the original `Web_scrapping.ipynb` into a small package `web_scraper`.

Quick start:

1. Create a virtual environment and install dependencies:

   python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt

2. Run the scraper (uses `Task 1/Links.json` by default):

   python scripts/run_scraper.py --links Links.json --out real_estates_data.json --rate 0.5

Files:
- `web_scraper/` - package with modules: `http.py`, `parsers.py`, `io.py`, `scraper.py`
- `scripts/run_scraper.py` - simple CLI wrapper
- `requirements.txt` - dependencies (updated)
- `notebooks/Web_scrapping_refactored.ipynb` - (suggested) refactored notebook

Notes:
- The package uses a session with retry logic and a small rate limit between requests.
- For tests and CI, use `pytest`.

