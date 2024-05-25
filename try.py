import pandas as pd
from bs4 import BeautifulSoup
import re

# Path to the local HTML file
file_path = "/mnt/c/Users/erick.makilagi/Downloads/dse.htm"  # Update with the actual file path

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
        columns = ["Bond No.", "Term (Years)", "Coupon (%)", "Issue Date", "Maturity Date", "Deals", "Trade Date", "Amount (Bln TZS)", "Price (%)", "Yield"]
        df = pd.DataFrame(data, columns=columns)

        # Print the DataFrame
        print(df)

        # Save to Excel
        df.to_excel('nowsdeoutput.xlsx', index=False)

        print("Data has been successfully written to output.xlsx")
