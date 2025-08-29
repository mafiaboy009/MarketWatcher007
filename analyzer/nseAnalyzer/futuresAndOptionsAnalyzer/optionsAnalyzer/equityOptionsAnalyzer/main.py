import json
import csv
import os

rootDir = "../../../../../"
inDataDir = os.path.join(rootDir,"inData")
outDataDir = os.path.join(rootDir,"outData")

#format: EXPIRY_25-Nov-2025_GRAB_29-Aug-2025
grabDate = "29-Aug-2025"
expiryDate = "30-Sep-2025"
#expiryDate = "28-Oct-2025"
dirName = "EXPIRY_" + expiryDate + "_GRAB_" + grabDate
inputDir = os.path.join(rootDir,"outData/nseData/nseOptionsData")
inputDir = os.path.join(inputDir, dirName)
os.makedirs(inputDir, exist_ok=True)

# Load symbols and expiries
symbolFileName = os.path.join(inDataDir,"nseData/futuresAndOptionsNseData/equityNseData/equityNseOptionsSymbols.txt")
with open(symbolFileName,"r") as s_file:
    symbols = [line.strip() for line in s_file if line.strip()]

watchEquity = f"equityOptionsShortlist_ex{expiryDate}_gr{grabDate}.csv"
watchEquity = os.path.join(outDataDir,watchEquity)
rowFields = "\"Symbol\",\"Expiry\",\"Grab\",\"Strike\",\"Spot\",\"CE OI\",\"PE OI\",\"Total OI\""
with open(watchEquity, 'a') as file:
    file.write(rowFields + '\n')  # append a newline character

for symbol in symbols:
    print(f"🔄 Analyzing data of {symbol} @ {grabDate}")
    try:
        jsonFileName = f"{symbol}_{expiryDate}_{grabDate}.json"
        jsonFileName = os.path.join(inputDir, jsonFileName)
        # Parse and write CSV
        try:
            with open(jsonFileName, 'r') as jsonfile:
                optionsData = json.load(jsonfile)
        except FileNotFoundError:
            print(f"File {jsonFileName} not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

        # Extract records
        records = optionsData.get("filtered", {}).get("data", [])

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
            ceSpotPrice = ce.get("underlyingValue", "")
            peSpotPrice = pe.get("underlyingValue", "")

            if peSpotPrice != ceSpotPrice:
                print(f"{symbol} with {expiryDate} has ambiguous value for underlying asset at {strike}")

            ceOI = ce.get("openInterest", "-")
            peOI = pe.get("openInterest", "-")
            totalOI = ceOI + peOI

            if totalOI >= 1000:
                #"\"Symbol\",\"Expiry\",\"Grab\",\"Strike\",\"Spot\",\"CE OI\",\"PE OI\",\"Total OI\""
                writeData = f"{symbol},{expiryDate},{grabDate},{strike},{ceSpotPrice},{ceOI},{peOI},{totalOI}"
                with open(watchEquity, 'a') as file:
                    file.write(writeData + '\n')  # append a newline character

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
        csv_filename = os.path.join(inputDir, f"{symbol}_{expiryDate}_{grabDate}.csv".replace(" ", "_"))
        with open(csv_filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        print(f"✅ CSV saved as {csv_filename}")

    except Exception as e:
        print(f"❌ Error for {symbol} @ {expiry}: {e}")

print("✅ All done.")
