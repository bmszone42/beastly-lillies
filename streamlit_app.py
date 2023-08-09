import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Function to check if a stock is ex-dividend today
def is_ex_dividend_today(symbol):
    try:
        stock = yf.Ticker(symbol)
        dividends = stock.dividends
        today = pd.Timestamp.today().date()
        return today in dividends.index
    except Exception:
        return False

# Function to get detailed dividend data for a symbol
def get_symbol_data(symbol, years):
    stock = yf.Ticker(symbol)
    hist = stock.history(period=f'{years}y')

    if 'Dividends' not in hist.columns:
        return pd.DataFrame()

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
                        'Ex-Dividend Date': stock.dividends.index[stock.dividends.index <= i][-1].strftime('%Y-%m-%d'),
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

# Function to calculate average days
def calculate_avg_days(symbols, years):
    data = []

    for symbol in symbols:
        data.append(get_symbol_data(symbol, years))

    dividend_dates = pd.concat(data)

    dividend_dates['Dividend Date'] = pd.to_datetime(dividend_dates['Dividend Date'])
    dividend_dates['Ex-Dividend Date'] = pd.to_datetime(dividend_dates['Ex-Dividend Date'])

    grouped = dividend_dates.groupby('Month')

    avg_days = []

    for month, group in grouped:
        periods = [group[i:i+10] for i in range(0, len(group), 10)]
        for period in periods:
            avg = period['Days to Opening Price > Target'].mean()
            #avg_days.append({'Symbol': symbol, 'Month': month, 'Avg Days': avg})
            avg_days.append({'Symbol': group['Symbol'].iloc[0], 'Month': month, 'Avg Days': avg})


    avg_days_df = pd.DataFrame(avg_days)

    return dividend_dates, avg_days_df

def display_sidebar(valid_symbols):
    st.sidebar.markdown("## Ex-Dividend Today")
    for symbol in valid_symbols:
        ex_dividend_today = is_ex_dividend_today(symbol)
        st.sidebar.write(f'{symbol}: Ex-Dividend Today? {ex_dividend_today}')

def main():
    st.title("Stock Dividend Analysis")
    st.markdown("## Instructions")
    st.write("1. Enter stock symbols separated by commas.")
    st.write("2. Choose a dividend date.")
    st.write("3. Click the 'Calculate' button to analyze dividend data.")

    years = 10
    valid_symbols = []

    col1, col2 = st.columns(2)
    with col1:
        symbols = st.text_input('Enter symbols separated by comma')
    with col2:
        default_date = pd.Timestamp.today().date()
        date = st.date_input('Enter dividend date', default_date)

    show_detailed_results = st.checkbox('Show Detailed Results', value=True)

    if st.button('Calculate'):
        symbols = symbols.split(',')
        for symbol in symbols:
            symbol = symbol.strip().upper()
            if yf.Ticker(symbol).info:
                valid_symbols.append(symbol)
            else:
                st.error(f"Invalid stock symbol: {symbol}")

        if valid_symbols:
            try:
                dividend_dates, avg_days_df = calculate_avg_days(valid_symbols, years)
                if show_detailed_results:
                    st.subheader(f'Dividend info for {valid_symbols}')
                    st.write(dividend_dates)

                    st.subheader(f'Average Days for {valid_symbols}')
                    st.write(avg_days_df)
                else:
                    summarized_results = dividend_dates[['Symbol', 'Ex-Dividend Date', 'Days to Opening Price > Target']].copy()
                    summarized_results = summarized_results.drop_duplicates(subset=['Symbol', 'Ex-Dividend Date'])
                    st.subheader('Summarized Results')

                    # Group summarized_results by Symbol and display for each symbol
                    for symbol, group in summarized_results.groupby('Symbol'):
                        st.write(f"Symbol: {symbol}")
                        st.write(group)

            except Exception as e:
                st.error(f"An error occurred: {e}")

            display_sidebar(valid_symbols)
        else:
            st.error("No valid stock symbols provided.")

if __name__ == '__main__':
    main()
