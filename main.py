from flask import Flask, render_template, request, send_file, session
import yfinance as yf
import pandas as pd
import openpyxl
import io
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session

def get_financial_ratios(ticker):
    """Get key financial ratios from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Define the ratios to extract
        ratios = {
            'Valuation Ratios': {
                'Market Cap': f"${info.get('marketCap', 'N/A'):,.0f}" if info.get('marketCap') else 'N/A',
                'Price/Earnings (TTM)': f"{info.get('trailingPE', 'N/A')}" if info.get('trailingPE') else 'N/A',
                'Forward P/E': f"{info.get('forwardPE', 'N/A')}" if info.get('forwardPE') else 'N/A',
                'PEG Ratio': f"{info.get('pegRatio', 'N/A')}" if info.get('pegRatio') else 'N/A',
                'Price/Sales': f"{info.get('priceToSalesTrailing12Months', 'N/A')}" if info.get('priceToSalesTrailing12Months') else 'N/A',
                'Price/Book': f"{info.get('priceToBook', 'N/A')}" if info.get('priceToBook') else 'N/A',
                'Enterprise Value/EBITDA': f"{info.get('enterpriseToEbitda', 'N/A')}" if info.get('enterpriseToEbitda') else 'N/A'
            },
            'Profitability Ratios': {
                'Profit Margin': f"{info.get('profitMargins', 'N/A')*100:.2f}%" if info.get('profitMargins') else 'N/A',
                'Operating Margin': f"{info.get('operatingMargins', 'N/A')*100:.2f}%" if info.get('operatingMargins') else 'N/A',
                'Return on Assets': f"{info.get('returnOnAssets', 'N/A')*100:.2f}%" if info.get('returnOnAssets') else 'N/A',
                'Return on Equity': f"{info.get('returnOnEquity', 'N/A')*100:.2f}%" if info.get('returnOnEquity') else 'N/A'
            },
            'Dividend Information': {
                'Dividend Yield': f"{info.get('dividendYield', 'N/A')*100:.2f}%" if info.get('dividendYield') else 'N/A',
                'Dividend Rate': f"${info.get('dividendRate', 'N/A')}" if info.get('dividendRate') else 'N/A',
                'Payout Ratio': f"{info.get('payoutRatio', 'N/A')*100:.2f}%" if info.get('payoutRatio') else 'N/A',
            },
            'Analyst Targets': {
                'Target High Price': f"${info.get('targetHighPrice', 'N/A')}" if info.get('targetHighPrice') else 'N/A',
                'Target Low Price': f"${info.get('targetLowPrice', 'N/A')}" if info.get('targetLowPrice') else 'N/A',
                'Target Mean Price': f"${info.get('targetMeanPrice', 'N/A')}" if info.get('targetMeanPrice') else 'N/A'
            }
        }
        
        return ratios
    except Exception as e:
        print(f"Error fetching financial ratios: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        start_date = request.form['start']
        end_date = request.form['end']
        interval = request.form['interval']
        
        # Download data
        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        except Exception as e:
            error = f"Error downloading data: {str(e)}"
            return render_template('index.html', error=error)
        
        # Validate data
        if data is None or data.empty:
            error = f"No data found for ticker '{ticker}'. Please check the symbol and try again."
            return render_template('index.html', error=error)
        
        # Get financial ratios
        financial_ratios = get_financial_ratios(ticker)
        
        # Store only query parameters in session for download
        session['last_query'] = {
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval
        }
        
        # Show price data table only
        price_table = data.reset_index().to_html(classes='table table-striped', index=False)
        return render_template('index.html', price_table=price_table, ticker=ticker, financial_ratios=financial_ratios)

    return render_template('index.html')

@app.route('/download_excel')
def download_excel():
    import pandas as pd
    if 'last_query' not in session:
        return "No price data available to download.", 400
    q = session['last_query']
    try:
        data = yf.download(q['ticker'], start=q['start_date'], end=q['end_date'], interval=q['interval'])
    except Exception as e:
        return f"Error downloading data: {str(e)}", 400
    if data is None or data.empty:
        return "No price data available to download.", 400
    # Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join([str(i) for i in col if i]) for col in data.columns.values]
    output = io.BytesIO()
    try:
        data.reset_index().to_excel(output, index=False, sheet_name='Price Data')
    except Exception as e:
        return f"Error writing Excel file: {str(e)}", 500
    output.seek(0)
    filename = f"{q['ticker']}_price_data.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
