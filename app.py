#!/usr/bin/env python3
"""
Apollo Contact Enricher
-------------------------------------------------
From an input CSV (clutch data), fetch executive contacts from Apollo
and write an output CSV with contact-level rows.

Usage:
    python app.py [input.csv] [output.csv]
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('apollo_enricher.log')
    ]
)
logger = logging.getLogger(__name__)

# -------------------- Constants --------------------
SEARCH_ENDPOINT = "https://api.apollo.io/v1/mixed_people/search"
ENRICH_ENDPOINT = "https://api.apollo.io/v1/people/match"
# Preferred titles in order of priority
PREFERRED_TITLES = [
    "Founder", "Growth"
]
# Limit to 3 people per company
PER_PAGE, MAX_PAGES, SLEEP_SECS = 3, 1, 1  # Only 1 page with 3 results
# -------------------------------------------------------


# ---------- Apollo helpers ----------
def get_apollo_headers() -> Dict[str, str]:
    """Get headers with API key for Apollo requests."""
    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        raise ValueError("APOLLO_API_KEY not found in environment variables")
    return {"x-api-key": api_key}


def search_people(company: str, page: int = 1) -> List[dict]:
    """Apollo People Search by domain OR name."""
    try:
        headers = get_apollo_headers()
        params = {
            "page": page,
            "per_page": PER_PAGE * 3,  # Get more results to filter locally
            "sort_by_most_recent_activity": "desc"
        }

    # Domain vs name heuristic
    if "." in company:
        params["q_organization_domains"] = company.lower()
    else:
        params["q_organization_name"] = company

    resp = requests.get(SEARCH_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("people", [])


def enrich_email(person_id: str) -> Optional[str]:
    """Reveal personal email; returns None if fails or no credits."""
    try:
        headers = get_apollo_headers()
        headers["Content-Type"] = "application/json"
        payload = {"id": person_id, "reveal_personal_emails": True}

        resp = requests.post(ENRICH_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if resp.status_code in (402, 429):
            logger.warning("Out of enrichment credits or rate limited")
            return None
            
        resp.raise_for_status()
        return resp.json().get("person", {}).get("email")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error enriching email: {str(e)}")
        return None


def fetch_contacts(company: str, company_domain: str = "") -> List[Tuple[str, str, str, str]]:
    """
    Return (first, last, email, title, linkedin) tuples for a company.
    Uses company_domain if provided, otherwise falls back to company name.
    Returns up to 3 people with preferred titles and valid emails.
    """
    contacts = []
    search_term = company_domain if company_domain and "." in company_domain else company
    
    try:
        # Get more people to increase chances of finding preferred titles
        people = search_people(search_term, page=1)
        if not people:
            return []
            
        # Sort people by title preference
        def title_priority(person):
            title = (person.get("title") or "").lower()
            for i, pref_title in enumerate(PREFERRED_TITLES):
                if pref_title.lower() in title:
                    return i  # Lower index means higher priority
            return len(PREFERRED_TITLES)  # Put non-preferred titles at the end
            
        # Sort people by title priority and take top 10 to process
        sorted_people = sorted(people, key=title_priority)[:10]
        
        for p in sorted_people:
            if len(contacts) >= 3:
                break
                
            email = p.get("email")
            if email == "email_not_unlocked@domain.com":
                email = enrich_email(p["id"]) or None
                
            # Only add if we have a valid email
            if email and email != "email_not_unlocked@domain.com":
                contacts.append((
                    p.get("first_name", ""),
                    p.get("last_name", ""),
                    email,
                    p.get("title") or "No title",
                    p.get("linkedin_url") or "No LinkedIn URL",
                ))
                
        time.sleep(SLEEP_SECS)
        
    except Exception as e:
        print(f"  ⚠️  Error fetching contacts: {str(e)}")
    
    return contacts
    
    return contacts
# ------------------------------------


def process_csv(input_path: str, output_path: str, test_mode: bool = True) -> None:
    print("📂 Loading input file...")
    in_df = pd.read_csv(input_path)
    rows = []
    total_companies = len(in_df)
    
    print(f"🔍 Found {total_companies} companies to process")
    if test_mode:
        print("🧪 Test mode: Only processing first company")
        in_df = in_df.head(1)
    
    for idx, row in in_df.iterrows():
        profile_url = row.get("clutch_profile_url", "")
        company_name = str(row.get("company_name", "")).strip()
        company_domain = str(row.get("company_website_url", "")).strip()
        
        if not company_name:
            print(f"⚠️  Skipping row {idx+1} - No company name")
            continue
            
        print(f"\n🏢 [{idx+1}/{len(in_df)}] Processing: {company_name}")
        if company_domain:
            print(f"  🌐 Using domain: {company_domain}")
        
        try:
            print("  🔄 Fetching contacts...")
            contacts = fetch_contacts(company_name, company_domain)
            print(f"  ✅ Found {len(contacts)} contacts")
            
            for first, last, email, title, linkedin in contacts:
                rows.append({
                    "clutch_profile_url": profile_url,
                    "company_name": company_name,
                    "company_website": company_domain,
                    "person_name": f"{first} {last}".strip(),
                    "role": title,
                    "email": email,
                    "linkedin_url": linkedin,
                })
                print(f"  👤 Added: {first} {last} - {title}")
                
        except Exception as e:
            print(f"  ❌ Error processing {company_name}: {str(e)}")

    out_df = pd.DataFrame(rows)
    out_df.to_csv(output_path, index=False)
    print(f"\n✅  Saved {len(out_df)} contact rows → {output_path}")


def parse_arguments() -> tuple[str, str]:
    """Parse command line arguments."""
    input_file = "clutch_with_sites.csv"
    output_file = "output.csv"
    
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    return input_file, output_file


def main() -> None:
    """Main entry point for the script."""
    try:
        input_file, output_file = parse_arguments()
        
        logger.info(f"Starting Apollo Contact Enricher")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Output file: {output_file}")
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Process the CSV
        process_csv(input_file, output_file, test_mode=False)
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
