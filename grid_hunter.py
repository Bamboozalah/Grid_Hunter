# grid_hunter.py - Recon Tool for Utility Sector OSINT Threat Research

import argparse
import json
import os
from datetime import datetime
import requests

WORDBANK_FILE = "gridhunter_wordbank.json"
OUTPUT_DIR = f"gridhunter_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GOOGLE_CX = os.getenv("GOOGLE_CX")  # Programmable Search Engine ID
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # API Key for Programmable Search

# === Load Wordbank ===
def load_wordbank():
    with open(WORDBANK_FILE, 'r') as f:
        return json.load(f)

# === Add Term to Wordbank ===
def add_to_wordbank(category, new_term):
    with open(WORDBANK_FILE, "r+") as f:
        data = json.load(f)
        if category in data:
            if new_term not in data[category]:
                data[category].append(new_term)
        else:
            data[category] = [new_term]
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
    print(f"[+] Added '{new_term}' to category '{category}'")

# === GitHub Search via API ===
def github_api_search(wordbank, output_file, company, github_token):
    print("Running GitHub API keyword reconnaissance...")
    headers = {"Authorization": f"token {github_token}"}
    results = []
    for category, terms in wordbank.items():
        for term in terms:
            query = f"{term} {company}"
            url = f"https://api.github.com/search/code?q={query.replace(' ', '+')}&per_page=5"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                for item in data.get('items', []):
                    results.append(f"[{category.upper()}] {item['html_url']} in {item['repository']['full_name']}")
            else:
                results.append(f"[{category.upper()}] ERROR: {r.status_code} for query '{query}'")
    with open(output_file, "w") as f:
        f.write("\n".join(results))
    print(f"GitHub API findings saved to {output_file}")

# === Google Programmable Search or Dork Generator ===
def google_search(wordbank, company):
    if GOOGLE_API_KEY and GOOGLE_CX:
        print("Running Google Programmable Search queries...")
        headers = {"Accept": "application/json"}
        results = []
        for category, terms in wordbank.items():
            for term in terms:
                query = f"{term} {company}"
                url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={GOOGLE_CX}&key={GOOGLE_API_KEY}"
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get('items', []):
                        results.append(f"[{category.upper()}] {item.get('title')} → {item.get('link')}")
                else:
                    results.append(f"[{category.upper()}] ERROR: {r.status_code} for query '{query}'")
        with open(os.path.join(OUTPUT_DIR, "google_results.txt"), "w") as f:
            f.write("\n".join(results))
    else:
        print("No Google API key detected — generating manual dork list...")
        dorks = []
        for category, terms in wordbank.items():
            for term in terms:
                dork = f"\"{term}\" AND \"{company}\" filetype:pdf OR filetype:xlsx"
                dorks.append(f"[{category.upper()}] {dork}")
        with open(os.path.join(OUTPUT_DIR, "google_dorks.txt"), "w") as f:
            f.write("\n".join(dorks))

# === Yandex Search URLs ===
def yandex_search_urls(wordbank, output_file, company):
    print("Generating Yandex dorks...")
    queries = []
    for category, terms in wordbank.items():
        for term in terms:
            dork = f"site:* {term} {company}"
            yandex_url = f"https://yandex.com/search/?text={dork.replace(' ', '+')}"
            queries.append(f"[{category.upper()}] {yandex_url}")
    with open(output_file, "w") as f:
        f.write("\n".join(queries))
    print(f"Yandex dork links saved to {output_file}")

# === FOIA, Pastebin, Postman ===
def foia_scraper(company, output_file):
    queries = [
        f"site:foia.gov {company}",
        f"site:archives.gov {company} NERC CIP",
        f"site:fec.gov {company} report",
        f"site:energy.gov filetype:pdf {company}"
    ]
    with open(output_file, "w") as f:
        f.write("\n".join(queries))

def pastebin_sources(company, output_file):
    targets = [
        f"site:pastebin.com {company}",
        f"site:ghostbin.com {company}",
        f"site:controlc.com {company}",
        f"site:pastefs.com {company}"
    ]
    with open(output_file, "w") as f:
        f.write("\n".join(targets))

def postman_dorks(wordbank, output_file, company):
    dorks = []
    for category, terms in wordbank.items():
        for term in terms:
            dork = f"site:postman.com {term} {company}"
            dorks.append(f"[{category.upper()}] {dork}")
    with open(output_file, "w") as f:
        f.write("\n".join(dorks))

# === Interactive Menu ===
def interactive_menu():
    company = input("Enter the electric utility company name to target (e.g. 'Watts Cookin Energy'): ").strip()
    github_token = input("Enter your GitHub personal access token: ").strip()
    while True:
        print("\nGRID_HUNTER :: Utility Recon Toolkit")
        print("1. View Wordbank Categories")
        print("2. Add Word to Category")
        print("3. Run Recon + Google + Yandex")
        print("4. Run FOIA + Pastebin + Postman")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            wordbank = load_wordbank()
            for k in wordbank:
                print(f"- {k}: {', '.join(wordbank[k])}")
        elif choice == '2':
            cat = input("Enter category: ").strip().lower()
            term = input("Enter new term: ").strip().lower()
            add_to_wordbank(cat, term)
        elif choice == '3':
            wordbank = load_wordbank()
            github_api_search(wordbank, os.path.join(OUTPUT_DIR, "github_results.txt"), company, github_token)
            google_search(wordbank, company)
            yandex_search_urls(wordbank, os.path.join(OUTPUT_DIR, "yandex_dorks.txt"), company)
        elif choice == '4':
            wordbank = load_wordbank()
            foia_scraper(company, os.path.join(OUTPUT_DIR, "foia_sources.txt"))
            pastebin_sources(company, os.path.join(OUTPUT_DIR, "pastebin_sources.txt"))
            postman_dorks(wordbank, os.path.join(OUTPUT_DIR, "postman_dorks.txt"), company)
        elif choice == '5':
            break
        else:
            print("[!] Invalid choice")

# === Main Entry ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dorks', action='store_true')
    parser.add_argument('--menu', action='store_true')
    parser.add_argument('--company')
    parser.add_argument('--token')
    args = parser.parse_args()

    if args.menu:
        interactive_menu()
    elif args.dorks and args.company and args.token:
        wordbank = load_wordbank()
        github_api_search(wordbank, os.path.join(OUTPUT_DIR, "github_results.txt"), args.company, args.token)
        google_search(wordbank, args.company)
        yandex_search_urls(wordbank, os.path.join(OUTPUT_DIR, "yandex_dorks.txt"), args.company)
        foia_scraper(args.company, os.path.join(OUTPUT_DIR, "foia_sources.txt"))
        pastebin_sources(args.company, os.path.join(OUTPUT_DIR, "pastebin_sources.txt"))
        postman_dorks(wordbank, os.path.join(OUTPUT_DIR, "postman_dorks.txt"), args.company)
    else:
        print("[!] Missing arguments. Use --menu or --dorks --company 'Name' --token 'ghp_xxx'")

if __name__ == '__main__':
    main()
