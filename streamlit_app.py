import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def is_increasing(series):
    return all(x<y for x, y in zip(series, series[1:]))

def calculate(stock_symbol, proceed, years_history):
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period=f'{years_history}y')

    hist.index = hist.index.tz_localize(None)

    st.write('Historical data:')
    st.dataframe(hist)

    dividends = hist[hist['Dividends'] > 0]['Dividends'].resample('Y').sum()

    st.write('Yearly dividends:')
    st.dataframe(dividends)

    if not is_increasing(dividends) and proceed == 'No':
        st.write(f"The dividends of {stock_symbol} have not been consistently increasing over the past {years_history} years.")
    else:
        st.write(f"Calculating for {stock_symbol}...")
        
        current_year = datetime.now().year
        dividend_dates = hist[(hist.index.year <= current_year) & (hist.index.year >= current_year-3) & (hist['Dividends'] > 0)].index
        
        st.write('Dividend dates for the past three years:')
        st.dataframe(pd.DataFrame(dividend_dates, columns=['Dividend Dates']))

        results = []
        for div_date in dividend_dates:
            start_date = div_date - timedelta(days=10)
            # Ensure start_date is a trading day
            while start_date not in hist.index:
                start_date -= timedelta(days=1)
                
            end_date = div_date + timedelta(days=90)
            window_data = hist.loc[start_date:end_date]

            st.write(f'Data for window from {start_date} to {end_date}:')
            st.dataframe(window_data)

            if div_date in hist.index:  
                dividend = hist.loc[div_date, 'Dividends']
                opening_price = hist.loc[start_date, 'Open']

                targets = [opening_price * (1 + x) for x in [0.5, 0.75, 1.0]]
                div_date_price = hist.loc[div_date, 'Close']

                target_days = {}
                target_prices = {}
                target_dates = {}

                for i, target in enumerate(targets):
                    target_day = window_data[window_data['Close'] >= target].index.min()
                    if pd.notna(target_day):
                        target_days[f"{50*(i+1)}%_target_days"] = (target_day - start_date).days
                        target_prices[f"{50*(i+1)}%_target_price"] = window_data.loc[target_day, 'Close']
                        target_dates[f"{50*(i+1)}%_target_date"] = target_day
                
                if target_days.values():
                    average_days = sum(target_days.values()) / len(target_days.values())
                else:
                    average_days = None

                result = {
                    'div_date': div_date, 
                    'div_date_price': div_date_price, 
                    'average_days_to_reach_target': average_days
                }
                result.update(target_days)
                result.update(target_prices)
                result.update(target_dates)
                results.append(result)

        results_df = pd.DataFrame(results)
        st.write('Results:')
        st.dataframe(results_df)

def main():
    stock_symbol = st.sidebar.text_input("Enter stock symbol", 'AAPL')
    proceed = st.sidebar.selectbox("Proceed if dividends are not increasing?", ('Yes', 'No'))
    years_history = st.sidebar.slider("Select range for historical data (years)", 1, 20, 10)
    
    calculate(stock_symbol, proceed, years_history)

if __name__ == "__main__":
    main()
