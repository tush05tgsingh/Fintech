import React, { useState } from 'react';
import { runArima } from '../api';

type Props ={
    ticker: string;
    start_date: string;
    end_date: string;
    onResult: (data:any) => void;
}

interface pdq {
    p : number; // Autoregressive order - no of past observations included 
    d : number; //Integrated order - no of times data is differenced
    q : number; //Moving Average order - no of past forecast errors 
}

// --- INITIAL STATE ---
const initialPdq: pdq = { p: 1, d: 0, q: 1 };

export default function ForecastControls({ticker, start_date, end_date, onResult}:Props){
    const [order, setOrder] = useState<pdq>(initialPdq);
    const [auto, setAuto] = useState<boolean>(true);
    const [test_size, setTestSize] = useState<number>(0.2);
    const [steps, setSteps] = useState<number>(20);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const handleOrderChange = (e: React.ChangeEvent<HTMLInputElement>, param: keyof pdq) => {
        const value = parseInt(e.target.value, 10);

        if (isNaN(value) || value < 0) {
            setErrorMessage(`ARIMA parameter ${param.toUpperCase()} must be a non-negative integer.`);
            return;
        }

        setErrorMessage(null); // Clear previous errors
        setOrder(prevOrder => ({
            ...prevOrder,
            [param]: value,
        }));
    };

    async function submit(){
        setLoading(true);
        const payload = {ticker, start_date, end_date, order, steps, test_size, auto};
        try{
            const res = await runArima(payload);
            console.log(res);
            onResult(res);
        } catch (err) {
            alert(String(err));
        } finally {
            setLoading(false);
        }
    }

    return(
        <div className="p-4 bg-gray-800 rounded mb-4">
            <div className="flex gap-2 items-center">
                 {/* P Input */}
                <div className="flex items-center gap-1">
                    <label htmlFor="p-input" className='text-sm text-gray-300 font-medium'>P</label>
                    <input 
                        id="p-input"
                        type='number' 
                        value={order.p} 
                        onChange={(e) => handleOrderChange(e, 'p')} 
                        className="w-16 p-1 rounded bg-gray-700 text-white border border-gray-600 focus:ring-teal-500 focus:border-teal-500" 
                        min="0"
                    />
                </div>
                
                {/* D Input */}
                <div className="flex items-center gap-1">
                    <label htmlFor="d-input" className='text-sm text-gray-300 font-medium'>D</label>
                    <input 
                        id="d-input"
                        type='number' 
                        value={order.d} 
                        onChange={(e) => handleOrderChange(e, 'd')} 
                        className="w-16 p-1 rounded bg-gray-700 text-white border border-gray-600 focus:ring-teal-500 focus:border-teal-500" 
                        min="0"
                    />
                </div>
                
                {/* Q Input */}
                <div className="flex items-center gap-1">
                    <label htmlFor="q-input" className='text-sm text-gray-300 font-medium'>Q</label>
                    <input 
                        id="q-input"
                        type='number' 
                        value={order.q} 
                        onChange={(e) => handleOrderChange(e, 'q')} 
                        className="w-16 p-1 rounded bg-gray-700 text-white border border-gray-600 focus:ring-teal-500 focus:border-teal-500" 
                        min="0"
                    />
                </div>
                <div className="flex items-center gap-1">
                    <label htmlFor="q-input" className='text-sm text-gray-300 font-medium'>Test Size</label>
                    <input 
                        id="test_size_input"
                        type='number' 
                        value={test_size} 
                        onChange={(e) => setTestSize(parseFloat(e.target.value))} 
                        className="w-16 p-1 rounded bg-gray-700 text-white border border-gray-600 focus:ring-teal-500 focus:border-teal-500" 
                        min="0"
                    />
                </div>
                <label className="ml-2">
                    <input type="checkbox" checked={auto} onChange={(e)=>setAuto(e.target.checked)}  className="form-checkbox h-4 w-4 text-teal-500 rounded border-gray-600 bg-gray-700"/> Auto search
                </label>
                <button 
                    onClick={submit} 
                    className="ml-auto bg-teal-500 px-3 py-1 rounded"
                >
                    {loading ? "Running..." : "Run ARIMA"}
                </button>
                {/* Error Message Display */}
                {errorMessage && (
                    <div className="mt-4 p-2 bg-red-800 bg-opacity-30 border border-red-500 text-red-300 rounded-lg text-sm">
                        {errorMessage}
                    </div>
                )}
            </div>
            <div className="mt-2 text-xs text-gray-400">If Auto search is enabled, p/q will be found via a small grid (0..3).</div>
        </div>
    );
}