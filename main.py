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
        
        # Company Information
        company_info = {
            'Company Information': {
                'Name': info.get('longName', ticker),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Country': info.get('country', 'N/A'),
                'Exchange': info.get('exchange', 'N/A'),
                'Currency': info.get('currency', 'N/A'),
                'Website': info.get('website', 'N/A')
            }
        }
        
        # Price & Performance Metrics
        performance = {
            'Price & Performance': {
                'Current Price': f"${info.get('currentPrice', info.get('regularMarketPrice', 'N/A')):.2f}" if isinstance(info.get('currentPrice', info.get('regularMarketPrice')), (int, float)) else 'N/A',
                '52 Week High': f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekHigh'), (int, float)) else 'N/A',
                '52 Week Low': f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekLow'), (int, float)) else 'N/A',
                '50-Day Avg': f"${info.get('fiftyDayAverage', 'N/A'):.2f}" if isinstance(info.get('fiftyDayAverage'), (int, float)) else 'N/A',
                '200-Day Avg': f"${info.get('twoHundredDayAverage', 'N/A'):.2f}" if isinstance(info.get('twoHundredDayAverage'), (int, float)) else 'N/A',
                'Beta': f"{info.get('beta', 'N/A'):.2f}" if isinstance(info.get('beta'), (int, float)) else 'N/A'
            }
        }
        
        # Valuation Ratios
        valuation = {
            'Valuation Ratios': {
                'Market Cap': f"${info.get('marketCap', 'N/A'):,.0f}" if isinstance(info.get('marketCap'), (int, float)) else 'N/A',
                'Enterprise Value': f"${info.get('enterpriseValue', 'N/A'):,.0f}" if isinstance(info.get('enterpriseValue'), (int, float)) else 'N/A',
                'P/E (TTM)': f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else 'N/A',
                'Forward P/E': f"{info.get('forwardPE', 'N/A'):.2f}" if isinstance(info.get('forwardPE'), (int, float)) else 'N/A',
                'PEG Ratio': f"{info.get('pegRatio', 'N/A'):.2f}" if isinstance(info.get('pegRatio'), (int, float)) else 'N/A',
                'Price/Sales': f"{info.get('priceToSalesTrailing12Months', 'N/A'):.2f}" if isinstance(info.get('priceToSalesTrailing12Months'), (int, float)) else 'N/A',
                'Price/Book': f"{info.get('priceToBook', 'N/A'):.2f}" if isinstance(info.get('priceToBook'), (int, float)) else 'N/A',
                'EV/EBITDA': f"{info.get('enterpriseToEbitda', 'N/A'):.2f}" if isinstance(info.get('enterpriseToEbitda'), (int, float)) else 'N/A',
                'EV/Revenue': f"{info.get('enterpriseToRevenue', 'N/A'):.2f}" if isinstance(info.get('enterpriseToRevenue'), (int, float)) else 'N/A'
            }
        }
        
        # Financial Health Metrics
        financial_health = {
            'Financial Health': {
                'Total Cash': f"${info.get('totalCash', 'N/A'):,.0f}" if isinstance(info.get('totalCash'), (int, float)) else 'N/A',
                'Total Debt': f"${info.get('totalDebt', 'N/A'):,.0f}" if isinstance(info.get('totalDebt'), (int, float)) else 'N/A',
                'Debt-to-Equity': f"{info.get('debtToEquity', 'N/A'):.2f}" if isinstance(info.get('debtToEquity'), (int, float)) else 'N/A',
                'Current Ratio': f"{info.get('currentRatio', 'N/A'):.2f}" if isinstance(info.get('currentRatio'), (int, float)) else 'N/A',
                'Quick Ratio': f"{info.get('quickRatio', 'N/A'):.2f}" if isinstance(info.get('quickRatio'), (int, float)) else 'N/A'
            }
        }
        
        # Profitability Ratios
        profitability = {
            'Profitability': {
                'Profit Margin': f"{info.get('profitMargins', 'N/A'):.2%}" if isinstance(info.get('profitMargins'), (int, float)) else 'N/A',
                'Operating Margin': f"{info.get('operatingMargins', 'N/A'):.2%}" if isinstance(info.get('operatingMargins'), (int, float)) else 'N/A',
                'Gross Margin': f"{info.get('grossMargins', 'N/A'):.2%}" if isinstance(info.get('grossMargins'), (int, float)) else 'N/A',
                'EBITDA Margin': f"{info.get('ebitdaMargins', 'N/A'):.2%}" if isinstance(info.get('ebitdaMargins'), (int, float)) else 'N/A',
                'Return on Assets': f"{info.get('returnOnAssets', 'N/A'):.2%}" if isinstance(info.get('returnOnAssets'), (int, float)) else 'N/A',
                'Return on Equity': f"{info.get('returnOnEquity', 'N/A'):.2%}" if isinstance(info.get('returnOnEquity'), (int, float)) else 'N/A'
            }
        }
        
        # Growth Metrics
        growth = {
            'Growth Metrics': {
                'Revenue Growth (YoY)': f"{info.get('revenueGrowth', 'N/A'):.2%}" if isinstance(info.get('revenueGrowth'), (int, float)) else 'N/A',
                'Earnings Growth (YoY)': f"{info.get('earningsGrowth', 'N/A'):.2%}" if isinstance(info.get('earningsGrowth'), (int, float)) else 'N/A',
                'EPS Growth (YoY)': f"{info.get('earningsQuarterlyGrowth', 'N/A'):.2%}" if isinstance(info.get('earningsQuarterlyGrowth'), (int, float)) else 'N/A',
                'Free Cash Flow (TTM)': f"${info.get('freeCashflow', 'N/A'):,.0f}" if isinstance(info.get('freeCashflow'), (int, float)) else 'N/A'
            }
        }
        
        # Dividend Information
        dividend = {
            'Dividend Information': {
                'Dividend Yield': f"{info.get('dividendYield', 'N/A'):.2%}" if isinstance(info.get('dividendYield'), (int, float)) else 'N/A',
                'Dividend Rate': f"${info.get('dividendRate', 'N/A'):.2f}" if isinstance(info.get('dividendRate'), (int, float)) else 'N/A',
                'Payout Ratio': f"{info.get('payoutRatio', 'N/A'):.2%}" if isinstance(info.get('payoutRatio'), (int, float)) else 'N/A',
                'Ex-Dividend Date': info.get('exDividendDate', 'N/A'),
                'Dividend Date': info.get('dividendDate', 'N/A')
            }
        }
        
        # Trading Information
        trading = {
            'Trading Information': {
                'Volume': f"{info.get('volume', 'N/A'):,.0f}" if isinstance(info.get('volume'), (int, float)) else 'N/A',
                'Avg. Volume': f"{info.get('averageVolume', 'N/A'):,.0f}" if isinstance(info.get('averageVolume'), (int, float)) else 'N/A',
                'Shares Outstanding': f"{info.get('sharesOutstanding', 'N/A'):,.0f}" if isinstance(info.get('sharesOutstanding'), (int, float)) else 'N/A',
                'Float': f"{info.get('floatShares', 'N/A'):,.0f}" if isinstance(info.get('floatShares'), (int, float)) else 'N/A',
                'Short Ratio': f"{info.get('shortRatio', 'N/A'):.2f}" if isinstance(info.get('shortRatio'), (int, float)) else 'N/A',
                'Short % of Float': f"{info.get('shortPercentOfFloat', 'N/A'):.2%}" if isinstance(info.get('shortPercentOfFloat'), (int, float)) else 'N/A'
            }
        }
        
        # Analyst Targets
        analyst = {
            'Analyst Opinions': {
                'Target High Price': f"${info.get('targetHighPrice', 'N/A'):.2f}" if isinstance(info.get('targetHighPrice'), (int, float)) else 'N/A',
                'Target Low Price': f"${info.get('targetLowPrice', 'N/A'):.2f}" if isinstance(info.get('targetLowPrice'), (int, float)) else 'N/A',
                'Target Mean Price': f"${info.get('targetMeanPrice', 'N/A'):.2f}" if isinstance(info.get('targetMeanPrice'), (int, float)) else 'N/A',
                'Recommendation': info.get('recommendationKey', 'N/A').capitalize() if info.get('recommendationKey') else 'N/A',
                'No. of Analysts': f"{info.get('numberOfAnalystOpinions', 'N/A')}" if info.get('numberOfAnalystOpinions') else 'N/A'
            }
        }
        
        # Combine all sections
        all_data = {}
        for section in [company_info, performance, valuation, profitability, growth, financial_health, dividend, trading, analyst]:
            all_data.update(section)
            
        return all_data
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
