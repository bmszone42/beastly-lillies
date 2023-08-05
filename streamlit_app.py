import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay

# Function to get stock data
def get_stock_data(ticker_list, start_date, end_date):
    data = {}
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            dividends = dividends[(dividends.index >= start_date) & (dividends.index <= end_date)]
            if not dividends.empty:
                data[ticker] = dividends
        except:
            st.error(f"Error downloading data for {ticker}. Please check the stock symbol.")
    return data

# Function to select a week
def select_week():
    today = datetime.today()
    week_start = st.sidebar.date_input('Start date', today)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

# Main function for the Streamlit app
def main():
    st.title('Dividend Checker')

    # User inputs
    tickers = st.text_input('Enter ticker symbols separated by commas: ')
    tickers = [ticker.strip() for ticker in tickers.split(',')]

    week_start, week_end = select_week()

    if st.button('Find Dividend Stocks'):
        data = get_stock_data(tickers, week_start, week_end)

        for ticker, dividends in data.items():
            st.write(f"{ticker} dividends for selected week:")
            st.write(dividends)

if __name__ == "__main__":
    main()
