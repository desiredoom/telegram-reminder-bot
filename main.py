import datetime
import pandas as pd
import requests

# Settings
TELEGRAM_BOT_TOKEN = "7952306960:AAHOcm-KRkUdn0Kvrjf577Z0AzapllYD4NU"
TELEGRAM_CHAT_ID = "894492883"

# Excel file from GitHub
excel_url = "https://raw.githubusercontent.com/desiredoom/telegram-reminder-bot/main/Upcoming_Events.xlsx"

# Load the Excel
try:
    df = pd.read_excel(excel_url)
except Exception as e:
    print("❌ Failed to read Excel file:", e)
    exit(1)

# Parse 'Date' column
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# Use Gulf Standard Time (UTC+4)
now_gulf = datetime.datetime.utcnow() + datetime.timedelta(hours=4)
target_dates = [
    (now_gulf + datetime.timedelta(days=1)).date(),
    (now_gulf + datetime.timedelta(days=2)).date()
]

# Filter for matching due dates
matches = df[df['Date'].dt.date.isin(target_dates)]

# Iterate through rows and send messages
for _, row in matches.iterrows():
    due_date = row['Date'].date()
    days_until_due = (due_date - now_gulf.date()).days
    label = "Due Tomorrow" if days_until_due == 1 else "Due Day After"

    reminder_type = str(row['Event']).strip().lower()
    property_name = row.get('Property Name', 'Unknown Property')
    amount = row.get('Amount', '')
    comment = row.get('Comments', '')
    comment_line = f"\n📝 Note: {comment}" if pd.notna(comment) and str(comment).strip() else ""

    date_str = due_date.strftime('%d/%m/%Y')

    if reminder_type == "rent due":
        message = (
            f"📢 Rent Due ({label}):\n"
            f"🏠 Property: {property_name}\n"
            f"📅 Due: {date_str}\n"
            f"💰 Amount: AED {amount}{comment_line}"
        )

    elif reminder_type == "renewal notice due":
        message = (
            f"📢 Renewal Notice Due ({label}):\n"
            f"🏠 Property: {property_name}\n"
            f"📅 Contract Expiry: {date_str}{comment_line}"
        )

    elif reminder_type == "service charge due":
        message = (
            f"📢 Service Charge Due ({label}):\n"
            f"🏢 Property: {property_name}\n"
            f"📅 Due: {date_str}\n"
            f"💰 Amount: AED {amount}{comment_line}"
        )

    elif reminder_type == "viewings start":
        message = (
            f"📢 Viewings Start ({label}):\n"
            f"🏠 Property: {property_name}\n"
            f"📅 Starts On: {date_str}{comment_line}"
        )

    elif reminder_type == "renewal completion due":
        message = (
            f"📢 Renewal Completion Due ({label}):\n"
            f"🏠 Property: {property_name}\n"
            f"📅 Completion Date: {date_str}{comment_line}"
        )

    elif reminder_type == "repair due":
        message = (
            f"📢 Repair / Inspection Due ({label}):\n"
            f"🏠 Property: {property_name}\n"
            f"📅 Scheduled For: {date_str}{comment_line}"
        )

    else:
        message = (
            f"📢 Reminder ({label}):\n"
            f"🏠 Property: {property_name}\n"
            f"📅 Date: {date_str}\n"
            f"🔔 Type: {row['Reminder Type']}{comment_line}"
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": message})

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("❌ Telegram Error:", e.response.text)
