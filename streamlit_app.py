import streamlit as st
from datetime import datetime, timedelta
from finance_calendars import finance_calendars as fc

# Function to get dividends
def get_dividends(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date)
    data = {}
    for date in dates:
        dividends = fc.get_dividends_by_date(date)
        if not dividends.empty:
            data[date] = dividends
    return data

# Function to select a week
def select_week():
    today = datetime.today()
    week_start = st.sidebar.date_input('Start date', today)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

# Main function for the Streamlit app
def main():
    st.title('Dividend Checker')

    week_start, week_end = select_week()

    if st.button('Find Dividend Stocks'):
        data = get_dividends(week_start, week_end)

        for date, dividends in data.items():
            st.write(f"Dividends for {date}:")
            st.write(dividends)

if __name__ == "__main__":
    main()
