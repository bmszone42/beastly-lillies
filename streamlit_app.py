import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_stock_data(ticker_list, start_date, end_date):
    data = {}
    for ticker in ticker_list:
        try:
            data[ticker] = yf.download(ticker, start=start_date, end=end_date)
        except:
            st.error(f"Error downloading data for {ticker}. Please check the stock symbol.")
    return data

def get_dividend_data(data):
    dividend_data = {}
    for ticker, df in data.items():
        try:
            # Debugging statement to print data for each stock
            print(f"Data for {ticker}:\n{df.head()}\n")

            div_df = df[df['Dividends'] > 0]
            if not div_df.empty:
                dividend_data[ticker] = {
                    'dates': list(div_df.index),
                    'amounts': list(div_df['Dividends'])
                }
            else:
                st.warning(f"No dividend data found for {ticker}.")
        except:
            st.error(f"Error processing dividend data for {ticker}.")
    return dividend_data


def calculate_target_prices(data, dividend_data):
    target_prices = {}
    for ticker, div_data in dividend_data.items():
        try:
            prices = data[ticker].loc[div_data['dates'], 'Close']
            targets = [prices + div_amount * i / 100 for div_amount in div_data['amounts'] for i in [50, 75, 100]]
            target_prices[ticker] = targets
        except:
            st.error(f"Error calculating target prices for {ticker}.")
    return target_prices

def calculate_days_to_target(data, dividend_data, target_prices):
    days_to_target = {}
    for ticker, div_data in dividend_data.items():
        try:
            days = []
            for target in target_prices[ticker]:
                for date, price in zip(div_data['dates'], target):
                    mask = (data[ticker].index <= date) & (data[ticker]['High'] >= price)
                    days.append((data[ticker][mask].index[-1] - date).days)
            days_to_target[ticker] = days
        except:
            st.error(f"Error calculating days to reach target for {ticker}.")
    return days_to_target

def main():
    st.title("Dividend Stock Analysis")

    tickers = st.text_input("Enter stock symbols separated by spaces")
    button = st.button("Analyze")

    if button:
        # Download data
        ticker_list = tickers.split()
        start_date = datetime.today() - timedelta(days=365 * 10)
        end_date = datetime.today()
        data = get_stock_data(ticker_list, start_date, end_date)

        # Get dividend info
        dividend_data = get_dividend_data(data)

        if len(dividend_data) == 0:
            st.error("No dividend data found for any of the specified stocks.")
            return

        # Calculate target prices
        target_prices = calculate_target_prices(data, dividend_data)

        # Calculate days to reach targets
        days_to_target = calculate_days_to_target(data, dividend_data, target_prices)

        # Create and display results dataframe
        col_names = ['50%', '75%', '100%']
        df = pd.DataFrame(days_to_target, index=col_names).T
        st.dataframe(df)

        # Output additional info
        for ticker in ticker_list:
            st.subheader(ticker)
            try:
                info = yf.Ticker(ticker).info
                st.write("Closing Price:", info['regularMarketPrice'])
                st.write("52 Week High:", info['fiftyTwoWeekHigh'])
                st.write("52 Week Low:", info['fiftyTwoWeekLow'])
                st.write("1 Year Target:", info['targetMeanPrice'])
                st.write("Dividend:", info['dividendRate'])
                st.write("Dividend Yield:", info['dividendYield'])
                st.write("Average Volume:", info['averageDailyVolume10Day'])
                st.write("Link to Chart:")
                st.write(f"https://finance.yahoo.com/chart/{ticker}")
            except:
                st.error(f"Error fetching additional info for {ticker}.")

if __name__ == "__main__":
    main()
