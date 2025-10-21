from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from pydantic import BaseModel

app = FastAPI()

#allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ARIMARequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    order: List[int]  # ARIMA order (p, d, q)
    forecast_periods: int

class ARIMAResponse(BaseModel):
    residuals_summary: Dict[str, float]
    forecast: List[float]
    dates: List[str]
    explanation:str

def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    stock = yf.download(ticker, start=start_date, end=end_date)
    if stock.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    stock = stock[['Close']].rename(columns={'Close': 'price'})
    stock.index = pd.to_datetime(stock.index)
    return stock

def compute_returns(data: pd.DataFrame) -> pd.DataFrame:
    data['returns'] = data['price'].pct_change().dropna()
    return data.dropna()

def search_best_order(series, d, p_max=4, q_max=4):
    best = None
    for p in range(p_max):
        for q in range(q_max):
            try:
                model = ARIMA(series, order=(p,d,q), enforce_stationarity=False)
                res = model.fit(disp=False)
                if best is None or res.aic <best.aic:
                    best = res
            except Exception as e:
                continue
    return best

@app.get("api/data")
async def get_data(ticker: str = "AAPL", start_date: str = "2020-01-01", end_date: str="2024-01-01") -> List[Dict[str, Any]]:
    try:
        stock_data = fetch_stock_data(ticker, start_date, end_date)
    except HTTPException as e:
        raise e
    stock_returns = compute_returns(stock_data)
    returns = stock_returns['returns']

    #Basic statistics
    skewness = stats.skew(returns)
    kurtosis = stats.kurtosis(returns)
    jb_stat, jb_pvalue = stats.jarque_bera(returns)
    adf_stat, adf_pvalue = adfuller(returns)
    kpss_stat, kpss_pvalue, _, _ = kpss(returns, regression='c')
    
    acff_vals = acf(returns, nlags=20, fft=False).tolist()

    payload = {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "n_obs": int(len(returns)),
        "skewness": skewness,
        "kurtosis": kurtosis,
        "jarque_bera": {"statistic": jb_stat, "p_value": jb_pvalue},
        "adf": {"statistic": adf_stat, "p_value": adf_pvalue},
        "kpss": {"statistic": kpss_stat, "p_value": kpss_pvalue},
        "acf": acff_vals,
        "price_data": [{"date": str(date.date()), "price": price} for date, price in zip(stock_data.index, stock_data['price'])],
        "returns_data": [{"date": str(date.date()), "return": returns} for date, returns in zip(stock_returns.index, stock_returns['returns'])]
    }

    return payload

async def get_arima_forcast(request: ARIMARequest) -> ARIMAResponse:
    if not request.ticker or not request.start_date or not request.end_date:
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    try:
        stock_data = fetch_stock_data(request.ticker, request.start_date, request.end_date)
    except HTTPException as e:
        raise e
    stock_returns = compute_returns(stock_data)
    returns = stock_returns['returns']

    # Fit ARIMA model
    if request.order == [0,0,0]:
        best_model = search_best_order(returns, d=1)
    else:
        best_model = search_best_order(returns, d=request.order[1], p_max=request.order[0]+1, q_max=request.order[2]+1)

    # Forecast future returns
    steps = int(request.forecast_periods or 20) # length of test set or default to 20
    forecast_result = best_model.get_forecast(steps=steps)
    forecasted_returns = forecast_result.predicted_mean
    ci = forecast_result.conf_int(alpha=0.05)

    # residual diagnostics
    lj = acorr_ljungbox(best_model.resid, lags=[5, 10, 20], return_df=True)
    lj_p = {
        "lb_lag5_pvalue": float(lj.loc[5, 'lb_pvalue']) if 5 in lj.index else float(lj['lb_pvalue'].iloc[0]),
        "lb_lag10_pvalue": float(lj.loc[10, 'lb_pvalue']) if 10 in lj.index else float(lj['lb_pvalue'].iloc[0]),
        "lb_lag20_pvalue": float(lj.loc[20, 'lb_pvalue']) if 20 in lj.index else float(lj['lb_pvalue'].iloc[0]),
    }

    # statistics summary of residuals
    resid_summary = {
        "mean'": float(best_model.resid.mean()),
        "std": float(best_model.resid.std()),
        "skewness": float(stats.skew(best_model.resid)),
        "kurtosis": float(stats.kurtosis(best_model.resid)),
    }

    # simple rule-based "AI" explanation
    explanation = []
    # stationarity tests
    if request.order[1]>=1: #differencing
        explanation.append("The time series was differenced to achieve stationarity.")
    else:
        explanation.append("The time series was stationary and did not require differencing.")
    # AIC/BIC note
    explanation.append(f"The ARIMA model was selected based on AIC/BIC criteria to balance fit and complexity.")
    # residuals
    if all(p > 0.05 for p in lj_p.values()):
        explanation.append("The Ljung-Box test indicates that residuals are uncorrelated, suggesting a good model fit.")
    else:
        explanation.append("The Ljung-Box test indicates that some residual correlation remains, suggesting the model may be improved.")
    # forecast uncertainty
    if forecasted_returns.iloc[-1] > forecasted_returns.iloc[0]:
        explanation.append("The forecast indicates an upward trend in returns")
    else:
        explanation.append("The forecast indicates a downward trend in returns")
    resultant_explanation = " ".join(explanation)
    

    # Convert returns to price forecast
    last_price = stock_data['price'].iloc[-1]
    forecasted_prices = []
    current_price = last_price
    for ret in forecasted_returns:
        current_price *= (1 + ret)
        forecasted_prices.append(current_price)

    forecast_dates = [(stock_data.index[-1] + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(request.forecast_periods)]

    response = ARIMAResponse(
        residuals_summary = resid_summary,
        forecast=forecasted_prices,
        dates=forecast_dates, 
        explanation=resultant_explanation
    )

    return response

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

