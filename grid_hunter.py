##Grid Hunter
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

# === Google Programmable Search (live results) ===
def google_programmable_search(wordbank, output_file, company):
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
    with open(output_file, "w") as f:
        f.write("\n".join(results))
    print(f"Google Search results saved to {output_file}")

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

# === FOIA Archive Search Placeholder ===
def foia_scraper(company, output_file):
    print("Preparing FOIA search URLs...")
    queries = [
        f"site:foia.gov {company}",
        f"site:archives.gov {company} NERC CIP",
        f"site:fec.gov {company} report",
        f"site:energy.gov filetype:pdf {company}"
    ]
    with open(output_file, "w") as f:
        f.write("\n".join(queries))
    print(f"FOIA queries saved to {output_file}")

# === Pastebin-style Sites (placeholder links) ===
def pastebin_sources(company, output_file):
    print("Generating pastebin-style site queries...")
    targets = [
        f"site:pastebin.com {company}",
        f"site:ghostbin.com {company}",
        f"site:controlc.com {company}",
        f"site:pastefs.com {company}"
    ]
    with open(output_file, "w") as f:
        f.write("\n".join(targets))
    print(f"[✔] Paste site queries saved to {output_file}")

# === Postman API Exposure Search ===
def postman_dorks(wordbank, output_file, company):
    print("Checking Postman public exposure dorks...")
    dorks = []
    for category, terms in wordbank.items():
        for term in terms:
            dork = f"site:postman.com {term} {company}"
            dorks.append(f"[{category.upper()}] {dork}")
    with open(output_file, "w") as f:
        f.write("\n".join(dorks))
    print(f"[✔] Postman exposure dorks saved to {output_file}")

# === Interactive Menu ===
def interactive_menu():
    company = input("Enter the electric utility company name to target (e.g. 'CenterPoint Energy'): ").strip()
    github_token = input("Enter your GitHub personal access token: ").strip()
    while True:
        print("\nGRID_HUNTER :: Utility Recon Toolkit")
        print("1. View Wordbank Categories")
        print("2. Add Word to Category")
        print("3. Run GitHub API + Google Search + Yandex URLs")
        print("4. Run FOIA + Pastebin + Postman Checks")
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
            google_programmable_search(wordbank, os.path.join(OUTPUT_DIR, "google_results.txt"), company)
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
    parser = argparse.ArgumentParser(description="GRID_HUNTER - Sensitive Data OSINT Collector for Utility Sector")
    parser.add_argument('--add', help='Term to add to the wordbank')
    parser.add_argument('--to', help='Category to add the term to')
    parser.add_argument('--menu', action='store_true', help='Launch interactive menu')
    parser.add_argument('--dorks', action='store_true', help='Run GitHub, Google, and Yandex dork output')
    parser.add_argument('--company', help='Target utility company name')
    parser.add_argument('--token', help='GitHub token for authenticated API search')
    args = parser.parse_args()

    if args.menu:
        interactive_menu()
    elif args.add and args.to:
        add_to_wordbank(args.to.strip().lower(), args.add.strip().lower())
    elif args.dorks and args.company and args.token:
        wordbank = load_wordbank()
        github_api_search(wordbank, os.path.join(OUTPUT_DIR, "github_results.txt"), args.company, args.token)
        google_programmable_search(wordbank, os.path.join(OUTPUT_DIR, "google_results.txt"), args.company)
        yandex_search_urls(wordbank, os.path.join(OUTPUT_DIR, "yandex_dorks.txt"), args.company)
        foia_scraper(args.company, os.path.join(OUTPUT_DIR, "foia_sources.txt"))
        pastebin_sources(args.company, os.path.join(OUTPUT_DIR, "pastebin_sources.txt"))
        postman_dorks(wordbank, os.path.join(OUTPUT_DIR, "postman_dorks.txt"), args.company)
    else:
        print("[!] No actionable arguments provided. Use --menu or --dorks --company 'CompanyName' --token 'ghp_XXXX' or --add + --to")

if __name__ == '__main__':
    main()

# === Generate Clickable HTML Dork Index ===
def generate_clickable_report(company):
    print("Generating clickable HTML dork index...")
    html_path = os.path.join(OUTPUT_DIR, "gridhunter_dork_index.html")
    sections = [
        ("GitHub", "github_results.txt"),
        ("Google", "google_results.txt"),
        ("Yandex", "yandex_dorks.txt"),
        ("FOIA", "foia_sources.txt"),
        ("Pastebin-style", "pastebin_sources.txt"),
        ("Postman", "postman_dorks.txt")
    ]

    with open(html_path, "w") as html:
        html.write("<html><head><title>GRID_HUNTER Dork Index</title></head><body style='font-family:sans-serif;background:#111;color:#eee;padding:20px;'>\n")
        html.write(f"<h1>GRID_HUNTER Dork Index for {company}</h1>\n")
        for name, file in sections:
            file_path = os.path.join(OUTPUT_DIR, file)
            if os.path.exists(file_path):
                html.write(f"<h2>{name}</h2><ul>\n")
                with open(file_path) as f:
                    for line in f:
                        line = line.strip()
                        if "http" in line or "https" in line:
                            link = line.split()[-1]
                            html.write(f"<li><a href='{link}' style='color:#90ee90;' target='_blank'>{line}</a></li>\n")
                        else:
                            html.write(f"<li>{line}</li>\n")
                html.write("</ul>\n")
        html.write("</body></html>")
    print(f"[✔] Clickable HTML report created: {html_path}")

# === Ask User to Create Clickable HTML Dork Index ===
def prompt_for_clickable_report(company):
    print("\nWould you like to generate a clickable HTML report of all dork links?")
    print("1. No")
    print("2. Yes")
    choice = input("Choose an option: ").strip()
    if choice == '2':
        generate_clickable_report(company)

# === Injected into interactive_menu flow ===
def interactive_menu():
    company = input("Enter the electric utility company name to target (e.g. 'CenterPoint Energy'): ").strip()
    github_token = input("Enter your GitHub personal access token: ").strip()
    while True:
        print("\nGRID_HUNTER :: Utility Recon Toolkit")
        print("1. View Wordbank Categories")
        print("2. Add Word to Category")
        print("3. Run GitHub API + Google Search + Yandex URLs")
        print("4. Run FOIA + Pastebin + Postman Checks")
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
            google_programmable_search(wordbank, os.path.join(OUTPUT_DIR, "google_results.txt"), company)
            yandex_search_urls(wordbank, os.path.join(OUTPUT_DIR, "yandex_dorks.txt"), company)
            prompt_for_clickable_report(company)
        elif choice == '4':
            wordbank = load_wordbank()
            foia_scraper(company, os.path.join(OUTPUT_DIR, "foia_sources.txt"))
            pastebin_sources(company, os.path.join(OUTPUT_DIR, "pastebin_sources.txt"))
            postman_dorks(wordbank, os.path.join(OUTPUT_DIR, "postman_dorks.txt"), company)
            prompt_for_clickable_report(company)
        elif choice == '5':
            break
        else:
            print("[!] Invalid choice")
