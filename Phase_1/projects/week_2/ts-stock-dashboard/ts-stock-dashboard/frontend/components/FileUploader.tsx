import React from 'react';
import Papa from "papaparse";

type Props = {
    onDataLoaded:(data:{date: string; price:number; returns:number}[]) => void;
};

export default function FileUploader({onDataLoaded}:Props){
    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if(!file) return;

        Papa.parse(file, {
            header: true,
            dynamicTyping: true,
            complete: (result) => {
                const data = result.data.map((row:any) => ({
                    date: row.date,
                    price: parseFloat(row.price),
                    returns: parseFloat(row.returns)
                }));
                onDataLoaded(data);
            },
            error: (error) => {
                console.error("Error parsing CSV:", error);
            }
        });
    };

    return(
        <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
                Upload CSV File:
                <input type="file" accept=".csv" onChange={handleFileUpload} className="bg-gray-800 p-2 rounded cursor-pointer hover:bg-gray-700"/>
            </label>
        </div>
    );
}