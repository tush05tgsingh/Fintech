import {useState} from 'react';
import {LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from 'recharts';
import FileUploader from '../components/FileUploader';
import './App.css';


// Interface defines the structure of stock data
interface StockData {
  date: string;
  price: number;
  returns: number;
}

type ForcastPoint = {
  date: string;
  predictedPrice: number;
}

const mockStockData: StockData[] = [
  {date: '2023-01-01', price: 150, returns: 0},
  {date: '2023-01-02', price: 155, returns: 0.033},
  {date: '2023-01-03', price: 160, returns: 0.032},
  {date: '2023-01-04', price: 158, returns: -0.0125},
  {date: '2023-01-05', price: 162, returns: 0.0253},
];

export default function App(){
  const[ticker, setTicker] = useState<string>('APPL'); //useState<Type> type-safe react state
  const[data, setData] = useState<StockData[]>([]); // Initial mock data
  const[forcastData, setForcastData] = useState<ForcastPoint[]>([]);
  const[view, setView] = useState<"price" | "returns">("price");

  const handleForcast = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if(!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const json = JSON.parse(event.target?.result as string);
      const formatted = json.dates.map((d:string, i:number) => ({date: d, predictedPrice: json.prices[i]}));
      setForcastData(formatted);  
    }
    reader.readAsText(file);
  };

  return(
    <div style={{padding: "10px", fontFamily: 'Arial, sans-serif'}}>
      <h1>Stock Analysis Dashboard</h1>
      <label>
        Enter Stock Ticker:
        <select value={ticker} onChange={(e) => setTicker(e.target.value)} style={{marginLeft: '10px', padding: '5px'}}>
          <option value="APPL">APPL</option>
          <option value="GOOGL">GOOGL</option>
          <option value="MSFT">MSFT</option>
        </select>
      </label>
      <h2 style={{marginTop: '20px'}}>Mock closing price for {ticker}</h2> {/* Dynamic title mix of JSX+TSX */}

      <ul>
        {mockStockData.map((data) => (
          <li key={data.date}>{data.date}: ${data.price}</li>
        ))}
      </ul>

      <FileUploader onDataLoaded={setData}/>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
            Upload Forcast JSON:
            <input type="file" accept=".json" onChange={handleForcast} className="bg-gray-800 p-2 rounded cursor-pointer hover:bg-gray-700"/>
        </label>
      </div>

      
      
      {data.length > 0 && forcastData.length > 0 ? (
      <>
        <div className ="flex gap-4 mb-6">
          <button onClick={() => setView("price")}
            className={`px-4 py-2 rounded ${view === "price" ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}>
            Price View
          </button>
          <button onClick={() => setView("returns")}
            className={`px-4 py-2 rounded ${view === "returns" ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}>
            Returns View
          </button>
        </div>
        {view === "price" ? (
          // Price Line Chart
            <div className="bg-gray-800 rounded-2xl p-4 mb-8 shadow-lg">
              <h2 className="text-white text-xl mb-4">Stock Prices Over Time</h2>
              <LineChart width={600} height={300} data={[...mockStockData, ...forcastData]}>
                <XAxis dataKey="date" stroke="#ccc"/>
                <YAxis stroke="#ccc"/>
                <Tooltip/>
                <CartesianGrid stroke="#555" strokeDasharray="3 3"/>
                <Line type="monotone" dataKey="price" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="predictedPrice" stroke="#82ca9d" strokeDasharray="5 5"/>
              </LineChart>
            </div>
          ):(
          // Returns Bar Chart
          <div className="bg-gray-800 rounded-2xl p-4 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Return Distribution</h2>
            <BarChart width={700} height={300} data={mockStockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#555" />
              <XAxis dataKey="date" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip />
              <Bar dataKey="returns" fill="#F6AD55" />
            </BarChart>
          </div>
        )}
      </>  
      ) : (
        <p className="text-gray-400">Please upload the csv to begin</p>)
      } 
      </div>
  );
}