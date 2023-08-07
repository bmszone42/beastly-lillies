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

    # Create a list of target months (1 to 12)
    target_months = list(range(1, 13))

    # Create a new DataFrame 'dividend_dates' to store dividend dates, -10 days dates, and +60 days dates
    dividend_dates_data = []
    for month in target_months:
        try:
            # Get the closest dividend date to the target month
            closest_date = hist.loc[hist.index.month == month, 'Dividends'].idxmax()
            dividend = hist.loc[closest_date, 'Dividends']

            # Calculate dates -10 and +60 days from the dividend date
            prev_date = closest_date - timedelta(days=10)
            next_date = closest_date + timedelta(days=60)

            # Check if the -10 and +60 days dates are business days and add them to the DataFrame
            if prev_date in hist.index and next_date in hist.index:
                prev_price = hist.loc[prev_date, 'Open']
                next_price = hist.loc[next_date, 'Open']

                # Calculate percentage increase
                percentage_increase = ((next_price - prev_price) / prev_price) * 100

                # Calculate the target (dividend + opening price on -10 days)
                target = dividend + prev_price

                # Calculate the number of days for the opening price to be greater than the target price
                days_to_target = ((hist.loc[next_date:, 'Open'] >= target).idxmax() - next_date).days

                dividend_dates_data.append({
                    'Dividend Date': closest_date.strftime('%Y-%m-%d'),
                    'Month': month,
                    'Dividend Amount': dividend,
                    'Price on Dividend Date': hist.loc[closest_date, 'Close'],
                    '-10 Days Date': prev_date.strftime('%Y-%m-%d'),
                    'Opening Price -10 Days': prev_price,
                    '+60 Days Date': next_date.strftime('%Y-%m-%d'),
                    'Opening Price +60 Days': next_price,
                    '% Increase': round(percentage_increase, 1),
                    'Target': target,
                    'Date Used for Target': prev_date.strftime('%Y-%m-%d'),
                    'Days to Opening Price > Target': days_to_target
                })
        except ValueError:
            continue

    # Create the dividend_dates DataFrame and sort it by 'Month' and 'Dividend Date' in descending order
    dividend_dates = pd.DataFrame(dividend_dates_data)
    dividend_dates.sort_values(by=['Month', 'Dividend Date'], ascending=[True, False], inplace=True)

    # Display the title and the dividend_dates DataFrame with rounded values
    st.write("# Dividend Calculation Data")
    st.write("Dividend Dates with Prices -10 and +60 Days, Targets, and % Increase:")
    st.write(dividend_dates.round({'Dividend Amount': 2, 'Price on Dividend Date': 2,
                                   'Opening Price -10 Days': 2, 'Opening Price +60 Days': 2, 'Target': 2}))

    # Calculate average days for each 10-year period with dividends in the same month
    avg_days_data = []
    for month in dividend_dates['Month'].unique():
        df_month = dividend_dates[dividend_dates['Month'] == month]
        for i in range(0, len(df_month), 10):
            df_period = df_month.iloc[i:i + 10]
            avg_days = df_period['Days to Opening Price > Target'].mean()
            avg_days_data.append({
                'Month': month,
                'Average Days to Opening Price > Target': avg_days
            })

    # Create the average_days DataFrame
    average_days = pd.DataFrame(avg_days_data)

    # Display the average_days DataFrame
    st.write("# Average Days to Opening Price > Target for Each 10-Year Period")
    st.write(average_days)

def main():
    stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'AAPL')
    years_history = st.sidebar.slider('Select number of years for history:', min_value=1, max_value=20, value=10)
    execute_button = st.sidebar.button('Execute')

    if execute_button:
        calculate(stock_symbol, years_history)

if __name__ == "__main__":
    main()
