import yfinance as yf
import pandas as pd
import streamlit as st

st.title('Stock Data')

# Get stock symbol from user
symbol = st.text_input('Enter Stock Symbol', 'AAPL') 

# Fetch data
ticker = yf.Ticker(symbol)
info = ticker.info

# Display data
st.header(symbol + ' Data')
st.markdown('**Closing Price:** ' + str(info['previousClose'])) 
st.markdown('**52 Week High:** ' + str(info['fiftyTwoWeekHigh']))
st.markdown('**52 Week Low:** ' + str(info['fiftyTwoWeekLow'])) 
st.markdown('**1 Year Target Estimate:** ' + str(info['targetMeanPrice']))
st.markdown('**Dividend:** ' + str(info['dividendRate'])) 
st.markdown('**Yield:** ' + str(info['dividendYield'] * 100) + '%')

# Calculate 30 day average volume 
last_30_days = hist.Close.iloc[-30:]
avg_30_day_vol = last_30_days.Volume.mean()

# Display 
st.markdown('**30 Day Average Volume:** ' + str(int(avg_30_day_vol)))

# Fetch historical data
hist = ticker.history(period="1y") 

# Display historical data
st.header('Historical Data')
st.line_chart(hist.Close)
st.dataframe(hist)
