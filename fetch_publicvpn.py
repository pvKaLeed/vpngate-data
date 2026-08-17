import csv
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://publicvpnlist.com/"
OUTPUT_CSV = "vpngate.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_base64_config(config_url):
    """ .ovpn ဖိုင်ကို ဒေါင်းလုဒ်ဆွဲပြီး Base64 string အဖြစ် ပြောင်းလဲပေးခြင်း """
    try:
        if not config_url:
            return ""
        res = requests.get(config_url, headers=HEADERS, timeout=10)
        if res.status_code == 200 and ("client" in res.text or "proto" in res.text):
            return base64.b64encode(res.content).decode('utf-8')
    except Exception as e:
        print(f"Config download error ({config_url}): {e}")
    return ""

def scrape_vpn_list():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Failed to load page: HTTP {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        servers = []

        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            col_text = [c.get_text(strip=True) for c in cols]
            
            if len(col_text) >= 4:
                link = row.find("a", href=True)
                if link:
                    config_url = urljoin(URL, link["href"])
                    # OpenVPN profile ကို ဒေါင်းလုဒ်ဆွဲ၍ Base64 ပြောင်းခြင်း
                    base64_config = get_base64_config(config_url)
                    
                    if base64_config:
                        servers.append(col_text + [base64_config])

        if not servers:
            print("No valid server configs found.")
            return

        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["#HostName", "IP", "Score", "Ping", "Speed", "CountryLong", "CountryShort", "NumSessions", "Uptime", "TotalUsers", "TotalTraffic", "LogType", "Operator", "Message", "OpenVPN_ConfigData_Base64"])
            
            for index, s in enumerate(servers):
                ip = s[0] if len(s) > 0 else f"node{index}.publicvpn"
                country = s[1] if len(s) > 1 else "Unknown"
                base64_data = s[-1]

                writer.writerow([
                    f"vpn{index}", ip, "10000", "50", "10000000",
                    country, country[:2].lower(), "0", "0", "0", "0",
                    "2w", "PublicVPN", "Auto-Scraped", base64_data
                ])

        print(f"Successfully generated {OUTPUT_CSV} with {len(servers)} valid servers.")

    except Exception as e:
        print(f"Error scraping PublicVPNList: {e}")

if __name__ == "__main__":
    scrape_vpn_list()
