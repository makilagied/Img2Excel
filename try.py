import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
import re

# option A Path to the local HTML file
file_path = "/mnt/c/Users/erick.makilagi/Downloads/dse.htm"


#Otion B ask fo file path
# file_path = input("Please enter the file path to the HTML file: ")

# Read the HTML file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, 'html.parser')

# Extract text from the HTML
text = soup.get_text(separator=" ")

# Find the index of the first occurrence of "Bond No."
start_index = text.find("Bond No.")

if start_index == -1:
    print("Pattern not found in the text.")
else:
    # Extract the text after the first occurrence of "Bond No."
    relevant_text = text[start_index:]

    # Clean text: remove all unwanted spaces, tabs, and newlines
    cleaned_text = re.sub(r'\s+', '', relevant_text)

    # Define the regex pattern to match the data entries with flexible separators
    pattern = re.compile(
        r'(\w{3})\.?(\d{1,2})\.?(\d{1,2}\.\d{2})\.?(\d{2}/\d{2}/\d{4})\.?(\d{2}/\d{2}/\d{4})\.?(\d{1})\.?(\d{2}/\d{2}/\d{4})\.?(\d+\.\d{5})\.?(\d+\.\d{4})\.?(\d+\.\d{4})'
    )

    # Process the cleaned text to extract structured data
    data = []
    for match in re.finditer(pattern, cleaned_text):
        data.append(match.groups())

    if not data:
        print("No matching data found.")
    else:
        # Convert to DataFrame
        columns = ["Bond_No.", "Term (Years)", "Coupon (%)", "Issue Date", "Maturity Date", "Deals", "Trade Date", "Amount (Bln TZS)", "Price (%)", "Yield"]
        df = pd.DataFrame(data, columns=columns)

        # Print the DataFrame
        print(df)
        file='DSE_bond_data.xlsx'
        # Save to Excel
        df.to_excel(file, index=False)

        print(f"Data has been successfully written to {file}")


# Connect to PostgreSQL Database
conn = psycopg2.connect(
    dbname="DSE_DB",
    user="postgres",
    password="iTrust123",
    host="192.168.1.18",
    port="5432"
)
cur = conn.cursor()

# Check if any trade dates already exist in the table
trade_dates = tuple(df['Trade Date'].unique())
query = f"SELECT \"TradeDate\" FROM bond_data WHERE \"TradeDate\" IN %s"
cur.execute(query, (trade_dates,))
existing_trade_dates = {row[0] for row in cur.fetchall()}

if existing_trade_dates:
    print(f"Trade dates {existing_trade_dates} already exist. Skipping insertion.")
else:
    # Insert data into PostgreSQL table
    query = """INSERT INTO bond_data ("Bond_No.", "Term", "Coupon", "IssueDate", "MaturityDate", "Deals", "TradeDate", "Amount", "Price", "Yield") 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = [(
        row['Bond_No.'], row['Term (Years)'], row['Coupon (%)'], row['Issue Date'], row['Maturity Date'], 
        row['Deals'], row['Trade Date'], row['Amount (Bln TZS)'], row['Price (%)'], row['Yield']
    ) for _, row in df.iterrows()]
    cur.executemany(query, values)
    print("Data has been successfully inserted.")


# Commit changes
conn.commit()

# Close database connection
cur.close()
conn.close()

