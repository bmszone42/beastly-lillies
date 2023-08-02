import streamlit as st
import yfinance as yf 
import pandas as pd
import plotly.express as px

st.title('Dividend Stock Analysis')

symbol = st.text_input('Enter a stock symbol', 'MSFT')
years = st.slider('Select number of years', 1, 10, 5)

@st.cache
def get_data(symbol):
    return yf.download(symbol, period='5y')

df = get_data(symbol)

dividends = df[['Dividends']]
prices = df[['Close']]

def calc_recovery(divs, prices):
    results = []
    for i, row in dividends.iterrows():
        div_amt = row['Dividends']
        price = prices.loc[i]['Close']
        c1 = price + 0.5 * div_amt 
        c2 = price + 0.75 * div_amt
        c3 = price + div_amt
        
        days = []
        for c in [c1, c2, c3]:
            mask = prices > c
            days.append((mask[mask].index[0] - i).days)
        results.append({'Date':i.date(), 'DaysToRecover': days})

    return pd.DataFrame(results)

recovery_data = calc_recovery(dividends, prices)

st.subheader('Dividend Recovery Analysis')
st.write(recovery_data)

st.subheader('Stock Closing Price')
fig = px.line(prices.reset_index(), x='Date', y='Close')
st.write(fig)
