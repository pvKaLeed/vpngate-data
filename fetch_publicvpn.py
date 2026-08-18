import csv
import base64
import requests

API_URL = "https://publicvpnlist.com/api/"
OUTPUT_CSV = "vpngate.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_and_convert():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"API Error: HTTP {response.status_code}")
            return

        data = response.json()
        
        # API ၏ Response Structure အလိုက် Server List ကို ဆွဲထုတ်ခြင်း
        servers = data if isinstance(data, list) else data.get("servers", data.get("data", []))

        csv_rows = []
        for index, item in enumerate(servers):
            ip = item.get("ip") or item.get("ip_address") or f"node{index}.publicvpn"
            country = item.get("country") or item.get("country_name") or "Unknown"
            country_code = item.get("country_code") or country[:2].lower()
            
            # OpenVPN Config ကို ရယူခြင်း
            ovpn_raw = item.get("config") or item.get("ovpn") or item.get("ovpn_config") or item.get("base64") or ""
            
            if ovpn_raw:
                # Raw Config Text ဖြစ်နေပါက Base64 သို့ ပြောင်းပါမည်
                if "client" in ovpn_raw or "proto" in ovpn_raw:
                    b64_config = base64.b64encode(ovpn_raw.encode("utf-8")).decode("utf-8")
                else:
                    b64_config = ovpn_raw
            else:
                b64_config = ""

            # Config ပါဝင်သည့် Server များကိုသာ CSV ထဲသို့ ထည့်သွင်းပါမည်
            if b64_config:
                csv_rows.append([
                    f"vpn{index}",          # HostName
                    ip,                    # IP
                    "10000",               # Score
                    "50",                  # Ping
                    "10000000",            # Speed
                    country,               # CountryLong
                    country_code,          # CountryShort
                    "0", "0", "0", "0",    # NumSessions, Uptime, TotalUsers, TotalTraffic
                    "2w",                  # LogType
                    "PublicVPN",           # Operator
                    "Auto-Scraped-API",    # Message
                    b64_config             # OpenVPN_ConfigData_Base64
                ])

        if not csv_rows:
            print("No valid VPN servers found from API.")
            return

        # VPNGate Standard CSV Format ဖြင့် သိမ်းဆည်းခြင်း
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "#HostName", "IP", "Score", "Ping", "Speed", 
                "CountryLong", "CountryShort", "NumSessions", 
                "Uptime", "TotalUsers", "TotalTraffic", 
                "LogType", "Operator", "Message", "OpenVPN_ConfigData_Base64"
            ])
            writer.writerows(csv_rows)

        print(f"Successfully generated {OUTPUT_CSV} with {len(csv_rows)} servers from API.")

    except Exception as e:
        print(f"Error fetching from API: {e}")

if __name__ == "__main__":
    fetch_and_convert()
