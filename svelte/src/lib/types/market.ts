export interface MarketData {
    index: string;
    expiry: string;
    strike: number;
    callPrice: number;
    putPrice: number;
}

export interface Quote {
    last: number;
    change: number;
    volume: number;
    timestamp: string;
}

export type QuoteMap = Record<string, Quote>;