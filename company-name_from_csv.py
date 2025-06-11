#!/usr/bin/env python3
"""
bulk_apollo_enricher.py
-------------------------------------------------
From an input CSV (clutch data), fetch exec contacts from Apollo
and write an output CSV with contact-level rows.

Usage:
    python3 bulk_apollo_enricher.py input.csv output.csv
"""
import os
import sys
import time
import requests
import pandas as pd
from typing import List, Tuple, Optional

# -------------------- Apollo config --------------------
APOLLO_API_KEY = "your_apollo_api_key_here"
SEARCH_ENDPOINT  = "https://api.apollo.io/v1/mixed_people/search"
ENRICH_ENDPOINT  = "https://api.apollo.io/v1/people/match"
DEFAULT_TITLES   = [
    "Agency Owner", "Business Growth", "Partner",
    "CEO", "CMO", "Tech Lead", "Founder",
]
PER_PAGE, MAX_PAGES, SLEEP_SECS = 25, 10, 1
# -------------------------------------------------------


# ---------- Apollo helpers ----------
def search_people(company: str, page: int = 1) -> List[dict]:
    """Apollo People Search by domain OR name."""
    headers = {"x-api-key": APOLLO_API_KEY}
    params  = {"page": page, "per_page": PER_PAGE}

    # Domain vs name heuristic
    if "." in company:
        params["q_organization_domains"] = company.lower()
    else:
        params["q_organization_name"] = company

    for t in DEFAULT_TITLES:
        params.setdefault("person_titles[]", []).append(t)

    resp = requests.get(SEARCH_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("people", [])


def enrich_email(person_id: str) -> Optional[str]:
    """Reveal personal email; returns None if fails or no credits."""
    headers = {"x-api-key": APOLLO_API_KEY, "Content-Type": "application/json"}
    payload = {"id": person_id, "reveal_personal_emails": True}

    resp = requests.post(ENRICH_ENDPOINT, headers=headers, json=payload, timeout=30)
    if resp.status_code in (402, 429):
        print("⚠️  Out of enrichment credits / rate-limited.")
        return None
    if resp.status_code != 200:
        return None
    return resp.json().get("person", {}).get("email")


def fetch_contacts(company: str) -> List[Tuple[str, str, str, str]]:
    """
    Return (first, last, email, title, linkedin) tuples for a company.
    """
    contacts = []
    for page in range(1, MAX_PAGES + 1):
        people = search_people(company, page=page)
        if not people:
            break
        for p in people:
            email = p.get("email")
            if email == "email_not_unlocked@domain.com":
                email = enrich_email(p["id"]) or email
            contacts.append((
                p.get("first_name", ""),
                p.get("last_name", ""),
                email or "No email",
                p.get("title") or "No title",
                p.get("linkedin_url") or "No LinkedIn URL",
            ))
        time.sleep(SLEEP_SECS)
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
        profile_url = row.get("top_10_clutch_companies.csv", "")
        company_name = str(row.get("company_name", "")).strip()
        
        if not company_name:
            print(f"⚠️  Skipping row {idx+1} - No company name")
            continue
            
        print(f"\n🏢 [{idx+1}/{len(in_df)}] Processing: {company_name}")
        
        try:
            print("  🔄 Fetching contacts...")
            contacts = fetch_contacts(company_name)
            print(f"  ✅ Found {len(contacts)} contacts")
            
            for first, last, email, title, linkedin in contacts:
                rows.append({
                    "profile_url": profile_url,
                    "company_name": company_name,
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


def main() -> None:
    # Default file paths if not provided
    input_file = "top_10_clutch_companies.csv"
    output_file = "output.csv"
    
    # Allow overriding defaults with command line args
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    print(f"🔧 Starting with:\n   Input: {input_file}\n   Output: {output_file}")
    
    if not os.path.exists(input_file):
        sys.exit(f"❌ Input file not found: {input_file}")
    
    process_csv(input_file, output_file, test_mode=True)
    print("\n✨ Processing complete!")


if __name__ == "__main__":
    main()
