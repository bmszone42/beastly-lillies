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

    # Convert index to datetime
    dividends.index = dividends.index.map(lambda x: datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S%z'))

    results = []

    for div_date, dividend in dividends.items():

        first_date = hist.index[0]
        start_date = max(first_date, div_date - timedelta(days=10))

        # Convert datetime to date
        div_date = div_date.date()
        start_date = start_date.date()

        # Make the start_date tz-aware
        tz = pytz.timezone('UTC')
        start_date = tz.localize(datetime.combine(start_date, datetime.min.time()))

        window_data = hist.loc[start_date:div_date + timedelta(days=90)]

        price_on_dividend_date = hist.loc[div_date, 'Open']

        targets = {
            '50%': price_on_dividend_date + dividend * 0.5,
            '75%': price_on_dividend_date + dividend * 0.75,
            '100%': price_on_dividend_date + dividend * 1.0
        }

        target_dates = {key: None for key in targets.keys()}

        for date, row in window_data.iterrows():
            for key, target in targets.items():
                if row['Open'] >= target and target_dates[key] is None:
                    target_dates[key] = date

        result_row = {
            'Dividend Date': div_date.isoformat(),
            'Opening Date': start_date.isoformat(),
            'Price on Dividend Date': price_on_dividend_date,
            '50% Target': targets['50%'],
            '75% Target': targets['75%'],
            '100% Target': targets['100%'],
            '50% Achieved': target_dates['50%'].isoformat() if target_dates['50%'] else None,
            '75% Achieved': target_dates['75%'].isoformat() if target_dates['75%'] else None,
            '100% Achieved': target_dates['100%'].isoformat() if target_dates['100%'] else None,
        }

        results.append(result_row)

    results_df = pd.DataFrame(results)

    st.dataframe(results_df)

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
