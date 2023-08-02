import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title('Dividend Stock Analysis')

tickers = st.text_input('Enter stock tickers separated by space')

if tickers:

  ticker_list = tickers.split()  

  # Initialize data structures
  data = {}
  metrics = {}
  dividend_data = {}
  
  for ticker in ticker_list:

    # Get data
    data[ticker] = yf.download(ticker, period='10y')

    # Get metrics
    ticker_info = yf.Ticker(ticker)
    metrics[ticker] = {
      '52 Week High': ticker_info.info['fiftyTwoWeekHigh'], 
      '52 Week Low': ticker_info.info['fiftyTwoWeekLow'],
      'Volume': ticker_info.info['averageVolume10days'],
      'Dividend': ticker_info.info['dividendRate'],
      'Yield': ticker_info.info['dividendYield']*100
    }

    # Get dividend data
    dividend_data[ticker] = yf.Ticker(ticker).dividends
    
    # Calculate dividend stats
    dividend_stats = calc_dividend_stats(dividend_data[ticker])
    metrics[ticker].update(dividend_stats)

  # Display results
  show_data(data, metrics, dividend_data)

def calc_dividend_stats(dividends):

  stats = {}

  for dividend in dividends:
    ex_date = dividend['exDate']
    amount = dividend['amount']
    
    # Get closing price on ex-date
    ex_price = get_close_price(ex_date)
    
    # Find recovery days
    days_50 = get_recovery_days(ex_price, amount, 0.5)
    days_75 = get_recovery_days(ex_price, amount, 0.75)  
    days_100 = get_recovery_days(ex_price, amount, 1.0)
    
    stats['50% Recovery Days'] = days_50 
    stats['75% Recovery Days'] = days_75
    stats['100% Recovery Days'] = days_100

  return stats

def get_close_price(date):
  # Use pandas to get close price on given date
  return close_price 

def get_recovery_days(ex_price, amount, target_recovery):
  # Find number of days for price to recover to target
  return recovery_days

def show_data(data, metrics, dividends):

  for ticker in data:

    df = data[ticker].reset_index()

    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day

    pivoted = df.pivot_table(index=['Year', 'Month', 'Day'], values='Close', aggfunc='mean').reset_index()

    st.header(ticker)
    st.write(pivoted)
    st.write(metrics[ticker])

    # Plot close price and dividends
    plot_data(df, dividends[ticker])
    
def plot_data(df, dividends):
    
  fig, ax = plt.subplots()

  ax.plot(df['Date'], df['Close'])

  for i, div in dividends.iterrows():
    ax.vlines(div.name, ymin=0, ymax=df['Close'].max(), colors='r')

  st.pyplot(fig)
