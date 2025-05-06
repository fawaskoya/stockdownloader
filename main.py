
from flask import Flask, render_template, request, send_file
import yfinance as yf
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        start_date = request.form['start']
        end_date = request.form['end']
        
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)
        
        # Save to Excel
        filename = f"{ticker}_{start_date}_to_{end_date}.xlsx"
        data.to_excel(filename)
        
        return send_file(filename, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
