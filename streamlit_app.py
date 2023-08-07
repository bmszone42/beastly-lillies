import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def calculate(stock_symbol, years_history):

    stock = yf.Ticker(stock_symbol)

    # Get the maximum and minimum available dates for filtering dividend data
    max_date = datetime.now()
    min_date = max_date - timedelta(days=years_history * 365)

    # Get historical stock data
    hist = stock.history(period="max")
    st.write('History data')
    st.write(hist.head())

    # Filter dividend data for the most recent 10 years
    dividends = stock.dividends[(stock.dividends.index >= min_date) & (stock.dividends.index <= max_date)]
    st.write('Dividend data for the most recent 10 years')
    st.write(dividends.head())

    # Convert index to datetime and ensure they have the same datetime format
    hist.index = pd.to_datetime(hist.index)
    dividends.index = pd.to_datetime(dividends.index)

    # Create a new DataFrame 'dividend_dates' to store dividend dates, -10 days dates, and +60 days dates
    dividend_dates_data = []
    for date, dividend in zip(dividends.index, dividends):
        try:
            # Calculate dates -10 and +60 days from the dividend date
            prev_date = date - timedelta(days=10)
            next_date = date + timedelta(days=60)

            # Check if the -10 and +60 days dates are within the available historical data range
            if prev_date >= hist.index.min() and next_date <= hist.index.max():
                prev_price = hist.loc[prev_date, 'Open']
                next_price = hist.loc[next_date, 'Open']

                # Calculate percentage increase
                percentage_increase = ((next_price - prev_price) / prev_price) * 100

                # Calculate the target (dividend + opening price on -10 days)
                target = dividend + prev_price

                dividend_dates_data.append({
                    'Dividend Date': date.strftime('%Y-%m-%d'),
                    'Dividend Amount': dividend,
                    'Price on Dividend Date': hist.loc[date, 'Close'],
                    '-10 Days Date': prev_date.strftime('%Y-%m-%d'),
                    'Opening Price -10 Days': prev_price,
                    '+60 Days Date': next_date.strftime('%Y-%m-%d'),
                    'Opening Price +60 Days': next_price,
                    '% Increase': round(percentage_increase, 1),
                    'Target': target,
                    'Date Used for Target': prev_date.strftime('%Y-%m-%d')
                })
        except KeyError:
            continue

    # Create the dividend_dates DataFrame and sort it by 'Dividend Date' in ascending order
    dividend_dates = pd.DataFrame(dividend_dates_data)
    dividend_dates.sort_values(by='Dividend Date', ascending=True, inplace=True)

    # Display the title and the dividend_dates DataFrame with rounded values
    st.write("# Dividend Calculation Data")
    st.write("Dividend Dates with Prices -10 and +60 Days, Targets, and % Increase:")
    st.write(dividend_dates.round({'Dividend Amount': 2, 'Price on Dividend Date': 2,
                                   'Opening Price -10 Days': 2, 'Opening Price +60 Days': 2, 'Target': 2}))

def main():
    stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'AAPL')
    years_history = st.sidebar.slider('Select number of years for history:', min_value=1, max_value=20, value=10)
    execute_button = st.sidebar.button('Execute')

    if execute_button:
        calculate(stock_symbol, years_history)

if __name__ == "__main__":
    main()
