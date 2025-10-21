const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function fetchStockData(ticker: string, start: string, end: string) {
    const res = await fetch('${BASE}/data?ticker=${ticker}&start=${start}&end=${end}');
    if (!res.ok) {
        throw new Error('Failed to fetch stock data');
    }
    return res.json();
}

export async function fetchForcastData(ticker: string) {
    const res = await fetch('${BASE}/forcast?ticker=${ticker}');
    if (!res.ok) {
        throw new Error('Failed to fetch forcast data');
    }
    return res.json();
}