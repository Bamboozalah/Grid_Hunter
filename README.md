# GRID_HUNTER

> *Targeted OSINT for Utility Sector Threat Research*

GRID_HUNTER is a tool for tools designed to identify sensitive and mismanaged data related to electric utility companies. It automates dork generation, GitHub code search, Google programmable queries, and vendor or infrastructure keyword exploration.

---

## Use Case

Designed for:
- Threat intelligence analysts in the energy sector
- Utility cybersecurity teams seeking proactive reconnaissance

It provides:
- Predefined and editable keyword categories (wordbank)
- Search support for GitHub, Google, Yandex, FOIA portals, pastebin-style dumps, and Postman public collections
- Clickable HTML report for easy queries

---

##  Features

-  GitHub Code Search via API (live queries)
-  Google Programmable Search *(optional)*
-  Google Dork Generator *(fallback if no API key)*
-  Yandex dork generation
-  FOIA query crafting
-  Pastebin and dump site targeting
-  Postman exposure dorking
-  Editable term wordbank
-  Clickable HTML report of dorks and results

---

## Setup

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/grid_hunter.git
cd grid_hunter
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Docker Option

### Build Image
```bash
docker build -t grid_hunter .
```

### Run Interactively
```bash
# Minimal mode (no Google search)
docker run -it \
  -v "$PWD:/app" \
  grid_hunter --menu

# Full mode (with Google Search)
docker run -it \
  -e GOOGLE_API_KEY="your_api_key" \
  -e GOOGLE_CX="your_cx_id" \
  -v "$PWD:/app" \
  grid_hunter --menu
```

---

## Usage Modes

### Interactive Menu Mode
```bash
python3 grid_hunter.py --menu
```
- View/edit wordbank
- Run searches for a specified utility company
- Optionally generate clickable report

### Command-Line Dork Collection
```bash
# Minimal mode (uses static Google dorks)
python3 grid_hunter.py --dorks \
  --company "Watt's Cookin Energy" \
  --token ghp_yourgithubtoken

# Full mode (live Google search results)
GOOGLE_API_KEY=your_key GOOGLE_CX=your_cx \
python3 grid_hunter.py --dorks \
  --company "Watt's Cookin Energy" \
  --token ghp_yourgithubtoken
```

---

## Output
Each run creates a timestamped folder like:
```
gridhunter_results_20250404_143301/
├── github_results.txt
├── google_results.txt  # If using API
├── google_dorks.txt    # If using fallback
├── yandex_dorks.txt
├── foia_sources.txt
├── pastebin_sources.txt
├── postman_dorks.txt
└── gridhunter_dork_index.html   # click-to-search index
```

---

## Wordbank Customization
Edit `gridhunter_wordbank.json` to update scoped search terms for:
- passwords, credentials, and secrets
- vendor and system names (e.g., Siemens, SEL, ABB)
- job roles (e.g., "OT engineer", "relay technician")
- OT schema indicators (e.g., "ladder logic", "PI historian")

Use `--menu` to add words live.

---

Don't use for nefarious purposes--keep yo' hands to yourself or you can cache me outside 
- (•_•)
- ( •_•)>⌐■-■
- (⌐■_■)

