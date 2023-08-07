import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

def calculate(stock_symbol, proceed, years_history):

    if not proceed:
        st.warning('The stock does not have an increasing dividend over the past 10 years.')
        return

    stock = yf.Ticker(stock_symbol)

    hist = stock.history(period=f'{years_history}y')

    dividends = stock.dividends

    # Convert index to datetime and ensure they have the same datetime format
    dividends.index = pd.to_datetime(dividends.index)
    hist.index = pd.to_datetime(hist.index)

    # Localize tz-naive datetime objects to UTC timezone
    tz = pytz.timezone('UTC')
    dividends.index = dividends.index.tz_localize(tz)
    hist.index = hist.index.tz_localize(tz)

    # Create a new DataFrame 'combined' to store dividend dates, closing prices, and prices -10 and +60 days from dividends
    combined_data = []
    for div_date, dividend in dividends.items():
        try:
            # Get closing price on dividend date
            price_on_dividend_date = hist.loc[div_date, 'Close']

            # Calculate dates -10 and +60 days from the dividend date
            prev_date = div_date - timedelta(days=10)
            next_date = div_date + timedelta(days=60)

            # Check if the -10 and +60 days dates are business days and get their closing prices
            prev_price = hist.loc[prev_date, 'Close'] if prev_date in hist.index else 'Not a Business Day'
            next_price = hist.loc[next_date, 'Close'] if next_date in hist.index else 'Not a Business Day'

            combined_data.append({
                'Dividend Date': div_date,
                'Dividend Amount': dividend,
                'Price on Dividend Date': price_on_dividend_date,
                '-10 Days Date': prev_date,
                'Price -10 Days': prev_price,
                '+60 Days Date': next_date,
                'Price +60 Days': next_price
            })
        except KeyError:
            continue

    combined = pd.DataFrame(combined_data)

    # Display the combined DataFrame
    st.write("Combined Data:")
    st.dataframe(combined)

def main():
    stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'AAPL')
    years_history = st.sidebar.slider('Select number of years for history:', min_value=10, max_value=20, value=10)
    proceed_button = st.sidebar.button('Execute')

    # Check if dividends are increasing over the past 10 years
    stock = yf.Ticker(stock_symbol)
    dividends = stock.dividends
    proceed = dividends.is_monotonic_increasing

    if proceed_button:
        calculate(stock_symbol, proceed, years_history)

if __name__ == "__main__":
    main()
