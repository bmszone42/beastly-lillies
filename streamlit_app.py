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

    # Create a new DataFrame 'dividend_dates' to store dividend dates, -10 days dates, and +60 days dates
    dividend_dates_data = []
    for date, dividend in zip(hist.index, hist['Dividends']):
        if dividend > 0:
            try:
                # Calculate dates -10 and +60 days from the dividend date
                prev_date = date - timedelta(days=10)
                next_date = date + timedelta(days=60)

                # Check if the -10 and +60 days dates are business days and add them to the DataFrame
                if prev_date in hist.index and next_date in hist.index:
                    prev_price = hist.loc[prev_date, 'Close']
                    next_price = hist.loc[next_date, 'Close']

                    # Calculate percentage increase
                    percentage_increase = ((next_price - prev_price) / prev_price) * 100

                    dividend_dates_data.append({
                        'Dividend Date': date.strftime('%Y-%m-%d'),
                        'Dividend Amount': dividend,
                        'Price on Dividend Date': hist.loc[date, 'Close'],
                        '-10 Days Date': prev_date.strftime('%Y-%m-%d'),
                        'Price -10 Days': prev_price,
                        '+60 Days Date': next_date.strftime('%Y-%m-%d'),
                        'Price +60 Days': next_price,
                        '% Increase': round(percentage_increase, 1)
                    })
            except KeyError:
                continue

    # Create the dividend_dates DataFrame
    dividend_dates = pd.DataFrame(dividend_dates_data)

    # Display the title and the dividend_dates DataFrame with rounded values
    st.write("# Dividend Calculation Data")
    st.write("Dividend Dates with Prices -10 and +60 Days and % Increase:")
    st.write(dividend_dates.round({'Dividend Amount': 2, 'Price on Dividend Date': 2,
                                   'Price -10 Days': 2, 'Price +60 Days': 2}))

def main():
    stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'AAPL')
    years_history = st.sidebar.slider('Select number of years for history:', min_value=1, max_value=20, value=10)
    execute_button = st.sidebar.button('Execute')

    if execute_button:
        calculate(stock_symbol, years_history)

if __name__ == "__main__":
    main()
