import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def calculate(stock_symbol, years_history):

    stock = yf.Ticker(stock_symbol)

    hist = stock.history(period=f'{years_history}y')
    st.write('History data')
    st.write(hist.head())

    # Convert index to datetime and ensure they have the same datetime format
    hist.index = pd.to_datetime(hist.index)

    st.write("Dates with Closing Prices:")
    for date in hist.index:
        try:
            # Get closing price on the date
            price_on_date = hist.loc[date, 'Close']

            # Calculate dates -10 and +60 days from the date
            prev_date = date - timedelta(days=10)
            next_date = date + timedelta(days=60)

            # Check if the -10 and +60 days dates are business days and get their closing prices
            prev_price = hist.loc[prev_date, 'Close'] if prev_date in hist.index else 'Not a Business Day'
            next_price = hist.loc[next_date, 'Close'] if next_date in hist.index else 'Not a Business Day'

            st.write(f"Date: {date}, Closing Price: {price_on_date}, -10 Days Date: {prev_date}, "
                     f"Price -10 Days: {prev_price}, +60 Days Date: {next_date}, Price +60 Days: {next_price}")
        except KeyError:
            continue

def main():
    stock_symbol = 'AAPL'
    years_history = 10

    calculate(stock_symbol, years_history)

if __name__ == "__main__":
    main()
