import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Function to get historical data
def get_historical_data(symbol, years):
    ticker = yf.Ticker(symbol) 
    return ticker.history(period=f'{years}y')

# Function to calculate metrics
def calculate_metrics(historical_data):
    
    # Extract dividend info 
    dividend_data = []
    for date, dividend in zip(historical_data.index, historical_data['Dividends']):
        if dividend > 0:
            # Calculate dates and prices
            prev_date = date - timedelta(days=10)
            next_date = date + timedelta(days=60)
            prev_price = historical_data.loc[prev_date, 'Open']
            next_price = historical_data.loc[next_date, 'Open']
            
            # Calculate metrics
            percentage_increase = ((next_price - prev_price) / prev_price) * 100
            target = dividend + prev_price
            days_to_target = ((historical_data.loc[next_date:, 'Open'] >= target).idxmax() - next_date).days
            
            # Append to dividend data
            dividend_data.append({
                'dividend_date': date.strftime('%Y-%m-%d'), 
                'month': date.month,
                'dividend_amount': dividend,
                'price_on_dividend_date': historical_data.loc[date, 'Close'],
                'prev_date': prev_date.strftime('%Y-%m-%d'),
                'prev_price': prev_price,
                'next_date': next_date.strftime('%Y-%m-%d'),
                'next_price': next_price,   
                'percent_increase': round(percentage_increase, 1),
                'target': target,
                'days_to_target': days_to_target
            })
            
    # Create dataframe        
    dividend_df = pd.DataFrame(dividend_data)
    
    # Groupby and aggregate        
    avg_days_df = dividend_df.groupby('month')[['days_to_target']].mean().reset_index()

    return dividend_df, avg_days_df
    
                
# Streamlit interface
def build_sidebar():
    st.sidebar.text_input('Enter stock symbol:', 'AAPL')
    st.sidebar.slider('Select number of years:', min_value=10, max_value=20, value=10)
    st.sidebar.button('Execute')

def show_results(dividend_df, avg_days_df):
    st.header('Dividend Data')
    st.write(dividend_df)
    
    st.header('Average Days to Target')
    st.write(avg_days_df)
    
def main():
    
    # Build sidebar
    symbol = build_sidebar()
    
    # Get data
    historical_data = get_historical_data(symbol, 10)
    
    # Calculate metrics
    dividend_df, avg_days_df = calculate_metrics(historical_data)

    # Display results 
    show_results(dividend_df, avg_days_df)
    
if __name__ == '__main__':
    main()
