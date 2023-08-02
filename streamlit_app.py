import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title('Dividend Stock Analysis')

def get_close_price(date, df):
    try:
        # Find the row corresponding to the given date and get the 'Close' price
        close_price = df.loc[df['Date'] == date, 'Close'].values[0]
        return close_price
    except IndexError:
        # Handle the case where the date is not found in the DataFrame
        return None

def get_recovery_days(ex_price, amount, target_recovery):
    target_price = ex_price * (1 + target_recovery)
    return (target_price - ex_price) / amount

def calc_dividend_stats(dividends, df):
    stats = {}
    df_dividends = dividends.reset_index()

    for dividend in df_dividends.itertuples():
        ex_date = dividend.Index
        amount = dividend._asdict()['Dividends']

        # Get closing price on ex-date
        ex_price = get_close_price(ex_date, df)

        if ex_price is None:
            continue

        # Find recovery days
        stats[ex_date] = {
            'Ex-Price': ex_price,
            '50% Target Price': ex_price * 1.5,
            '75% Target Price': ex_price * 1.75,
            '100% Target Price': ex_price * 2.0,
            '50% Recovery Days': get_recovery_days(ex_price, amount, 0.5),
            '75% Recovery Days': get_recovery_days(ex_price, amount, 0.75),
            '100% Recovery Days': get_recovery_days(ex_price, amount, 1.0)
        }

    return pd.DataFrame.from_dict(stats, orient='index')

def show_data(data, metrics, dividends, dividend_stats):
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

        # Display dividend recovery statistics
        st.write(dividend_stats.loc[ticker])

def plot_data(df, dividends):
    fig, ax = plt.subplots()

    ax.plot(df['Date'], df['Close'])

    for i, div in dividends.iterrows():
        ax.vlines(div.Index, ymin=0, ymax=df['Close'].max(), colors='r')

    st.pyplot(fig)

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
            'Yield': ticker_info.info['dividendYield'] * 100
        }

        # Get dividend data
        dividend_data[ticker] = yf.Ticker(ticker).dividends

        # Calculate dividend stats
        dividend_stats = calc_dividend_stats(dividend_data[ticker], data[ticker])

        metrics[ticker].update(dividend_stats)

    # Display results
    show_data(data, metrics, dividend_data, dividend_stats)
