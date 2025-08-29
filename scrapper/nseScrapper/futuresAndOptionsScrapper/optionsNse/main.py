from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
from datetime import datetime

# Load symbols and expiries
with open("../../../../inData/nseData/futuresAndOptionsNseData/equityNseData/equityNseOptionsSymbols.txt") as s_file:
    symbols = [line.strip() for line in s_file if line.strip()]

with open("../../../../inData/nseData/futuresAndOptionsNseData/equityNseData/equityNseOptionsExpiries.txt") as e_file:
    expiries = [line.strip() for line in e_file if line.strip()]

# Ensure output folder exists
os.makedirs("../../../../outData", exist_ok=True)

# Setup headless browser
options = Options()
options.headless = True
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)

# Visit NSE homepage once to set cookies
driver.get("https://www.nseindia.com")
time.sleep(3)

# Loop over every symbol and every expiry
timestamp = datetime.now().strftime("%d-%b-%Y")

for expiry in expiries:
    dirName = "EXPIRY_" + expiry
    dirName = dirName + "_GRAB_" + timestamp
    output_dir = os.path.join("../../../../outData/nseData/nseOptionsData", dirName)
    os.makedirs(output_dir, exist_ok=True)

    for symbol in symbols:
        print(f"🔄 Fetching: {symbol} @ {expiry}")
        try:
            # Build URL
            url = f"https://www.nseindia.com/api/option-chain-v3?type=Equity&symbol={symbol}&expiry={expiry}"
            driver.get(url)
            time.sleep(3)

            # Extract JSON from <pre> tag
            json_text = driver.find_element("tag name", "pre").text
            json_filename = os.path.join(output_dir, f"{symbol}_{expiry}_{timestamp}.json".replace(" ", "_"))
            with open(json_filename, "w") as f:
                f.write(json_text)
            print(f"✅ Saved JSON: {json_filename}")

        except Exception as e:
            print(f"❌ Error for {symbol} @ {expiry}: {e}")

driver.quit()
print("✅ All done.")
