from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Dict, Any
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from pydantic import BaseModel
from statsmodels.tsa.stattools import acf, pacf
from mangum import Mangum 

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "pong"}

handler = Mangum(app) 

#allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ARIMARequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    order: dict  # ARIMA order (p, d, q)
    steps: int
    test_size : float
    auto: bool = True

    class Config:
        extra = "ignore"

class ARIMAResponse(BaseModel):
    residuals_summary: Dict[str, float]
    forecast: List[float]
    dates: List[str]
    explanation:str

def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    try:
        stock = yf.download(ticker, start=start_date, end=end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yahoo Finance error: {str(e)}")

    # If no data returned
    if stock is None or stock.empty:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")

    # Check if Close column exists
    if "Close" not in stock.columns:
        raise HTTPException(status_code=500, detail="Unexpected data format from Yahoo")

    # Keep only Close prices
    stock = stock[["Close"]].rename(columns={"Close": "price"})
    stock.index = pd.to_datetime(stock.index)
    stock = stock.sort_index()
    return stock

def compute_returns(data: pd.DataFrame) -> pd.DataFrame:
    data['returns'] = data['price'].pct_change().dropna()
    return data

def search_best_order(train, d, p_max=4, q_max=4):
    best_aic = float("inf")
    best_order = None
    best_model = None

    for p in range(p_max + 1):
        for q in range(q_max + 1):
            try:
                model = ARIMA(train, order=(p, d, q)).fit()
                if model.aic < best_aic:
                    best_aic = model.aic
                    best_order = (p, d, q)
                    best_model = model
            except:
                continue

    print("Best order found:", best_order)
    return best_model

def adf_test(series, name=''):
    result = adfuller(series.dropna())
    print(f"ADF Test for {name}: stat={result[0]:.4f}, p-value={result[1]:.4f}")
    response = "Null Hypothesis (H0): The series is non-stationary.\n"
    if result[1] < 0.05:
        response += f"--> {name} is stationary (reject H0)"
    else:
        response += f"--> {name} is non-stationary (fail to reject H0)"
    return result, response

def kpss_test(series, name=''):
    result = kpss(series.dropna(), regression='c', nlags="auto")
    print(f"KPSS Test for {name}: stat={result[0]:.4f}, p-value={result[1]:.4f}")
    response = "Null Hypothesis (H0): The series is stationary.\n"
    if result[1] < 0.05:
        response += f"--> {name} is stationary (reject H0)"
    else:
        response += f"--> {name} is non-stationary (fail to reject H0)"
    return result, response

def train_test_split(series, test_size = 0.2):
    split_idx = int(len(series) * (1-test_size))
    train = series.iloc[:split_idx]
    test = series.iloc[split_idx:]
    return train, test 

def get_acf_pacf(series, nlags=40):
    return {
        "acf": acf(series, nlags=nlags).tolist(),
        "pacf": pacf(series, nlags=nlags).tolist(),
        "lags": list(range(nlags + 1))
    }
    
@app.get("/api/data")
async def get_data(
    ticker: str = "AAPL",
    start_date: str = "2020-01-01",
    end_date: str = "2024-01-01"
) -> Dict[str, Any]:

    # Get price data
    try:
        stock_data = fetch_stock_data(ticker, start_date, end_date)
    except HTTPException as e:
        raise e

    # Compute returns
    stock_returns = compute_returns(stock_data)
    returns = stock_returns["returns"].dropna().values  # 1D array

    stock_data = stock_data["price"].reset_index()
    # Basic statistics
    skewness = stats.skew(returns)
    kurtosis = stats.kurtosis(returns)
    jb_stat, jb_pvalue = stats.jarque_bera(returns)

    # ADF
    adf_result = adfuller(returns)
    adf_stat = adf_result[0]
    adf_pvalue = adf_result[1]

    # KPSS (safe)
    try:
        kpss_stat, kpss_pvalue, _, _ = kpss(returns, regression="c")
    except Exception:
        kpss_stat, kpss_pvalue = None, None

    # ACF
    nlags = min(20, len(returns) - 1)
    acf_vals = acf(returns, nlags=nlags, fft=False, adjusted=False).tolist()

    payload = {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "n_obs": int(len(returns)),

        "skewness": float(skewness),
        "kurtosis": float(kurtosis),

        "jarque_bera": {
            "statistic": float(jb_stat),
            "p_value": float(jb_pvalue)
        },

        "adf": {
            "statistic": float(adf_stat),
            "p_value": float(adf_pvalue)
        },

        "kpss": {
            "statistic": kpss_stat,
            "p_value": kpss_pvalue
        },

        "acf": acf_vals,

        "price_data": [
           {"date": str(row["Date"].date()), "price": float(row[ticker])}
            for _, row in stock_data.iterrows()
        ],

        "returns_data": [
            {"date": str(date.date()), "return": float(ret)} for date, ret in zip(stock_returns.index, stock_returns["returns"])
        ],
    }

    return payload

@app.post("/api/arima")
async def get_arima_forcast(request: ARIMARequest):
    # --- Validate input ---
    if not request.ticker or not request.start_date or not request.end_date or not request.test_size:
        raise HTTPException(status_code=400, detail="Invalid input parameters")

    # --- Fetch and prepare data ---
    stock_data = fetch_stock_data(request.ticker, request.start_date, request.end_date)
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.droplevel(1)
    
    prices = stock_data['price'].dropna()
    returns_data = compute_returns(stock_data)
    returns = returns_data['returns'].dropna()

    prices = prices.squeeze()    # DataFrame -> Series
    returns = returns.squeeze()

    # ----- test Adf and kssp for stationary test 
    adf_result, adf_response = adf_test(returns, 'Returns')
    kpss_result, kpss_response = kpss_test(returns, 'Returns')
    acf_pacf_prices = get_acf_pacf(prices)
    acf_pacf_returns = get_acf_pacf(returns)

    # -- create train and test series for returns and prices ---
    returns_train, returns_test = train_test_split(returns, test_size=request.test_size)
    prices_train, prices_test = train_test_split(prices, test_size=request.test_size)

    # --- Model selection ---
    p = request.order.get("p", 1)
    d = request.order.get("d", 0)
    q = request.order.get("q", 1)

    # Auto mode: search small grid
    if request.auto:
        best_model = search_best_order(returns_train, d=0, p_max=3, q_max=3)
    else:
        best_model = ARIMA(returns_train, order=(p, d, q)).fit()

    # --- Forecast returns ---
    steps = len(returns_test)

    # Correct method: get_forecast
    forecast_result = best_model.get_forecast(steps=steps)

    forecasted_returns = forecast_result.predicted_mean
    ci = forecast_result.conf_int(alpha=0.05)

    # Align forecast index to test index
    forecasted_returns.index = returns_test.index
    ci.index = returns_test.index

    # 3. Convert returns → forecasted prices
    last_train_price = float(prices_train.iloc[-1])

    forecast_prices = []
    current_price = last_train_price

    for r in forecasted_returns:
        current_price *= (1 + r)
        forecast_prices.append(current_price)   # ← moved inside loop

    # 4. Forecast dates = test price dates
    forecast_dates = prices_test.index.strftime("%Y-%m-%d").tolist()

    # --- Residuals diagnostics ---
    resid = best_model.resid.dropna()

    lj = acorr_ljungbox(resid, lags=[5,10,20], return_df=True)

    lj_p = {str(k): float(lj.loc[k, "lb_pvalue"]) 
            for k in lj.index if k in [5,10,20]}

    resid_summary = {
        "mean": float(resid.mean()),
        "std": float(resid.std()),
        "skewness": float(stats.skew(resid)),
        "kurtosis": float(stats.kurtosis(resid, fisher=False)),
    }

    explanation = ""
    if request.order['d']>=1: #differencing 
        explanation+=" The time series was differenced to achieve stationarity."
    else: 
        explanation+=" The time series was stationary and did not require differencing." 
    # AIC/BIC note 
    explanation+= f" The ARIMA model was selected based on AIC/BIC criteria to balance fit and complexity." 
    # residuals 
    if all(p > 0.05 for p in lj_p.values()): 
        explanation+=" The Ljung-Box test indicates that residuals are uncorrelated, suggesting a good model fit."
    else: 
        explanation+=" The Ljung-Box test indicates that some residual correlation remains, suggesting the model may be improved." # forecast uncertainty 
    if forecasted_returns.iloc[-1] > forecasted_returns.iloc[0]: 
        explanation+=" The forecast indicates an upward trend in returns"
    else: 
        explanation+=" The forecast indicates a downward trend in returns"


    # --- Return clean response ---
    res =  {
        "ticker": request.ticker,
        "prices": prices,
        "returns": returns,
        "order": request.order,
        "aic": float(best_model.aic),
        "bic": float(best_model.bic),
        "forecast_dates": forecast_dates,
        "forecast": forecast_prices,
        "lower_ci": ci.iloc[:, 0].tolist(),
        "upper_ci": ci.iloc[:, 1].tolist(),
        "residuals_summary": resid_summary,
        "ljungbox_pvalues": lj_p,
        "explanation":explanation,
        "adf":{"result":adf_result, "response":adf_response},
        "kpss":{"result":kpss_result, "response":kpss_response},
        "acf_pacf": {
            "prices": acf_pacf_prices,
            "returns": acf_pacf_returns
        }
    }
    return res


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

