import yfinance as yf 
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_symbol_data(symbol, date, years):

  stock = yf.Ticker(symbol)

  hist = stock.history(period=f'{years}y')
  
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
    symbol_data = get_symbol_data(symbol, date, years)
    data.append(symbol_data)

  dividend_dates = pd.concat(data)

  avg_days = []

  for month in dividend_dates['Month'].unique():
    df_month = dividend_dates[dividend_dates['Month'] == month]

    for i in range(0, len(df_month), 10):
      df_period = df_month.iloc[i:i+10]
      mean_days = df_period['Days to Opening Price > Target'].mean()
      avg_days.append({
        'Month': month, 
        'Average Days': round(mean_days)  
      })

  avg_days_df = pd.DataFrame(avg_days)

  st.write(avg_days_df)


def main():

  date = st.date_input('Enter dividend date')
  symbols = st.text_input('Enter symbols separated by comma')
  symbols = symbols.split(',')  
  years = 10

  if st.button('Calculate'):
    calculate_avg_days(symbols, date, years)

if __name__ == '__main__':
  main()
