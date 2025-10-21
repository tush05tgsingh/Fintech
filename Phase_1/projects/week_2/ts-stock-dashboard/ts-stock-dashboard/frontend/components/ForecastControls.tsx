import React, { useState } from 'react';

type Props ={
    ticker: string;
    start: string;
    end: string;
    onResult: (data:any) => void;
}

export deafult function queryForcast({ticker, start, end, onResult}:Props){
    const [order, setOrder] = useState<list>();
    