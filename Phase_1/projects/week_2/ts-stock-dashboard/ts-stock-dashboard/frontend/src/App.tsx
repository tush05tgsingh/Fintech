import {useState} from 'react';
import {LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import ACFPACFChart from "./components/graphs";
import ForecastControls from "./components/ForecastControls";
import './App.css';
import { fetchStockData } from './api';

type DataPoint = {
  date:string;
  price?:number;
  return?:number;
  forecast?:number;
}

export default function App(){
  const [ticker, setTicker] = useState("AAPL");
  const [start, setStart] = useState("2020-01-01");
  const [end, setEnd] = useState("2024-12-31");
  const [data, setData] = useState<DataPoint[]>([]);
  const [caldata, setcaldata] = useState<DataPoint[]>([]);
  const [forecast, setForecast] = useState<any | null>(null);
  const [stats, setStats] = useState<any | null>(null);

  async function load(){
    const res = await fetchStockData(ticker, start, end);
    console.log("API response:", res);
    setData(res.price_data.map((p:any)=>({
      date:p.date, price:p.price})));
    setStats(res);
  }

  function handleArimaResult(res: any){
    setForecast(res);
    
    const historicalPoints: DataPoint[] = Object.entries(res.prices).map(
      ([date, val]: any) => ({
        date: new Date(date).toISOString().split("T")[0],
        price: val,
      })
    );


    console.log(historicalPoints)

    const forecastPoints: DataPoint[] = res.forecast_dates.map(
      (date: string, i: number) => ({
        date,
        forecast: res.forecast[i],
      })
    );

    const merged = [...historicalPoints, ...forecastPoints];

    // 4) Store in state
    setcaldata(merged);
  }

  return(
    <div style={{padding: "10px", fontFamily: 'Arial, sans-serif'}}>
      <h1 className="text-2xl font-semibold flex items-center gap-2">
          Stock Analysis Dashboard 
          <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-md shadow-sm cursor-default select-none">
            React
          </span>
          <span className="px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700 rounded-md shadow-sm cursor-default select-none">
            TypeScript
          </span>
          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-md shadow-sm cursor-default select-none">
            FastAPI
          </span>
        </h1>

      <div className="flex gap-2 mb-4">
        <input value={ticker} onChange={(e)=>setTicker(e.target.value)} className='p-2 rounded bg-gray-800' />
        <input value={start} onChange={(e)=>setStart(e.target.value)} className='p-2 rounded bg-gray-800' />
        <input value={end} onChange={(e)=>setEnd(e.target.value)} className='p-2 rounded bg-gray-800' />
        <button onClick={load} className='bg-teal-500 px-3 rounded'>Load</button>
      </div>

      <ForecastControls ticker={ticker} start_date={start} end_date={end} onResult={handleArimaResult}/>

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
        <div className='bg-gray-800 rounded p-4'>
          {data ? (
            <div><h3 className='font-semibold mb-2'>Price Chart</h3>
          <LineChart width={500} height={400} data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#555" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price" stroke="#4FD1C5" dot={false} />
            <Line type="monotone" dataKey="forecast" stroke="#F6AD55" strokeDasharray="5 5" dot={false} />
          </LineChart></div>): <div>price chart</div>}
          {caldata? (
            <div>
              <LineChart width={500} height={400} data={caldata}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />

              <Line
                type="monotone"
                dataKey="price"
                stroke="#aa3382ff"
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#f6ad55"
                strokeDasharray="4 4"
                dot={false}
              />
            </LineChart>
            </div>
          ): <div></div>}
        </div>

        <div className="bg-gray-800 rounded p-4">
          <h3 className="font-semibold mb-2">Summary</h3>
          {stats ? (
            <div>
              <div>Ticker: {ticker}</div>
              <div>Skewness: {stats.skewness.toFixed(4)}</div>
              <div>Kurtosis: {stats.kurtosis.toFixed(4)}</div>
              <div>ADF p-value (returns): {stats.adf.p_value.toFixed(4)}</div>
            </div>
          ) : <div>Load data to see stats</div>}
          {forecast ? (
            <div>
              <h4 className="mt-3">ARIMA Result</h4>
              <div>Order: ({forecast.order.p}, {forecast.order.d}, {forecast.order.q})</div>
              <div>AIC: {forecast.aic.toFixed(2)}  BIC: {forecast.bic.toFixed(2)}</div>
              <div className="mt-2 text-sm text-gray-300">{forecast.explanation}</div>
              <ACFPACFChart title="ACF & PACF — Prices" data={forecast.acf_pacf.prices} />
              <ACFPACFChart title="ACF & PACF — Returns" data={forecast.acf_pacf.returns} />
            </div>
          ): <div>The forecast need to be calculated</div>}
        </div>
      </div>
    </div>
  );
}