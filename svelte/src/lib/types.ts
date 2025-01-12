export interface MarketData {
    indices: string[];
    expiryDates: string[];
    quotes: Record<string, { last: number }>;
    strikes: (index: string, expiry: string) => number[];
}

export interface Selection {
    index: string;
    expiry: string;
    strike: string;
}