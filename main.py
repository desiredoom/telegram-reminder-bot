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

# Parse Due Date column
df['Due Date'] = pd.to_datetime(df['Due Date'], format='%d/%m/%Y')

# Use Gulf Standard Time (UTC+4)
date_gulf = datetime.datetime.utcnow() + datetime.timedelta(hours=4)
target_dates = [
    (date_gulf + datetime.timedelta(days=1)).date(),  # Tomorrow
    (date_gulf + datetime.timedelta(days=2)).date()   # Day after
]

# Filter for matching due dates
matches = df[df['Due Date'].dt.date.isin(target_dates)]

# Send Telegram messages
for _, row in matches.iterrows():
    due_date = row['Due Date'].date()
    days_until_due = (due_date - date_gulf.date()).days

    if days_until_due == 1:
        label = "Due Tomorrow"
    elif days_until_due == 2:
        label = "Due Day After"
    else:
        label = f"Due in {days_until_due} days"

    message = (
        f"📢 Rent Reminder ({label}):\n"
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
