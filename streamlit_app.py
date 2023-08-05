import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Define the stock and dividend dates
stock_symbol = 'AAPL'  # Change this to your stock symbol
dividend_dates = ['2023-04-01', '2022-04-01', '2020-04-01', '2019-04-01']  # add more dates as needed

# Get the stock data
stock = yf.Ticker(stock_symbol)
hist = stock.history(period='10y')

# Check if dividends have been increasing over the past 10 years
dividends = hist[hist['Dividends'] > 0]['Dividends']
if not dividends.is_monotonic:
    print(f"The dividends of {stock_symbol} have not been consistently increasing over the past 10 years.")
    proceed = input("Do you wish to proceed? (y/n) ")
    if proceed.lower() != 'y':
        exit()

results = []

# Loop through each dividend date
for div_date_str in dividend_dates:
    div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
    start_date = div_date - timedelta(days=10)
    end_date = div_date + timedelta(days=90)

    # Get the window data
    window_data = hist.loc[start_date:end_date]

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
print(results_df)
