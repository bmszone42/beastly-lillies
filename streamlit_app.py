import yfinance as yf
import streamlit as st
import pandas as pd

st.title('Dividend Investing Analysis')

tickers = st.text_input('Enter stock tickers separated by spaces')

if tickers:
    tickers = tickers.split()
    
    data = {}
    metrics = {}
    
    for ticker in tickers:
        data[ticker] = yf.Ticker(ticker)
        history = data[ticker].history(period="max")
        
        metrics[ticker] = {
            '52 Week High': history['High'].max(),
            '52 Week Low': history['Low'].min(),
            'Dividend': data[ticker].info['dividendRate'], 
            'Yield': data[ticker].info['dividendYield'] * 100,
            'Volume': history['Volume'].mean()
        }
        
    metrics_df = pd.DataFrame(metrics).T
    
    st.table(metrics_df)
