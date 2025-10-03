# save as app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
import yfinance as yf

# Load data from Yahoo Finance
@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data.reset_index(inplace=True)  # make Date a column
    return data

st.title("📊 Time Series Dashboard")

# Sidebar inputs
ticker = st.sidebar.selectbox("Select Ticker", ["AAPL", "MSFT", "GOOGL"])
date_range = st.sidebar.date_input(
    "Select Date Range", 
    [pd.to_datetime("2020-01-01"), pd.to_datetime("2023-01-01")]
)

# Load data
df = load_data(ticker, date_range[0], date_range[1])

# Analysis option
analysis_option = st.selectbox(
    "Choose analysis to perform:",
    ["Raw Series", "SMA", "ADF Test", "ACF Plot"]
)

if analysis_option == "Raw Series":
    st.write("### Closing Price Over Time")
    st.line_chart(df.set_index("Date")["Close"])

elif analysis_option == "SMA":
    st.write("### Simple Moving Average (SMA)")
    window = st.slider("Select SMA Window", 2, 60, 7)
    df["SMA"] = df["Close"].rolling(window=window).mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot( df["Close"], label="Close Price", color="blue")
    ax.plot( df["SMA"], label=f"SMA {window}", color="red")

    ax.set_title(f"{ticker} Closing Price with SMA ({window}-day)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
    st.write(f"SMA smooths out price data to identify trends over a {window}-day window.The SMA is one of the most fundamental indicators. It takes the `average` of a stock's closing price over a specific number of days.- *Why is it useful?* The SMA helps to smooth out price data, making it easier to see the overall trend. A short-term SMA (like the 10-day) reacts quickly to price changes, while a long-term SMA (like the 50-day) is much slower and shows the bigger picture. When a short-term SMA crosses above a long-term SMA, it's often seen as a bullish signal (a sign of a rising trend), and a cross below is a bearish signal (a sign of a falling trend). By including these as features, our model can learn these trend-following patterns.")

elif analysis_option == "ADF Test":
    st.write("### Augmented Dickey-Fuller Test for Stationarity")
    result = adfuller(df["Close"].dropna())
    st.write(f"ADF Statistic: {result[0]:.4f}")
    st.write(f"p-value: {result[1]:.4f}")
    st.write(f"Lags Used: {result[2]}")
    st.write(f"Number of Observations: {result[3]}")
    st.write("A stationary time series is one whose properties don’t change over time.That means:- Constant mean → it doesn’t drift upward or downward.- Constant variance → volatility doesn’t keep changing.- Constant autocorrelation structure → relationship between today and yesterday is stable.Non-stationary : like stock prices and Stationary : like stock returns (percentage change).We care about the stationarity because most ML models assume the data is stationary. because if it is not stationary then this happens : if trends stay up forever, a model learns that values stay up. if varience keeps changing, your confidence intervals are meaningless. If autocorrelations shift, yesterday's pattern doesn't help predict tomorrow. So predictions become misleading. The ADF test helps us check stationarity. The null hypothesis (H₀) is that the series is non-stationary. The alternative (H₁) is that the series is stationary. If the p-value is below a threshold (like 0.05), we reject H₀ and conclude the series is stationary. If above, we fail to reject H₀, suggesting non-stationarity.")

elif analysis_option == "ACF Plot":
    st.write("### Autocorrelation Function (ACF) Plot")
    fig, ax = plt.subplots()
    plot_acf(df["Close"].dropna(), ax=ax, lags=30)
    st.pyplot(fig)
    st.write("The ACF plot shows how the time series is correlated with its own past values at different lags. If the autocorrelation drops off quickly, it suggests that past values have less influence on future values, indicating a more random series. If the autocorrelation remains high for many lags, it suggests that past values strongly influence future values, indicating a more predictable series. In stock prices, we often see weak autocorrelation, meaning past prices don't strongly predict future prices. However, in stock returns (percentage changes), we might see stronger autocorrelation, especially over short lags. This can be useful for short-term trading strategies.")