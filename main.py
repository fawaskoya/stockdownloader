from flask import Flask, render_template, request, send_file, session
import yfinance as yf
import pandas as pd
import io
import os
from datetime import datetime
from functools import lru_cache

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache static files for 5 minutes

# Cache financial ratios data to reduce API calls
@lru_cache(maxsize=32)
def get_financial_ratios(ticker, max_age=3600):  # Cache for 1 hour
    """Get key financial ratios from Yahoo Finance with caching"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info:
            return None
            
        # Organize data into categories with formatting functions
        categories = {
            'Company Information': {
                'Name': info.get('longName', ticker),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Country': info.get('country', 'N/A'),
                'Exchange': info.get('exchange', 'N/A'),
                'Currency': info.get('currency', 'N/A'),
                'Website': info.get('website', 'N/A')
            },
            'Price & Performance': format_price_metrics(info),
            'Valuation Ratios': format_valuation_metrics(info),
            'Financial Health': format_financial_health(info),
            'Profitability': format_profitability(info),
            'Growth Metrics': format_growth_metrics(info),
            'Dividend Information': format_dividend_info(info),
            'Trading Information': format_trading_info(info),
            'Analyst Opinions': format_analyst_info(info)
        }
        
        return categories
    except Exception as e:
        print(f"Error fetching financial ratios: {e}")
        return None

def format_currency(value, symbol='$'):
    """Format a value as currency with appropriate scaling"""
    if not isinstance(value, (int, float)):
        return 'N/A'
    
    if abs(value) >= 1_000_000_000:
        return f"{symbol}{value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{symbol}{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{symbol}{value/1_000:.2f}K"
    else:
        return f"{symbol}{value:.2f}"

def format_percent(value):
    """Format a value as percentage"""
    return f"{value*100:.2f}%" if isinstance(value, (int, float)) else 'N/A'

def format_number(value):
    """Format a number with commas"""
    return f"{value:,.0f}" if isinstance(value, (int, float)) else 'N/A'

def format_decimal(value, decimals=2):
    """Format a decimal value"""
    return f"{value:.{decimals}f}" if isinstance(value, (int, float)) else 'N/A'

def format_price_metrics(info):
    """Format price and performance metrics"""
    return {
        'Current Price': format_currency(info.get('currentPrice', info.get('regularMarketPrice'))),
        '52 Week High': format_currency(info.get('fiftyTwoWeekHigh')),
        '52 Week Low': format_currency(info.get('fiftyTwoWeekLow')),
        '50-Day Avg': format_currency(info.get('fiftyDayAverage')),
        '200-Day Avg': format_currency(info.get('twoHundredDayAverage')),
        'Beta': format_decimal(info.get('beta'))
    }

def format_valuation_metrics(info):
    """Format valuation metrics"""
    return {
        'Market Cap': format_currency(info.get('marketCap')),
        'Enterprise Value': format_currency(info.get('enterpriseValue')),
        'P/E (TTM)': format_decimal(info.get('trailingPE')),
        'Forward P/E': format_decimal(info.get('forwardPE')),
        'PEG Ratio': format_decimal(info.get('pegRatio')),
        'Price/Sales': format_decimal(info.get('priceToSalesTrailing12Months')),
        'Price/Book': format_decimal(info.get('priceToBook')),
        'EV/EBITDA': format_decimal(info.get('enterpriseToEbitda')),
        'EV/Revenue': format_decimal(info.get('enterpriseToRevenue'))
    }

def format_financial_health(info):
    """Format financial health metrics"""
    return {
        'Total Cash': format_currency(info.get('totalCash')),
        'Total Debt': format_currency(info.get('totalDebt')),
        'Debt-to-Equity': format_decimal(info.get('debtToEquity')),
        'Current Ratio': format_decimal(info.get('currentRatio')),
        'Quick Ratio': format_decimal(info.get('quickRatio'))
    }

def format_profitability(info):
    """Format profitability metrics"""
    return {
        'Profit Margin': format_percent(info.get('profitMargins')),
        'Operating Margin': format_percent(info.get('operatingMargins')),
        'Gross Margin': format_percent(info.get('grossMargins')),
        'EBITDA Margin': format_percent(info.get('ebitdaMargins')),
        'Return on Assets': format_percent(info.get('returnOnAssets')),
        'Return on Equity': format_percent(info.get('returnOnEquity'))
    }

def format_growth_metrics(info):
    """Format growth metrics"""
    return {
        'Revenue Growth (YoY)': format_percent(info.get('revenueGrowth')),
        'Earnings Growth (YoY)': format_percent(info.get('earningsGrowth')),
        'EPS Growth (YoY)': format_percent(info.get('earningsQuarterlyGrowth')),
        'Free Cash Flow (TTM)': format_currency(info.get('freeCashflow'))
    }

def format_dividend_info(info):
    """Format dividend information"""
    dividend_yield = info.get('dividendYield', 'N/A')
    if isinstance(dividend_yield, (int, float)):
        dividend_yield_formatted = f"{dividend_yield*100:.2f}%" if dividend_yield < 1 else f"{dividend_yield:.2f}%"
    else:
        dividend_yield_formatted = 'N/A'
        
    return {
        'Dividend Yield': dividend_yield_formatted,
        'Dividend Rate': format_currency(info.get('dividendRate')),
        'Payout Ratio': format_percent(info.get('payoutRatio')),
        'Ex-Dividend Date': info.get('exDividendDate', 'N/A'),
        'Dividend Date': info.get('dividendDate', 'N/A')
    }

def format_trading_info(info):
    """Format trading information"""
    return {
        'Volume': format_number(info.get('volume')),
        'Avg. Volume': format_number(info.get('averageVolume')),
        'Shares Outstanding': format_number(info.get('sharesOutstanding')),
        'Float': format_number(info.get('floatShares')),
        'Short Ratio': format_decimal(info.get('shortRatio')),
        'Short % of Float': format_percent(info.get('shortPercentOfFloat'))
    }

def format_analyst_info(info):
    """Format analyst information"""
    return {
        'Target High Price': format_currency(info.get('targetHighPrice')),
        'Target Low Price': format_currency(info.get('targetLowPrice')),
        'Target Mean Price': format_currency(info.get('targetMeanPrice')),
        'Recommendation': info.get('recommendationKey', 'N/A').capitalize() if info.get('recommendationKey') else 'N/A',
        'No. of Analysts': f"{info.get('numberOfAnalystOpinions')}" if info.get('numberOfAnalystOpinions') else 'N/A'
    }

# Optimize downloading data to avoid redundant calls
def download_stock_data(ticker, start_date, end_date, interval):
    """Download stock data with error handling"""
    try:
        # Download only required columns to save memory
        data = yf.download(
            ticker, 
            start=start_date, 
            end=end_date, 
            interval=interval,
            progress=False,  # Disable progress bar to reduce console output
            threads=True     # Enable multi-threading for faster downloads
        )
        
        # Optimize memory usage by converting to appropriate dtypes
        if not data.empty:
            # Convert float64 to float32 to reduce memory usage
            for col in data.select_dtypes(include=['float64']).columns:
                data[col] = data[col].astype('float32')
                
        return data
    except Exception as e:
        print(f"Error downloading data: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper().strip()
        start_date = request.form['start']
        end_date = request.form['end']
        interval = request.form['interval']
        
        # Download data
        data = download_stock_data(ticker, start_date, end_date, interval)
        
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
        
        # Generate HTML table with optimized settings
        price_table = data.reset_index().to_html(
            classes='table table-striped table-sm', 
            index=False,
            float_format='%.2f',  # Limit decimal places
            border=0,
            justify='left'
        )
        
        return render_template('index.html', price_table=price_table, ticker=ticker, financial_ratios=financial_ratios)

    return render_template('index.html')

@app.route('/download_excel')
def download_excel():
    if 'last_query' not in session:
        return "No price data available to download.", 400
    
    q = session['last_query']
    data = download_stock_data(q['ticker'], q['start_date'], q['end_date'], q['interval'])
    
    if data is None or data.empty:
        return "No price data available to download.", 400
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    try:
        # Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join([str(i) for i in col if i]) for col in data.columns.values]
        
        # Optimize Excel export
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.reset_index().to_excel(
                writer, 
                sheet_name='Price Data',
                index=False,
                float_format="%.2f"  # Limit decimal places
            )
            
            # Set column widths for better readability
            worksheet = writer.sheets['Price Data']
            for i, col in enumerate(data.reset_index().columns):
                max_length = max(data.reset_index()[col].astype(str).map(len).max(), len(str(col)))
                worksheet.column_dimensions[chr(65 + i)].width = max_length + 2
    
    except Exception as e:
        return f"Error writing Excel file: {str(e)}", 500
    
    output.seek(0)
    filename = f"{q['ticker']}_price_data.xlsx"
    return send_file(
        output, 
        as_attachment=True, 
        download_name=filename, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        max_age=300  # Cache for 5 minutes
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
