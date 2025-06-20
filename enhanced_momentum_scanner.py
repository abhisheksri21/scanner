
import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Function to fetch stock data
def fetch_stock_data(ticker):
    stock_data = yf.download(ticker, period="1y", interval="1d")
    return stock_data

# Function to calculate momentum indicators
def calculate_indicators(stock_data):
    stock_data['RSI'] = ta.momentum.RSIIndicator(stock_data['Close']).rsi()
    stock_data['MACD'] = ta.trend.MACD(stock_data['Close']).macd_diff()
    stock_data['SMA_10'] = ta.trend.SMAIndicator(stock_data['Close'], window=10).sma_indicator()
    stock_data['SMA_50'] = ta.trend.SMAIndicator(stock_data['Close'], window=50).sma_indicator()
    stock_data['ADX'] = ta.trend.ADXIndicator(stock_data['High'], stock_data['Low'], stock_data['Close']).adx()
    stock_data['RVOL'] = stock_data['Volume'] / stock_data['Volume'].rolling(window=20).mean()
    return stock_data

# Function to apply quality filters
def apply_quality_filters(stock_data, roe_threshold, debt_to_equity_threshold):
    stock_data = stock_data[(stock_data['ROE'] > roe_threshold) & (stock_data['Debt_to_Equity'] < debt_to_equity_threshold)]
    return stock_data

# Function to rank stocks based on momentum
def rank_stocks(stock_data):
    stock_data['Momentum_Score'] = stock_data['RSI'] + stock_data['MACD'] + (stock_data['SMA_10'] - stock_data['SMA_50']) + stock_data['ADX'] + stock_data['RVOL']
    return stock_data

# Streamlit UI
st.title("Indian Stock Momentum Scanner")

# Dropdown to select index
indices = {
    "Nifty 50": "^NSEI",
    "Nifty Next 50": "^NSENEXT50",
    "Nifty 100": "^CNX100",
    "Nifty 200": "^CNX200",
    "Nifty 500": "^CNX500",
    "Nifty Midcap 50": "^CNXMID50",
    "Nifty Midcap 100": "^CNXMID100",
    "Nifty Midcap 150": "^CNXMID150",
    "Nifty Smallcap 50": "^CNXSMCAP50",
    "Nifty Smallcap 100": "^CNXSMCAP100",
    "Nifty Smallcap 250": "^CNXSMCAP250",
    "Nifty IT": "^CNXIT",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Bank": "^NSEBANK",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Auto": "^CNXAUTO",
    "Nifty Energy": "^CNXENERGY",
    "Nifty Realty": "^CNXREALTY"
}

index = st.selectbox("Select Stock Index", list(indices.keys()))

# Input for quality filters
roe_threshold = st.number_input("ROE Threshold", value=10.0)
debt_to_equity_threshold = st.number_input("Debt-to-Equity Threshold", value=1.0)

if index:
    # Fetch and display stock data
    index_ticker = indices[index]
    stock_data = fetch_stock_data(index_ticker)
    st.write(f"Stock Data for {index}")
    st.dataframe(stock_data.tail(10))

    # Calculate and display indicators
    stock_data = calculate_indicators(stock_data)
    st.write("Momentum Indicators")
    st.dataframe(stock_data[['RSI', 'MACD', 'SMA_10', 'SMA_50', 'ADX', 'RVOL']].tail(10))

    # Apply quality filters
    stock_data = apply_quality_filters(stock_data, roe_threshold, debt_to_equity_threshold)

    # Rank and display momentum stocks
    stock_data = rank_stocks(stock_data)
    top_stocks = stock_data.nlargest(5, 'Momentum_Score')
    st.write("Top 5 Momentum Stocks")
    st.dataframe(top_stocks[['Momentum_Score']])

    # Plotting
    for ticker in top_stocks.index:
        st.write(f"Stock: {ticker}")
        st.line_chart(stock_data.loc[ticker, ['Close', 'SMA_10', 'SMA_50']])
        st.line_chart(stock_data.loc[ticker, ['RSI']])
        st.line_chart(stock_data.loc[ticker, ['MACD']])
        st.line_chart(stock_data.loc[ticker, ['ADX']])
