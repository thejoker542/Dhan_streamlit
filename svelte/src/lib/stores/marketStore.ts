
import { writable, derived, get } from 'svelte/store';
import type { MarketData, Quote, QuoteMap } from '$lib/types/market';

function createMarketStore() {
    const { subscribe, set, update } = writable<MarketData[]>([]);
    const { subscribe: quotesSubscribe, set: quotesSet } = writable<QuoteMap>({});
    const { subscribe: loadingSubscribe, set: loadingSet } = writable(false);
    const { subscribe: lastUpdateSubscribe, set: lastUpdateSet } = writable<Date | null>(null);

    // Derived stores for unique values
    const indices = derived({ subscribe }, ($marketData) => 
        [...new Set($marketData.map(d => d.index))]
    );

    const expiryDates = derived({ subscribe }, ($marketData) => 
        (index: string) => [...new Set($marketData
            .filter(d => d.index === index)
            .map(d => d.expiry)
        )].sort()
    );

    const strikes = derived({ subscribe }, ($marketData) => 
        (index: string, expiry: string) => [...new Set($marketData
            .filter(d => d.index === index && d.expiry === expiry)
            .map(d => d.strike)
        )].sort((a, b) => a - b)
    );

    async function loadData() {
        const now = new Date();
        const lastUpdate = get(lastUpdateSubscribe);
        
        const needsReload = !lastUpdate || (
            now.getHours() >= 8 && 
            now.getMinutes() >= 30 && 
            (now.getTime() - lastUpdate.getTime()) > 10 * 60 * 60 * 1000
        );

        if (needsReload) {
            loadingSet(true);
            try {
                const response = await fetch('/api/market-data');
                const data: MarketData[] = await response.json();
                set(data);
                lastUpdateSet(now);
                
                // Also update quotes
                await updateQuotes();
            } catch (error) {
                console.error('Failed to load market data:', error);
            } finally {
                loadingSet(false);
            }
        }
    }

    async function updateQuotes() {
        const currentIndices = get(indices);
        const quotes: QuoteMap = {};
        
        await Promise.all(currentIndices.map(async (index) => {
            try {
                const response = await fetch(`/api/quote/${index}`);
                quotes[index] = await response.json();
            } catch (error) {
                console.error(`Failed to fetch quote for ${index}:`, error);
            }
        }));
        
        quotesSet(quotes);
    }

    return {
        subscribe,
        indices: { subscribe: indices.subscribe },
        expiryDates,
        strikes,
        quotes: { subscribe: quotesSubscribe },
        isLoading: { subscribe: loadingSubscribe },
        lastUpdate: { subscribe: lastUpdateSubscribe },
        loadData,
        updateQuotes
    };
}

export const marketStore = createMarketStore();