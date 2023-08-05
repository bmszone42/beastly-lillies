Dividend Checker
This is a Streamlit app that allows you to check if certain stocks have dividends in a specific week.

Installation
First, clone this repository:

bash
Copy code
git clone https://github.com/yourusername/dividend-checker.git
cd dividend-checker
Then, create a virtual environment and install the dependencies:

bash
Copy code
python3 -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
pip install -r requirements.txt
Usage
To run the app, use the following command:

arduino
Copy code
streamlit run app.py
Then, visit http://localhost:8501 in your browser.

In the app, enter the ticker symbols of the stocks you're interested in, separated by commas. Then select a start date for a week. The app will check if the specified stocks have dividends in the selected week.

Dependencies
yfinance
pandas
streamlit
License
MIT
