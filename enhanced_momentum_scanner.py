
import streamlit as st
import yfinance as yf
import pandas as pd
try:
    import ta
except ImportError:
    st.error("The 'ta' library is not installed. Please install it using 'pip install ta'.")

# Function to fetch stock data
def fetch_stock_data(ticker):
    stock_data = yf.download(ticker, period="1y", interval="1d")
    return stock_data

# Function to calculate momentum indicators
def calculate_indicators(stock_data):
    stock_data['RSI'] = ta.momentum.RSIIndicator(stock_data['Close'].squeeze()).rsi()
    stock_data['MACD'] = ta.trend.MACD(stock_data['Close']).macd_diff()
    stock_data['SMA_10'] = ta.trend.SMAIndicator(stock_data['Close'], window=10).sma_indicator()
    stock_data['SMA_50'] = ta.trend.SMAIndicator(stock_data['Close'], window=50).sma_indicator()
    stock_data['ADX'] = ta.trend.ADXIndicator(stock_data['High'], stock_data['Low'], stock_data['Close']).adx()
    stock_data['RVOL'] = stock_data['Volume'] / stock_data['Volume'].rolling(window=20).mean()
    return stock_data

# Function to rank stocks based on momentum
def rank_stocks(stock_data):
    stock_data['Momentum_Score'] = stock_data['RSI'] + stock_data['MACD'] + (stock_data['SMA_10'] - stock_data['SMA_50']) + stock_data['ADX'] + stock_data['RVOL']
    return stock_data

# Function to apply quality filters
def apply_quality_filters(stock_data, roe_threshold, debt_to_equity_threshold):
    stock_data = stock_data[stock_data['ROE'] >= roe_threshold]
    stock_data = stock_data[stock_data['Debt_to_Equity'] <= debt_to_equity_threshold]
    return stock_data

# Streamlit UI
st.title("Indian Stock Momentum Scanner")

# Dropdown for selecting index
index_options = [
    "Nifty 50", "Nifty Next 50", "Nifty 100", "Nifty 200", "Nifty 500",
    "Nifty Midcap 50", "Nifty Midcap 100", "Nifty Midcap 150",
    "Nifty Smallcap 50", "Nifty Smallcap 100", "Nifty Smallcap 250",
    "Nifty IT", "Nifty Pharma", "Nifty Bank", "Nifty FMCG", "Nifty Auto", "Nifty Energy", "Nifty Realty"
]
selected_index = st.selectbox("Select Stock Index", index_options)

# Input for quality filters
roe_threshold = st.slider("Minimum ROE (%)", 0, 50, 15)
debt_to_equity_threshold = st.slider("Maximum Debt-to-Equity Ratio", 0.0, 3.0, 1.0)

# Placeholder for stock data
stock_data = pd.DataFrame()

# Fetch stock data for the selected index
if selected_index:
    # Example tickers for demonstration (replace with actual tickers for each index)
    tickers = {
        "Nifty 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
        "Nifty Next 50": ["BAJAJHLDNG.NS", "DMART.NS", "ICICIPRULI.NS"],
        "Nifty 100": ["INFY.NS", "HINDUNILVR.NS", "KOTAKBANK.NS"],
        # Add more tickers for other indices
    }
    selected_tickers = tickers.get(selected_index, [])

    for ticker in selected_tickers:
        data = fetch_stock_data(ticker)
        data = calculate_indicators(data)
        data['Ticker'] = ticker
        stock_data = pd.concat([stock_data, data])

    # Apply quality filters
    stock_data['ROE'] = 20  # Example ROE value (replace with actual data)
    stock_data['Debt_to_Equity'] = 0.5  # Example Debt-to-Equity value (replace with actual data)
    stock_data = apply_quality_filters(stock_data, roe_threshold, debt_to_equity_threshold)

    # Rank stocks based on momentum
    stock_data = rank_stocks(stock_data)
    top_stocks = stock_data.groupby('Ticker').tail(1).sort_values(by='Momentum_Score', ascending=False).head(5)

    # Display top 5 momentum stocks
    st.write("Top 5 Momentum Stocks")
    st.dataframe(top_stocks[['Ticker', 'Momentum_Score', 'RSI', 'MACD', 'SMA_10', 'SMA_50', 'ADX', 'RVOL']])

    # Plotting
    for ticker in top_stocks['Ticker']:
        st.write(f"Stock Data for {ticker}")
        ticker_data = stock_data[stock_data['Ticker'] == ticker]
        st.line_chart(ticker_data[['Close', 'SMA_10', 'SMA_50']])
        st.line_chart(ticker_data[['RSI']])
        st.line_chart(ticker_data[['MACD']])
        st.line_chart(ticker_data[['ADX']])
        st.line_chart(ticker_data[['RVOL']])
