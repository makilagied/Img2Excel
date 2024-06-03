from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

def process_html_content(content):
    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Extract text from the HTML
    text = soup.get_text(separator=" ")

    # Find the index of the first occurrence of "Bond No."
    start_index = text.find("Bond No.")

    if start_index == -1:
        return None, "Pattern not found in the text."
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
            return None, "No matching data found."
        else:
            # Convert to DataFrame
            columns = ["Bond_No.", "Term (Years)", "Coupon (%)", "Issue Date", "Maturity Date", "Deals", "Trade Date", "Amount (Bln TZS)", "Price (%)", "Yield"]
            df = pd.DataFrame(data, columns=columns)

            # Return DataFrame and success message
            return df, None

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("No selected file")
        return redirect(request.url)
    if file:
        content = file.read().decode('utf-8')  # Ensure the content is decoded to a string
        df, error = process_html_content(content)
        if error:
            flash(error)
            return redirect(request.url)
        else:
            output_file = 'DSE_bond_data.xlsx'
            df.to_excel(output_file, index=False)
            flash(f"Data has been successfully written to {output_file}")
            return redirect(url_for('upload_form'))

if __name__ == "__main__":
    app.run(debug=True)
