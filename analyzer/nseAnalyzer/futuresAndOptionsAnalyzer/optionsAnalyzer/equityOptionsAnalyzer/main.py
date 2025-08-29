from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import csv
import os
from datetime import datetime

current_working_dir = os.getcwd()
print(current_working_dir)


# Create timestamped folder inside 'data'
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.join("../../../../../data", timestamp)
os.makedirs(output_dir, exist_ok=True)

# Load symbols and expiries
with open("../../../../../inData/nseData/futuresAndOptionsNseData/indexNseData/indexNseOptionsSymbols.txt") as s_file:
    symbols = [line.strip() for line in s_file if line.strip()]

with open("../../../../../inData/nseData/futuresAndOptionsNseData/indexNseData/indexNseOptionsExpiries.txt") as e_file:
    expiries = [line.strip() for line in e_file if line.strip()]

# Ensure output folder exists
os.makedirs("../../../../../data", exist_ok=True)

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
for symbol in symbols:
    for expiry in expiries:
        print(f"🔄 Fetching: {symbol} @ {expiry}")
        try:
            # Build URL
            url = f"https://www.nseindia.com/api/option-chain-v3?type=Equity&symbol={symbol}&expiry={expiry}"
            driver.get(url)
            time.sleep(3)

            # Extract JSON from <pre> tag
            json_text = driver.find_element("tag name", "pre").text
            json_filename = os.path.join(output_dir, f"{symbol}_{expiry}.json".replace(" ", "_"))
            with open(json_filename, "w") as f:
                f.write(json_text)
            print(f"✅ Saved JSON: {json_filename}")

            # Parse and write CSV
            data = json.loads(json_text)

            # Extract records
            records = data.get("records", {}).get("data", [])

            # Output columns (mirroring image layout)
            headers = [
                # CALL side
                "CALL_OI", "CALL_CHNG_IN_OI", "CALL_VOLUME", "CALL_IV", "CALL_LTP", "CALL_CHNG",
                "CALL_BID_QTY", "CALL_BID", "CALL_ASK", "CALL_ASK_QTY",
                # STRIKE
                "STRIKE",
                # PUT side
                "PUT_BID_QTY", "PUT_BID", "PUT_ASK", "PUT_ASK_QTY", "PUT_CHNG", "PUT_LTP",
                "PUT_IV", "PUT_VOLUME", "PUT_CHNG_IN_OI", "PUT_OI"
            ]

            # Extract relevant data
            rows = []
            for record in records:
                ce = record.get("CE", {})
                pe = record.get("PE", {})
                strike = record.get("strikePrice", "")

                row = {
                    # CALLS
                    "CALL_OI": ce.get("openInterest", "-") or "-",
                    "CALL_CHNG_IN_OI": ce.get("changeinOpenInterest", "-") or "-",
                    "CALL_VOLUME": ce.get("totalTradedVolume", "-") or "-",
                    "CALL_IV": ce.get("impliedVolatility", "-") or "-",
                    "CALL_LTP": ce.get("lastPrice", "-") or "-",
                    "CALL_CHNG": ce.get("change", "-") or "-",
                    "CALL_BID_QTY": ce.get("buyQuantity1", "-") or "-",
                    "CALL_BID": ce.get("buyPrice1", "-") or "-",
                    "CALL_ASK": ce.get("sellPrice1", "-") or "-",
                    "CALL_ASK_QTY": ce.get("sellQuantity1", "-") or "-",

                    # STRIKE
                    "STRIKE": strike or "-",

                    # PUTS
                    "PUT_BID_QTY": pe.get("buyQuantity1", "-") or "-",
                    "PUT_BID": pe.get("buyPrice1", "-") or "-",
                    "PUT_ASK": pe.get("sellPrice1", "-") or "-",
                    "PUT_ASK_QTY": pe.get("sellQuantity1", "-") or "-",
                    "PUT_CHNG": pe.get("change", "-") or "-",
                    "PUT_LTP": pe.get("lastPrice", "-") or "-",
                    "PUT_IV": pe.get("impliedVolatility", "-") or "-",
                    "PUT_VOLUME": pe.get("totalTradedVolume", "-") or "-",
                    "PUT_CHNG_IN_OI": pe.get("changeinOpenInterest", "-") or "-",
                    "PUT_OI": pe.get("openInterest", "-") or "-",
                }

                rows.append(row)

            # Save to CSV
            csv_filename = os.path.join(output_dir, f"{symbol}_{expiry}.csv".replace(" ", "_"))
            with open(csv_filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            print(f"✅ CSV saved as {csv_filename}")

        except Exception as e:
            print(f"❌ Error for {symbol} @ {expiry}: {e}")

driver.quit()
print("✅ All done.")
