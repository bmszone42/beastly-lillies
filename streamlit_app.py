import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Function to check if dividends have been increasing over the past 10 years
def is_increasing(series):
    return all(x<y for x, y in zip(series, series[1:]))

def calculate(stock_symbol, proceed, years_history):
    # Get the stock data
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period=f'{years_history}y')

    # Convert the DateTimeIndex to a timezone-naive DateTimeIndex
    hist.index = hist.index.tz_localize(None)

    st.write('Historical data:')
    st.dataframe(hist)

    dividends = hist[hist['Dividends'] > 0]['Dividends'].resample('Y').sum()

    st.write('Yearly dividends:')
    st.dataframe(dividends)

    if not is_increasing(dividends) and proceed == 'No':
        st.write(f"The dividends of {stock_symbol} have not been consistently increasing over the past {years_history} years.")
    else:
        # Proceed with calculations
        st.write(f"Calculating for {stock_symbol}...")
        
        # Get dividend dates for current and past 3 years
        current_year = datetime.now().year
        dividend_dates = hist[(hist.index.year <= current_year) & (hist.index.year >= current_year-3) & (hist['Dividends'] > 0)].index
        
        st.write('Dividend dates for the past three years:')
        st.dataframe(pd.DataFrame(dividend_dates, columns=['Dividend Dates']))

        results = []
        # Loop through each dividend date
        for div_date in dividend_dates:
            start_date = div_date - timedelta(days=10)
            end_date = div_date + timedelta(days=90)

            # Get the window data
            window_data = hist.loc[start_date:end_date]

            st.write(f'Data for window from {start_date} to {end_date}:')
            st.dataframe(window_data)

            if div_date in hist.index:  
                # Get the dividend
                dividend = hist.loc[div_date, 'Dividends']

                # Get the opening price 10 days before the ex-date
                opening_price = hist.loc[start_date, 'Open']

                # Calculate targets
                targets = [(opening_price + dividend) * x for x in [1.5, 1.75, 2.0]]

                target_days = {}
                # Loop through each target
                for i, target in enumerate(targets):
                    # Find the first day where the closing price is greater than or equal to the target
                    target_day = window_data[window_data['Close'] >= target].index.min()
                    if pd.notna(target_day):
                        target_days[f"{50*(i+1)}_target_days"] = (target_day - start_date).days

                # Calculate average
                if target_days.values():
                    average_days = sum(target_days.values()) / len(target_days.values())
                else:
                    average_days = None

                target_days.update({'div_date': div_date, 'average_days': average_days})
                results.append(target_days)

        # Convert results to a DataFrame for easier viewing
        results_df = pd.DataFrame(results)
        st.write('Results:')
        st.dataframe(results_df)

def main():
    # Define the stock
    stock_symbol = st.sidebar.text_input("Enter stock symbol", 'AAPL')
    proceed = st.sidebar.selectbox("Proceed if dividends are not increasing?", ('Yes', 'No'))
    years_history = st.sidebar.slider("Select range for historical data (years)", 1, 20, 10)
    
    calculate(stock_symbol, proceed, years_history)

if __name__ == "__main__":
    main()
