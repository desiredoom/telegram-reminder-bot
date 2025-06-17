import datetime
import pandas as pd
import requests

# Settings
TELEGRAM_BOT_TOKEN = "7952306960:AAHOcm-KRkUdn0Kvrjf577Z0AzapllYD4NU"
TELEGRAM_CHAT_ID = "894492883"

# Excel file from GitHub
excel_url = "https://raw.githubusercontent.com/desiredoom/telegram-reminder-bot/main/upcoming_installments.xlsx"

try:
    df = pd.read_excel(excel_url)
except Exception as e:
    print("❌ Failed to read Excel file:", e)
    exit(1)

df['Due Date'] = pd.to_datetime(df['Due Date'], format='%d/%m/%Y')

# Use Gulf Standard Time (UTC+4)
target_date = (datetime.datetime.utcnow() + datetime.timedelta(hours=4) + datetime.timedelta(days=2)).date()

matches = df[df['Due Date'].dt.date == target_date]

for _, row in matches.iterrows():
    message = (
        f"📢 Rent Reminder:\n"
        f"🏠 Property: {row['Property Name']}\n"
        f"📅 Due: {row['Due Date'].strftime('%d/%m/%Y')}\n"
        f"💰 Amount: AED {row['Installment Amount (AED)']}\n"
        f"🏦 {row['Deposit Instruction']}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": message})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("❌ Telegram Error:", e.response.text)
