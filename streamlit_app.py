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

def get_dividends(symbol):
  """Get dividend payment history."""
  ticker = yf.Ticker(symbol)
  dividends = ticker.dividends  
    
  dividends.index = dividends.index.map(lambda x: datetime.strptime(str(x), '%Y%m%d'))
  return dividends

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
  
  # Get data
  data = get_historical_data(symbol, years)
  
  # Get dividends
  dividends = get_dividends(symbol) 
  
  results = []

  for dividend_date, dividend in dividends.iteritems():
    # Rest of function
  
  return pd.DataFrame(results)

def main():

  st.title("Dividend Analysis")
  
  symbol = st.sidebar.text_input("Symbol")
  years = st.sidebar.slider("Years", 1, MAX_YEARS, DEFAULT_YEARS)
  run_btn = st.sidebar.button("Analyze")

  if run_btn:
    results = analyze_dividends(symbol, years)

    st.markdown("## Results")
    st.dataframe(results)

    cols = st.columns(2)
    cols[0].metric("50% Target Met", f"{results['Percent Targets Met']['50%'].mean()*100:.1f}%") 
    cols[1].metric("Avg Days to 75% Target", f"{results['Days to Meet Targets']['75%'].mean():.1f}")

    details = results[["Percent Targets Met", "Days to Meet Targets"]].describe()
    st.dataframe(details)

if __name__ == "__main__":
  main()
