
import os
import sys
import time
import requests
from typing import List, Tuple, Optional

# --------------------------------------------------------------------------- #
#  CONFIGURATION
# --------------------------------------------------------------------------- #
#!/usr/bin/env python3
"""
apollo_email_enricher.py
---------------------------------
Scrape executives for a company domain and reveal emails.

Prerequisites:
  pip install requests
Environment:
  export APOLLO_API_KEY="YOUR_REAL_KEY"
Usage:
  python3 apollo_email_enricher.py switchsoftware.io
"""

import os
import sys
import time
import requests
from typing import List, Tuple, Optional

# --------------------------------------------------------------------------- #
# CONFIGURATION
# --------------------------------------------------------------------------- #
API_KEY = "u8iiaA60i2cdgXfNgq9_qg"  # override if you like

DEFAULT_TITLES = [
    "Agency Owner",
    "Business Growth",
    "Partner",
    "CEO",
    "CMO",
    "Tech Lead",
    "Founder",
]

SEARCH_ENDPOINT  = "https://api.apollo.io/v1/mixed_people/search"
ENRICH_ENDPOINT  = "https://api.apollo.io/v1/people/match"   # replaces old “unlock”

PER_PAGE   = 25      # Apollo max
MAX_PAGES  = 10      # safety stop – 250 contacts
SLEEP_SECS = 1       # avoid API throttling
# --------------------------------------------------------------------------- #


def search_people(
    domain: str,
    titles: Optional[List[str]] = None,
    page: int = 1,
    per_page: int = PER_PAGE,
) -> List[dict]:
    """Return raw person dicts from Apollo People Search."""
    headers = {"x-api-key": API_KEY}
    params = {
        "q_organization_domains": domain,
        "page": page,
        "per_page": per_page,
    }
    if titles:
        for title in titles:
            params.setdefault("person_titles[]", []).append(title)

    resp = requests.get(SEARCH_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("people", [])


def enrich_person(person_id: str) -> Optional[str]:
    """
    Reveal a personal email via Apollo People Match.
    Returns the unlocked email string or None.
    """
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "id": person_id,
        "reveal_personal_emails": True,   # consume 1 enrichment credit
    }

    resp = requests.post(ENRICH_ENDPOINT, headers=headers, json=payload, timeout=30)

    if resp.status_code == 402:                  # out of credits
        print("⚠️  Out of enrichment credits.")
        return None
    if resp.status_code != 200:                  # any other error
        print(f"⚠️  Enrich failed ({resp.status_code}): {resp.text[:120]}")
        return None

    return resp.json().get("person", {}).get("email")


def fetch_emails(
    domain: str,
    titles: Optional[List[str]] = None,
    max_pages: int = MAX_PAGES,
) -> List[Tuple[str, str, str, str, str]]:
    """
    Return list of tuples:
      (first_name, last_name, email, title, linkedin_url)
    """
    results = []
    for page in range(1, max_pages + 1):
        people = search_people(domain, titles, page=page)
        if not people:
            break  # no more results

        for p in people:
            email = p.get("email")
            if email == "email_not_unlocked@domain.com":
                email = enrich_person(p["id"]) or email

            results.append(
                (
                    p.get("first_name", ""),
                    p.get("last_name", ""),
                    email or "No email",
                    p.get("title") or "No title",
                    p.get("linkedin_url") or "No LinkedIn URL",
                )
            )
        time.sleep(SLEEP_SECS)
    return results


def pretty_print(domain: str, rows: List[Tuple[str, str, str, str, str]]) -> None:
    print(f"🔍  Searching for people at: {domain}")
    print(f"🌐  Company Website: https://{domain}\n")

    if not rows:
        print("🙅‍  No results found.")
        return

    for first, last, email, title, linkedin in rows:
        print(f"👤 {first} {last}")
        print(f"   🏢 {title}")
        if linkedin and linkedin != "No LinkedIn URL":
            print(f"   🔗 {linkedin}")
        print(f"   ✉️  {email}\n")


def main() -> None:
    domain   = "andersenlab.com"  # change the domain name here
    contacts = fetch_emails(domain, titles=DEFAULT_TITLES)
    pretty_print(domain, contacts)


if __name__ == "__main__":
    main()
