import yfinance as yf 
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_symbol_data(symbol, date, years):

  stock = yf.Ticker(symbol)

  hist = stock.history(period=f'{years}y')

  # Check if 'Dividends' column exists
  if 'Dividends' not in hist.columns:
    return pd.DataFrame() # return empty DataFrame

  try:
    hist.index.tz 
  except AttributeError:
    # Index is tz-naive
    pass  
  else:
    # Index is tz-aware
    date = pd.to_datetime(date).tz_localize(hist.index.tz)
  
  # Filter to dividend dates before given date
  hist = hist[:date]

  # Convert index to datetime 
  hist.index = pd.to_datetime(hist.index)

  dividend_dates = []

  for i, dividend in hist['Dividends'].items():
    if dividend > 0:
      try:
        prev_date = i - timedelta(days=10)
        next_date = i + timedelta(days=60)

        if prev_date in hist.index and next_date in hist.index:
          
          prev_price = hist.loc[prev_date, 'Open']
          next_price = hist.loc[next_date, 'Open']

          percentage_increase = ((next_price - prev_price) / prev_price) * 100

          target = dividend + prev_price

          days_to_target = ((hist.loc[next_date:, 'Open'] >= target).idxmax() - next_date).days

          dividend_dates.append({
              'Symbol': symbol,
              'Dividend Date': i.strftime('%Y-%m-%d'),
              'Month': i.month,
              'Dividend Amount': dividend,
              'Price on Dividend Date': hist.loc[i, 'Close'], 
              '-10 Days Date': prev_date.strftime('%Y-%m-%d'),
              'Opening Price -10 Days': prev_price,
              '+60 Days Date': next_date.strftime('%Y-%m-%d'),
              'Opening Price +60 Days': next_price,
              '% Increase': round(percentage_increase, 1),
              'Target': target,
              'Date Used for Target': prev_date.strftime('%Y-%m-%d'),
              'Days to Opening Price > Target': days_to_target
            })

      except KeyError:
        continue

  return pd.DataFrame(dividend_dates)


def calculate_avg_days(symbols, date, years):

  data = []

  for symbol in symbols:  
    data.append(get_symbol_data(symbol, date, years))

  st.write(f'Data info for {symbols}')
  st.write(data)
  
  #dividend_dates = pd.concat(data)
  # Convert 'Dividend Date' column to datetime type explicitly
  dividend_dates['Dividend Date'] = pd.to_datetime(dividend_dates['Dividend Date'])


  st.write(f'Dividend info for {symbols}')
  st.write(dividend_dates)

  # Extract month from date 
  dividend_dates['Month'] = dividend_dates['Dividend Date'].dt.month

  # Group by month 
  grouped = dividend_dates.groupby('Month')

  avg_days = []

  # Iterate through groups
  for month, group in grouped:

    # Get 10 year periods 
    periods = [group[i:i+10] for i in range(0, len(group), 10)]

    # Calculate average for each period
    for period in periods:
      avg = period['Days to Opening Price > Target'].mean()
      avg_days.append({'Symbol': symbol, 'Month': month, 'Avg Days': avg})

  avg_days_df = pd.DataFrame(avg_days)
  
  st.write(avg_days_df)
  return dividend_dates, avg_days_df


def main():
  date = st.date_input('Enter dividend date')
  symbols = st.text_input('Enter symbols separated by comma')
  symbols = symbols.split(',')  
  years = 10
  
  if st.button('Calculate'):
    calculate_avg_days(symbols, date, years)

    st.write(f'Average Days for {symbols}')
    st.write(avg_days_df)

    st.write(f'Dividend info for {symbols}')
    st.write(dividend_dates)

if __name__ == '__main__':
  main()
