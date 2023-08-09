import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_stock_data(symbol, years):
    try:
        stock = yf.Ticker(symbol)
        dividends = stock.dividends
        today = pd.Timestamp.today().date()
        closest_ex_dividend_date = dividends.index[dividends.index <= today].max()

        if pd.isna(closest_ex_dividend_date):
            ex_dividend_message = "No past or present ex-dividend date found."
        else:
            next_dividend_date = dividends.index[dividends.index > today].min()
            ex_dividend_message = f"Closest ex-dividend date: {closest_ex_dividend_date.strftime('%Y-%m-%d')}."

            if pd.notna(next_dividend_date):
                ex_dividend_message += f" Next ex-dividend date: {next_dividend_date.strftime('%Y-%m-%d')}."

        is_ex_dividend_today = today == closest_ex_dividend_date

        # Display the dividends data as a table in Streamlit
        st.write(f"Dividend data for {symbol}:")
        st.write(dividends.to_frame())

        hist = stock.history(period=f'{years}y')
        # Display the history data as a table in Streamlit
        st.write(f"History data for {symbol}:")
        st.write(hist.to_frame())

        # Continue with the logic from get_symbol_data
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

        return is_ex_dividend_today, ex_dividend_message, pd.DataFrame(dividend_dates)

    except Exception as e:
        return False, f"Error fetching dividend data for {symbol}: {e}", None

# Function to calculate average days
def calculate_avg_days(symbols, years):
    data = []
    for symbol in symbols:
        _, _, dividend_data = get_stock_data(symbol, years)
        data.append(dividend_data)

    dividend_dates = pd.concat(data)
    dividend_dates['Dividend Date'] = pd.to_datetime(dividend_dates['Dividend Date'])
    dividend_dates['Ex-Dividend Date'] = pd.to_datetime(dividend_dates['Ex-Dividend Date'])

    grouped = dividend_dates.groupby('Month')
    avg_days = []

    for month, group in grouped:
        periods = [group[i:i+10] for i in range(0, len(group), 10)]
        for period in periods:
            avg = period['Days to Opening Price > Target'].mean()
            avg_days.append({'Month': month, 'Avg Days': avg})

    avg_days_df = pd.DataFrame(avg_days)
    return dividend_dates, avg_days_df

def main():
    st.title("Stock Dividend Analysis")
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
            is_ex_dividend, message, _ = get_stock_data(symbol, years)
            st.sidebar.write(f'{symbol}: {message}')
            valid_symbols.append(symbol)

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
                st.write(summarized_results)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
