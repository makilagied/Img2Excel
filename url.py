import pandas as pd
from bs4 import BeautifulSoup

# Path to the local HTML file
file_path = "/mnt/c/Users/erick.makilagi/Downloads/dse.htm"  # Update with the actual file path

# Read the HTML file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, 'html.parser')

# Extract text from the HTML
text = soup.get_text(separator="\n")

# Split the text into lines
lines = text.split("\n")

# Initialize variables to store data
data = []
current_data = []

# Define a flag to indicate if we are in the relevant data section
in_data_section = False

# Process lines to extract structured data
for line in lines:
    # Check if the line contains "Bond No." indicating the start of relevant data
    if "Bond No." in line:
        in_data_section = True
        continue

    # Check if the line contains "Total" indicating the end of data
    if "Total" in line:
        if current_data:
            data.append(current_data)
        break

    # If we are in the relevant data section, extract the data
    if in_data_section:
        # Split the line by whitespace
        elements = line.split()
        
        # Ensure that the line has the expected number of elements
        if len(elements) == 10:
            current_data.append(elements)
        else:
            # If the line doesn't have the expected number of elements, reset current_data
            if current_data:
                data.append(current_data)
                current_data = []

# Convert to DataFrame
columns = ["Bond No.", "Term (Years)", "Coupon (%)", "Issue Date", "Maturity Date", "Deals", "Trade Date", "Amount (Bln TZS)", "Price (%)", "Yield"]
df = pd.DataFrame(data, columns=columns)

# Save to Excel
excel_file = '12344output.xlsx'
df.to_excel(excel_file, index=False)

print(f"Data has been successfully written to {excel_file}")
