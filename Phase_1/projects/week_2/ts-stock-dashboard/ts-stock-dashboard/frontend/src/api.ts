const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5173/api';

export async function fetchStockData(ticker: string, start: string, end: string) {
    const res = await fetch(`${BASE}/data?ticker=${ticker}&start=${start}&end=${end}`);
    if (!res.ok) {
        throw new Error('Failed to fetch stock data');
    }
    return res.json();
}

export async function runArima(payload: any) {
    const res = await fetch(`${BASE}/arima`,{
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    }
    );
    if (!res.ok) {
        throw new Error('Failed to fetch forcast data');
    }
    return res.json();
}