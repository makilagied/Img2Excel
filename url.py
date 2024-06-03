import pandas as pd
from bs4 import BeautifulSoup
import re
import io
import ipywidgets as widgets
from IPython.display import display

# Function to handle file upload
def handle_file_upload(change):
    file = change['new']
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
            r'(\w{2,3})\.?(\d{1,2})\.?(\d{1,2}\.\d{2})\.?(\d{2}/\d{2}/\d{4})\.?(\d{2}/\d{2}/\d{4})\.?(\d{1})\.?(\d{2}/\d{2}/\d{4})\.?(\d+\.\d{4})\.?(\d+\.\d{5})\.?(\d+\.\d{5})'
        )

        # Process the cleaned text to extract structured data
        data = []
        for match in re.finditer(pattern, cleaned_text):
            groups = match.groups()
            data.append(groups)

        if not data:
            print("No matching data found.")
        else:
            # Convert to DataFrame
            columns = ["Bond No.", "Term (Years)", "Coupon (%)", "Issue Date", "Maturity Date", "Deals", "Trade Date", "Amount (Bln TZS)", "Price (%)", "Yield"]
            df = pd.DataFrame(data, columns=columns)

            # Print the DataFrame
            display(df)

            # Save to Excel
            df.to_excel('output.xlsx', index=False)

            print("Data has been successfully written to output.xlsx")


# Create a file uploader widget
file_upload = widgets.FileUpload(accept='.html', multiple=False)

# Attach the file upload handler function
file_upload.observe(handle_file_upload, names='value')

# Display the file uploader widget
display(file_upload)
