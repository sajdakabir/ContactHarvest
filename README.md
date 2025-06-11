# ContactHarvest 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Python tool for extracting and enriching B2B contact information using the Apollo.io API. Perfect for sales teams, recruiters, and marketers looking to build targeted contact lists.

## ✨ Features

- **Smart Contact Discovery** - Find executive contacts by company name or domain
- **Title-Based Filtering** - Prioritize contacts by job titles (Founder, Growth, etc.)
- **Email Enrichment** - Unlock personal emails when available
- **CSV Export** - Easy integration with your existing workflow
- **Rate Limiting** - Built-in rate limiting to respect API usage policies
- **Error Handling** - Robust error handling and logging
- **CLI Interface** - Simple command-line interface for easy integration

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Valid [Apollo.io](https://www.apollo.io/) API key with sufficient credits

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sajdakabir/ContactHarvest.git
   cd ContactHarvest
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows
   # python -m venv venv
   # .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Apollo.io API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
APOLLO_API_KEY=your_api_key_here
```

### Script Configuration

You can modify the following constants in `app.py` to customize the behavior:

```python
# Preferred job titles (in order of priority)
PREFERRED_TITLES = ["Founder", "Growth"]

# API settings
PER_PAGE = 3        # Number of results per page
MAX_PAGES = 1       # Max pages to fetch per company
SLEEP_SECS = 1      # Delay between API calls (in seconds)
```

## 🛠️ Usage

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

### Basic Usage

```bash
# Process a single company
python app.py input.csv output.csv

# Example with test mode (processes only the first company)
python app.py --test input.csv output.csv

# Show help
python app.py --help
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input.csv` | Path to input CSV file | Required |
| `output.csv` | Path to save output CSV | `output.csv` |
| `--test` | Test mode (process first company only) | `False` |
| `--limit N` | Limit number of companies to process | `None` (all) |

### Input Format

Your input CSV should include these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `company_name` | Yes | The name of the company |
| `company_website_url` | No | Company website (improves match accuracy) |
| `clutch_profile_url` | No | Original Clutch profile URL |

### Output Format

The generated CSV will contain these columns:

| Column | Description |
|--------|-------------|
| `clutch_profile_url` | Original Clutch profile URL |
| `company_name` | Company name |
| `company_website` | Company website |
| `person_name` | Contact's full name |
| `role` | Job title |
| `email` | Email address |
| `linkedin_url` | LinkedIn profile URL |

## 📈 Example

1. **Prepare your input CSV** (`companies.csv`):
   ```csv
   company_name,company_website_url
   Google,google.com
   Microsoft,microsoft.com
   ```

2. **Run the script**:
   ```bash
   python app.py companies.csv results.csv
   ```

3. **Check the results** (`results.csv`):
   ```csv
   clutch_profile_url,company_name,company_website,person_name,role,email,linkedin_url
   ,Google,google.com,Sundar Pichai,CEO,ceo@google.com,linkedin.com/in/sundarpichai
   ,Microsoft,microsoft.com,Satya Nadella,CEO,ceo@microsoft.com,linkedin.com/in/satyanadella
   ```

## 🔧 Advanced Configuration

### Rate Limiting

The script includes built-in rate limiting to prevent hitting Apollo.io's API limits. You can adjust these settings in `app.py`:

```python
# Adjust these values as needed
PER_PAGE = 3      # Results per page (max 100)
MAX_PAGES = 1     # Pages to fetch per company (set to None for all)
SLEEP_SECS = 1    # Delay between API calls (in seconds)
```

### Customizing Contact Search

Modify the `PREFERRED_TITLES` list in `app.py` to prioritize different job titles:

```python
PREFERRED_TITLES = [
    "Founder", "CEO", "CTO", "Growth", "Marketing", 
    "Sales", "Business Development", "VP"
]
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **API Credits**: Each API call consumes credits from your Apollo.io account
- **Rate Limits**: Be mindful of Apollo.io's rate limits to avoid temporary bans
- **Data Privacy**: Ensure compliance with data protection regulations when storing contact information
- **Testing**: Always test with the `--test` flag when making changes
- **Backup**: Keep backups of your input and output files

## 🔗 Related Projects

- [Apollo.io API Documentation](https://apolloio.github.io/api-docs/)
- [Requests Library](https://docs.python-requests.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🙏 Acknowledgments

- Built with ❤️ using Python and ☕ coffee
- Thanks to Apollo.io for their powerful API
- Inspired by the need for better sales intelligence tools
