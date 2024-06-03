import psycopg2
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import re
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'bondmarketdata'
DB_USER = 'bond'
DB_PASSWORD = 'MarketData'

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

from datetime import datetime


def insert_data_to_db(df, conn):
    cur = conn.cursor()
    try:
        # Convert dates to the correct format in the DataFrame
        df['Trade Date'] = pd.to_datetime(df['Trade Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        df['Maturity Date'] = pd.to_datetime(df['Maturity Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        df['Issue Date'] = pd.to_datetime(df['Issue Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        
        # Convert DataFrame to a list of tuples
        data = [tuple(x) for x in df.to_numpy()]
        
        # Check if any of the trade dates already exist in the database
        existing_trade_dates = set()
        cur.execute("SELECT DISTINCT Trade_Date FROM bonds")
        for row in cur.fetchall():
            existing_trade_dates.add(row[0])
        
        new_trade_dates = set(row[6] for row in data)  # Index 6 corresponds to the 'Trade Date' column
        
        if any(trade_date in existing_trade_dates for trade_date in new_trade_dates):
            raise ValueError("Trade date(s) already exist(s) in the database.")
        
        # Insert the data into the database as a single batch operation
        cur.executemany(
            "INSERT INTO bonds (Bond_No, Term_Years, Coupon, Issue_Date, Maturity_Date, Deals, Trade_Date, Amount_Bln_TZS, Price, Yield) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            data
        )
        
        conn.commit()
        cur.close()
        return "Data inserted successfully into the database."
    except Exception as e:
        conn.rollback()  # Rollback any changes made in this transaction
        cur.close()
        return str(e)







@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        content = file.read().decode('utf-8')
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        df, error = process_html_content(content)
        if error:
            flash(error)
            return redirect(request.url)
        else:
            result = insert_data_to_db(df, conn)
            conn.close()
            if "successfully" in result:
                # Save DataFrame to Excel
                output_file = 'DSE_bond_data.xlsx'
                df.to_excel(output_file, index=False)
            
                # Flash message and redirect
                flash(f"{result} Data written to {output_file}")
                return redirect(url_for('upload_form'))
            else:
                flash(result)  # Flash message indicating duplicated trade dates or other errors
                return redirect(url_for('upload_form'))
    else:
        return render_template('upload.html')



if __name__ == "__main__":
    app.run(debug=True)
