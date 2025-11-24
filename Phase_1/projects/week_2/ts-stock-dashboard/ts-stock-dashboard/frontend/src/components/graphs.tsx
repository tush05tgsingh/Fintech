import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from "recharts";

type Props = {
  title: string;
  data: any;
}
export default function ACFPACFChart({ title, data }:Props) {
  const chartData = data.lags.map((lag:any, i:number) => ({
    lag,
    acf: data.acf[i],
    pacf: data.pacf[i],
  }));

  return (
    <div className="mb-6">
      <h3 className="text-white text-lg mb-2">{title}</h3>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#555" />
            <XAxis dataKey="lag" stroke="#aaa" />
            <YAxis stroke="#aaa" />
            <Tooltip />
            <Legend />

            <Line dataKey="acf" stroke="#82ca9d" dot={false} name="ACF" />
            <Line dataKey="pacf" stroke="#8884d8" dot={false} name="PACF" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
