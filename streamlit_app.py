import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

st.title('Dividend Investing Analysis')

def get_data(tickers, years):
    data = {}
    for ticker in tickers:
        ticker_obj = yf.Ticker(ticker)
   
        data[ticker] = {'History': ticker_obj.history(period=f"{years}y")}
      
    return data

def get_metrics(data):
    metrics = {}
    for ticker in data:
        history = data[ticker].history(period="max")
        dividends = data[ticker]['Dividends']
        metrics[ticker] = {
            '52 Week High': history['High'].max(),
            '52 Week Low': history['Low'].min(),
            'Dividend': dividends['Dividends'].max(),
            'Yield': data[ticker].info['dividendYield'] * 100,
            'Volume': history['Volume'].mean() 
        }
    return metrics
        
def add_div_analysis(data, metrics, years):
    analysis = {}
    for ticker in data:
        dividends = data[ticker]['Dividends']
        div_days = [(x - dividends.index[0]).days for x in dividends.index]
        div_dates = [dividends.index[0] + timedelta(days=x) for x in div_days]
        div_yields = [metrics[ticker]['Yield'] * y / 100 for y in dividends['Dividends']]
        
        prices = data[ticker].history(div_dates)['Close']
        highs = data[ticker].history(div_dates)['High']
        
        perf = {}
        for i, div_date in enumerate(div_dates):
            perf[div_date.year] = {}
            for pct in [50, 75, 100]:
                target = prices[i] + pct/100 * div_yields[i]
                high_price = highs[i:]
                days = np.argmax(high_price > target)
                perf[div_date.year][pct] = days
                
        avg_perf = {pct: np.mean([perf[y][pct] for y in perf]) for pct in [50, 75, 100]}
        
        analysis[ticker] = {'Perf': perf, 'Avg': avg_perf}
        
    return analysis
            
tickers = st.text_input('Enter stock tickers separated by spaces')
years = st.number_input('Enter number of years to analyze', 5, 10, 10)

if st.button('Analyze'):

    if tickers:
        tickers = tickers.split()
        data = get_data(tickers, years)
        metrics = get_metrics(data)
        analysis = add_div_analysis(data, metrics, years)

        m_df = pd.DataFrame(metrics).T
        a_df = pd.DataFrame(analysis).T
        
        st.subheader('Metrics')
        st.table(m_df)
        
        st.subheader('Dividend Analysis')
        st.table(a_df['Avg'])
