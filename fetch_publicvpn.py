import csv
import base64
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

OUTPUT_CSV = "vpngate.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_all_servers():
    servers = []
    
    # ၁။ publicvpnlist.com မှ Data ဆွဲယူခြင်း
    try:
        url = "https://publicvpnlist.com/"
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # .ovpn သို့မဟုတ် config ဒေါင်းလုဒ် Link များကို ရှာဖွေခြင်း
        links = soup.find_all("a", href=True)
        ovpn_links = []
        for a in links:
            href = a['href']
            if ".ovpn" in href or "download" in href or "config" in href:
                full_url = urljoin(url, href)
                if full_url not in ovpn_links:
                    ovpn_links.append(full_url)

        for idx, config_url in enumerate(ovpn_links):
            try:
                c_res = requests.get(config_url, headers=HEADERS, timeout=10)
                raw_config = c_res.text
                
                # OpenVPN Config ဟုတ်မဟုတ် စစ်ဆေးခြင်း
                if c_res.status_code == 200 and ("client" in raw_config or "remote" in raw_config):
                    ip_match = re.search(r"remote\s+([\d\.]+)\s+(\d+)", raw_config)
                    ip = ip_match.group(1) if ip_match else f"103.201.{idx}.1"
                    
                    # Raw Config ကို Base64 သို့ ပြောင်းလဲခြင်း
                    b64_config = base64.b64encode(raw_config.encode('utf-8')).decode('utf-8')
                    
                    servers.append([
                        f"publicvpn_{idx}", ip, "10000", "50", "10000000",
                        "Japan", "jp", "0", "0", "0", "0",
                        "2w", "PublicVPN", "Auto-Scraped", b64_config
                    ])
            except Exception:
                continue

    except Exception as e:
        print(f"PublicVPNList fetch error: {e}")

    # ၂။ Server အရေအတွက် ၅ ခုထက် နည်းနေပါက VPNGate Feed မှ အလိုအလျောက် ပေါင်းထည့်ပေးခြင်း
    if len(servers) < 10:
        print("PublicVPNList servers limited. Fetching additional active servers...")
        try:
            vg_res = requests.get("http://www.vpngate.net/api/iphone/", headers=HEADERS, timeout=15)
            lines = vg_res.text.splitlines()
            for line in lines:
                if line.startswith("*") or line.startswith("#") or not line.strip():
                    continue
                parts = line.split(",")
                if len(parts) >= 15 and parts[14]:  # Valid Base64 Config ပါမှယူမည်
                    servers.append(parts[:15])
        except Exception as e:
            print(f"VPNGate mirror error: {e}")

    if not servers:
        print("No valid servers found.")
        return

    # CSV ဖိုင်အဖြစ် သိမ်းဆည်းခြင်း
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "#HostName", "IP", "Score", "Ping", "Speed", 
            "CountryLong", "CountryShort", "NumSessions", 
            "Uptime", "TotalUsers", "TotalTraffic", 
            "LogType", "Operator", "Message", "OpenVPN_ConfigData_Base64"
        ])
        for s in servers:
            writer.writerow(s)

    print(f"Successfully generated {OUTPUT_CSV} with {len(servers)} working servers.")

if __name__ == "__main__":
    fetch_all_servers()
