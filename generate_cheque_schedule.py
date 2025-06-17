
import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Load database
conn = sqlite3.connect("khan_properties.db")

# Owner-based deposit instruction mapping
owner_map = {
    "Saira Khan": "Deposit to Saira Khan DIB Account",
    "Saira Khan Damcy Nazario Britto": "Deposit to Saira Khan DIB Account",
    "Khan Ltd": "Deposit to Khan Ltd ADIB Account"
}

# Read properties table
properties_df = pd.read_sql("SELECT * FROM properties;", conn)

# Prepare relevant fields
df = properties_df[['PropertyID', 'Tenant_Name', 'First_Cheque_Date', 'Installments',
                    'Yearly_Rent_AED', 'Building_Name', 'Owner']].dropna(subset=['First_Cheque_Date'])
df['First_Cheque_Date'] = pd.to_datetime(df['First_Cheque_Date'])

# Function to calculate due dates
def get_due_dates(start_date, installments):
    months_apart = 12 // installments
    return [(start_date + relativedelta(months=i * months_apart)) for i in range(installments)]

# Build cheque rows
rows = []
today = datetime.today()
for _, row in df.iterrows():
    due_dates = get_due_dates(row['First_Cheque_Date'], row['Installments'])
    amt = round(row['Yearly_Rent_AED'] / row['Installments']) if row['Installments'] else 0
    instruction = owner_map.get(row['Owner'], "To be confirmed")
    for i, due in enumerate(due_dates, 1):
        if due >= today:
            rows.append({
                "Property Name": row['Building_Name'],
                "Installment No.": i,
                "Due Date": due.strftime('%d/%m/%Y'),
                "Installment Amount (AED)": amt,
                "Deposit Instruction": instruction
            })

# Create DataFrame
cheque_schedule = pd.DataFrame(rows)
cheque_schedule.sort_values(by="Due Date", inplace=True)

# Export
cheque_schedule.to_excel("final_upcoming_installments.xlsx", index=False)
print("Report generated: final_upcoming_installments.xlsx")
