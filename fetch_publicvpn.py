import csv
import requests
from bs4 import BeautifulSoup

URL = "https://publicvpnlist.com/"
OUTPUT_CSV = "vpngate.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_vpn_list():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Failed: HTTP {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        servers = []

        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            col_text = [c.get_text(strip=True) for c in cols]
            if len(col_text) >= 4:
                link = row.find("a", href=True)
                config_url = link["href"] if link else ""
                servers.append(col_text + [config_url])

        if not servers:
            print("No server data found.")
            return

        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["#HostName", "IP", "Score", "Ping", "Speed", "CountryLong", "CountryShort", "NumSessions", "Uptime", "TotalUsers", "TotalTraffic", "LogType", "Operator", "Message", "OpenVPN_ConfigData_Base64"])
            
            for index, s in enumerate(servers):
                ip = s[0] if len(s) > 0 else f"node{index}.publicvpn"
                country = s[1] if len(s) > 1 else "Unknown"
                config = s[-1] if len(s) > 2 else ""

                writer.writerow([
                    f"vpn{index}", ip, "10000", "50", "10000000",
                    country, country[:2].lower(), "0", "0", "0", "0",
                    "2w", "PublicVPN", "Auto-Scraped", config
                ])

        print(f"Successfully saved {len(servers)} servers to {OUTPUT_CSV}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_vpn_list()
