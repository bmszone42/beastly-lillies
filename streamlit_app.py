"""Streamlit app to analyze stock dividend performance."""

from datetime import datetime, timedelta
import logging
import pytz
import pandas as pd
import yfinance as yf
import streamlit as st
import dateparser

# Constants
DEFAULT_YEARS = 10
MAX_YEARS = 20 
TARGET_PERCENTS = [0.5, 0.75, 1.0]

logging.basicConfig(level=logging.INFO)

def get_historical_data(symbol, years):
  ticker = yf.Ticker(symbol)
  start = datetime.now() - timedelta(days=365*years)  
  data = ticker.history(start=start)
  return data

def get_dividends(symbol):
  ticker = yf.Ticker(symbol)
  dividends = ticker.dividends
  dividends.index = dividends.index.map(lambda x: datetime.strptime(str(x), '%Y-%m-%dT%H:%M:%S%z'))
  return dividends
  
def calculate_target_prices(dividend, opening_price):
  targets = {
      f"{p*100}%": opening_price + dividend * p
      for p in TARGET_PERCENTS
  }
  return targets

def get_first_valid_date(dividend_date, data):
  """Find the first valid date that is at least 10 business days before the dividend date."""
  days_back = 10
  while days_back > 0:
    date = dividend_date - timedelta(days=days_back)
    if data.loc[date, 'Open'] is not None:
      if is_business_day(date):
        return date
    days_back -= 1
  return None

def is_business_day(date):
  """Returns True if the date is a business day, False otherwise."""
  if date.weekday() == 5 or date.weekday() == 6:
    return False
  else:
    return True

def analyze_dividends(symbol, years=DEFAULT_YEARS):
  
  data = get_historical_data(symbol, years)
  dividends = get_dividends(symbol)

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

def print_df_info(df):
  print("DataFrame Info:")
  print(f"Columns: {df.columns.tolist()}") 
  print(f"Index: {df.index.name} as {df.index.dtype}")
  print(f"Index min: {df.index.min()} max: {df.index.max()}")


def main():
  
  st.title("Dividend Analysis")
  symbol = st.sidebar.text_input("Symbol", "AAPL")
  years = st.sidebar.slider("Years", 10, MAX_YEARS, DEFAULT_YEARS) 
  run_btn = st.sidebar.button("Analyze")

  if run_btn:
    
    results = analyze_dividends(symbol, years)
    
    print_df_info(dividends)

    st.markdown("## Results")
    st.dataframe(results)

    # Display dividends DataFrame
    st.markdown("## Dividends Data")  
    dividends = get_dividends(symbol)
    st.dataframe(dividends)

    cols = st.columns(2)
    cols[0].metric("50% Target Met", f"{results['Percent Targets Met']['50%'].mean()*100:.1f}%")
    cols[1].metric("Avg Days to 75% Target", f"{results['Days to Meet Targets']['75%'].mean():.1f}")

    details = results[["Percent Targets Met", "Days to Meet Targets"]].describe()
    st.dataframe(details)

if __name__ == "__main__":
  main()
