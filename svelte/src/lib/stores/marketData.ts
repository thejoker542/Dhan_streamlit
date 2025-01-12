import { writable, get } from 'svelte/store';
import type { MarketData, QuoteMap } from '$lib/types/market';

interface MarketStore {
    masterData: MarketData[];
    quotes: QuoteMap;
    lastUpdate: Date | null;
    isLoading: boolean;
}

const initialState: MarketStore = {
    masterData: [],
    quotes: {},
    lastUpdate: null,
    isLoading: false
};

export const marketStore = writable<MarketStore>(initialState);

const INDICES = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'BANKEX', 'MIDCAPNIFTY'];

export async function loadMarketData() {
    const { isLoading, lastUpdate } = get(marketStore);
    const now = new Date();
    
    // Don't reload if already loading or if last update was recent
    if (isLoading || (lastUpdate && (now.getTime() - lastUpdate.getTime()) < 10000)) {
        return;
    }

    marketStore.update(state => ({ ...state, isLoading: true }));

    try {
        // Load master data
        const masterResponse = await fetch('/api/master-data');
        const masterData = await masterResponse.json();

        // Load quotes for each index
        const quotesData: QuoteMap = {};
        await Promise.all(INDICES.map(async (index) => {
            try {
                const quoteResponse = await fetch(`/api/quote/${index}`);
                if (!quoteResponse.ok) throw new Error(`Failed to fetch quote for ${index}`);
                quotesData[index] = await quoteResponse.json();
            } catch (error) {
                console.error(`Error loading quote for ${index}:`, error);
                quotesData[index] = { last: 0, change: 0, volume: 0, timestamp: now.toISOString() };
            }
        }));

        marketStore.update(state => ({
            ...state,
            masterData,
            quotes: quotesData,
            lastUpdate: now,
            isLoading: false
        }));
    } catch (error) {
        console.error('Failed to load market data:', error);
        marketStore.update(state => ({ ...state, isLoading: false }));
    }
}
