import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta  
import numpy as np

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

  # Set minimum days before dividend
  min_days_before = 10

  for div_date, dividend in dividends.items():

    # Offset dividend date by 10 business days
    start_date = np.busday_offset(div_date, -10, roll='forward')
    
    opening_price = hist.loc[start_date, 'Open']

    price_on_dividend_date = hist.loc[div_date, 'Open']

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
      'Dividend Date': div_date.strftime('%Y-%m-%d'),
      'Opening Date': start_date.strftime('%Y-%m-%d'),
      'Price on Dividend Date': price_on_dividend_date,
      'Opening Price': opening_price,
      '50% Target': targets['50%'],
      '75% Target': targets['75%'],
      '100% Target': targets['100%'],
      '50% Achieved': target_dates['50%'].strftime('%Y-%m-%d') if target_dates['50%'] else None,
      '75% Achieved': target_dates['75%'].strftime('%Y-%m-%d') if target_dates['75%'] else None,
      '100% Achieved': target_dates['100%'].strftime('%Y-%m-%d') if target_dates['100%'] else None,
    }

    results.append(result_row)

  results_df = pd.DataFrame(results)
  
  st.dataframe(results_df)

def main():

  stock_symbol = st.sidebar.text_input('Enter stock symbol:', 'AAPL')

  years_history = st.sidebar.slider('Select number of years for history:', min_value=5, max_value=20, value=10)

  proceed_button = st.sidebar.button('Execute')

  # Check if dividends are increasing over the past 10 years
  stock = yf.Ticker(stock_symbol)
  dividends = stock.dividends
  proceed = dividends.is_monotonic_increasing

  if proceed_button:
    calculate(stock_symbol, proceed, years_history)

if __name__ == "__main__":
  main()
