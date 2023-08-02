import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.title("Dividend Stock Analysis")

tickers = st.text_input("Enter stock symbols separated by spaces")
button = st.button("Analyze")

if button:

    # Download data
    ticker_list = tickers.split()
    data = {} 
    start_date = datetime.today() - timedelta(days=365*10)
    end_date = datetime.today()
    for ticker in ticker_list:
        data[ticker] = yf.download(ticker,start=start_date, end=end_date)

    # Get current info
    current_info = {}
    for ticker in ticker_list:
        current_info[ticker] = yf.Ticker(ticker).info

    # Initialize dataframe
    col_names = ['50%', '75%', '100%']
    df = pd.DataFrame(columns=col_names)

    # Analyze each ticker
    for ticker in ticker_list:

        # Get dividend info
        div_df = data[ticker][data[ticker]['Dividends'] > 0]
        div_dates = list(div_df.index)
        div_amounts = list(div_df['Dividends'])

        # Get price on dividend dates
        prices = data[ticker].loc[div_dates, 'Close']

        # Calculate target prices
        targets = [prices + div_amounts*i/100 for i in [50, 75, 100]]
        
        # Find number of days to reach target
        days_to_target = []
        for idx, target in enumerate(targets):
            days = []
            for date, price in zip(div_dates, target):
                mask = (data[ticker].index <= date) & (data[ticker]['High'] >= price)
                days.append(mask.idxmax())
            days_to_target.append(days)
        
        # Add results to dataframe
        df[ticker] = days_to_target

    # Output results
    st.dataframe(df)

    # Output additional info
    for ticker in ticker_list:
        st.subheader(ticker) 
        st.write("Closing Price:", current_info[ticker]['regularMarketPrice'])
        st.write("52 Week High:", current_info[ticker]['fiftyTwoWeekHigh'])
        st.write("52 Week Low:", current_info[ticker]['fiftyTwoWeekLow'])
        st.write("1 Year Target:", current_info[ticker]['targetMeanPrice'])
        st.write("Dividend:", current_info[ticker]['dividendRate'])
        st.write("Dividend Yield:", current_info[ticker]['dividendYield'])
        st.write("Average Volume:", current_info[ticker]['averageDailyVolume10Day'])
        
        st.write("Link to Chart:")
        st.write(f"https://finance.yahoo.com/chart/{ticker}")
