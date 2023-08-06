import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import timedelta

def calculate(stock_symbol, proceed, years_history):
    if not proceed:
        st.warning('The stock does not have an increasing dividend over the past 10 years.')
        return

    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period=f'{years_history}y')
    dividends = stock.dividends

    # Ensure dividends are in ascending order
    dividends = dividends.sort_index(ascending=True)

    results = []

    for div_date, dividend in dividends.items():
        start_date = div_date - timedelta(days=10)
        # Ensure start_date is a trading day
        while start_date not in hist.index:
            start_date -= timedelta(days=1)
            if start_date < hist.index.min():
                start_date = hist.index.min()
                break

        opening_price = hist.loc[start_date, 'Open']
        targets = {
            '50%': opening_price + dividend * 0.5,
            '75%': opening_price + dividend * 0.75,
            '100%': opening_price + dividend * 1.0
        }
        
        target_dates = {key: None for key in targets.keys()}
        
        window_data = hist.loc[start_date:div_date + timedelta(days=90)]
        
        for date, row in window_data.iterrows():
            for key, target in targets.items():
                if row['Open'] >= target and target_dates[key] is None:
                    target_dates[key] = date

        result_row = {
            'Dividend Date': div_date,
            'Opening Price': opening_price,
            '50% Target': targets['50%'],
            '75% Target': targets['75%'],
            '100% Target': targets['100%'],
            '50% Achieved': target_dates['50%'],
            '75% Achieved': target_dates['75%'],
            '100% Achieved': target_dates['100%'],
        }
        results.append(result_row)

    results_df = pd.DataFrame(results)
    st.dataframe(results_df)

def main():
    stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'STOCK_SYMBOL')
    years_history = st.sidebar.slider('Select number of years for history:', min_value=3, max_value=20, value=3)
    proceed_button = st.sidebar.button('Execute')

    # Check if dividends are increasing over the past 10 years
    stock = yf.Ticker(stock_symbol)
    dividends = stock.dividends
    proceed = dividends.is_monotonic_increasing

    if proceed_button:
        calculate(stock_symbol, proceed, years_history)

if __name__ == "__main__":
    main()
