"""Streamlit app to analyze stock dividend performance."""

from datetime import datetime, timedelta
import logging

import pandas as pd
import yfinance as yf
import streamlit as st

# Constants
DEFAULT_YEARS = 3  
MAX_YEARS = 20
TARGET_PERCENTS = [0.5, 0.75, 1.0]   

logging.basicConfig(level=logging.INFO)

def get_historical_data(symbol, years):
  ticker = yf.Ticker(symbol)    
  start = datetime.now() - timedelta(days=365*years)
  data = ticker.history(start=start)
  return data

def calculate_target_prices(dividend, opening_price):
  targets = {
      f"{p*100}%": opening_price + dividend * p   
      for p in TARGET_PERCENTS
  }
  return targets

def find_target_dates(targets, data):
  target_dates = {p:None for p in targets.keys()}
  for date, row in data.iterrows():
    open_price = row['Open']    
    for p, target in targets.items():
      if open_price >= target and target_dates[p] is None:
        target_dates[p] = date
        
  return target_dates
  
def analyze_dividends(symbol, years=DEFAULT_YEARS):
  
  data = get_historical_data(symbol, years)
  dividends = get_dividends(symbol) #mocked for example

  results = []

  for dividend_date, dividend in dividends.iteritems():
    start_date = get_first_valid_date(dividend_date, data)
    open_price = data.loc[start_date, 'Open']
    price_on_dividend_date = data.loc[dividend_date, 'Open']

    targets = calculate_target_prices(dividend, open_price)
    target_dates = find_target_dates(targets, data)

    pcts_met = {p: date is not None for p, date in target_dates.items()}
    days_to_targets = {p: (target_dates[p] - dividend_date).days  
                       for p, date in target_dates.items() if date}

    result_row = {
      "Dividend Date": dividend_date,
      "Opening Date": start_date,
      "Opening Price": open_price,
      "Price on Dividend Date": price_on_dividend_date,
      "50% Target": targets['50%'],
      "75% Target": targets['75%'], 
      "100% Target": targets['100%'],
      "50% Target Date": target_dates['50%'],
      "75% Target Date": target_dates['75%'],
      "100% Target Date": target_dates['100%'],
      "Percent Targets Met": pcts_met,
      "Days to Meet Targets": days_to_targets
    }

    results.append(result_row)

  return pd.DataFrame(results)

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
