# Apollo.io Contact Enricher

A Python script that enriches company data from Clutch with executive contact information using the Apollo.io API.

## Features

- Fetches executive contacts from Apollo.io based on company names or domains
- Prioritizes contacts with specific job titles (Founder, Growth, etc.)
- Exports results to a CSV file with contact details
- Handles rate limiting and API errors gracefully

## Prerequisites

- Python 3.7+
- Apollo.io API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Apollo.io API key:
   ```env
   APOLLO_API_KEY=your_apollo_api_key_here
   ```

## Usage

```bash
python app.py input.csv output.csv
```

### Arguments

- `input.csv`: Path to the input CSV file containing company data
- `output.csv`: Path where the output CSV will be saved (default: `output.csv`)

### Input CSV Format

The input CSV should contain at least one of these columns:
- `company_name`: The name of the company
- `company_website_url`: The company's website URL (optional, but recommended for better results)
- `clutch_profile_url`: The Clutch profile URL (optional, included in output)

### Output

The script will generate a CSV file with the following columns:
- `clutch_profile_url`: Original Clutch profile URL
- `company_name`: Company name
- `company_website`: Company website URL
- `person_name`: Contact's full name
- `role`: Contact's job title
- `email`: Contact's email address
- `linkedin_url`: Contact's LinkedIn profile URL

## Configuration

You can modify the following constants in `app.py` to customize the behavior:

- `PREFERRED_TITLES`: List of job titles to prioritize
- `PER_PAGE`: Number of results to fetch per API call
- `MAX_PAGES`: Maximum number of pages to fetch per company
- `SLEEP_SECS`: Delay between API calls to avoid rate limiting

## License

This project is licensed under the MIT License - see the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) file for details.

## Note

- Make sure you have sufficient API credits in your Apollo.io account
- The script includes rate limiting to comply with API usage policies
- For large datasets, consider running the script in batches to avoid hitting API limits
