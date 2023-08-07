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

    # Create a new DataFrame 'dividend_dates' to store dividend dates, -10 days dates, +60 days dates, and targets
    dividend_dates_data = []
    for date, dividend in zip(hist.index, hist['Dividends']):
        if dividend > 0:
            try:
                # Calculate dates -10 and +60 days from the dividend date
                prev_date = date - timedelta(days=10)
                next_date = date + timedelta(days=60)

                # Check if the -10 and +60 days dates are business days and add them to the DataFrame
                if prev_date in hist.index and next_date in hist.index:
                    prev_price = hist.loc[prev_date, 'Open']
                    next_price = hist.loc[next_date, 'Open']

                    # Calculate percentage increase
                    percentage_increase = ((next_price - prev_price) / prev_price) * 100

                    # Calculate the target (dividend + opening price on -10 days)
                    target = dividend + prev_price

                    # Calculate the number of days for the closing price to be 50% above the target
                    target_50_percent = target * 1.5
                    days_to_50_percent = ((hist.loc[next_date:, 'Close'] >= target_50_percent).idxmax() - next_date).days

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
                        'Date Used for Target': prev_date.strftime('%Y-%m-%d'),
                        'Days to 50% Above Target': days_to_50_percent,
                        'Target Price at 50%': target_50_percent
                    })
            except KeyError:
                continue

    # Create the dividend_dates DataFrame and sort it by 'Dividend Date' in descending order
    dividend_dates = pd.DataFrame(dividend_dates_data)
    dividend_dates.sort_values(by='Dividend Date', ascending=False, inplace=True)

    # Display the title and the dividend_dates DataFrame with rounded values
    st.write("# Dividend Calculation Data")
    st.write("Dividend Dates with Prices -10 and +60 Days, Targets, and % Increase:")
    st.write(dividend_dates.round({'Dividend Amount': 2, 'Price on Dividend Date': 2,
                                   'Opening Price -10 Days': 2, 'Opening Price +60 Days': 2, 'Target': 2,
                                   'Target Price at 50%': 2}))

def main():
    stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'AAPL')
    years_history = st.sidebar.slider('Select number of years for history:', min_value=1, max_value=20, value=10)
    execute_button = st.sidebar.button('Execute')

    if execute_button:
        calculate(stock_symbol, years_history)

if __name__ == "__main__":
    main()
