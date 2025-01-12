import { writable, derived, get } from 'svelte/store';
import type { MarketData, Quote, QuoteMap, Selection } from '$lib/types/market';

const initialMarketData: MarketData = {
    indices: ['NIFTY', 'BANKNIFTY'],
    expiryDates: [],
    quotes: {},
    strikes: () => []
};

function findClosestStrike(strikes: number[], target: number): number {
    return strikes.reduce((prev, curr) => 
        Math.abs(curr - target) < Math.abs(prev - target) ? curr : prev
    );
}

function createMarketStore() {
    // Initialize with default values
    const { subscribe, set } = writable<MarketData[]>([]);
    const selectedIndex = writable('NIFTY');
    const selectedExpiry = writable('');
    const selectedStrike = writable('');
    
    // Initialize other stores
    const quotes = writable<QuoteMap>({});
    const loading = writable(false);
    const lastUpdate = writable<Date | null>(null);

    // Create derived stores
    const indices = derived([{ subscribe }], ([$data]) => 
        [...new Set($data.map(d => d.index))] || ['NIFTY', 'BANKNIFTY']
    );

    const expiryDates = derived(
        [{ subscribe }, selectedIndex],
        ([$data, $selectedIndex]) => 
            [...new Set($data
                .filter(d => d.index === $selectedIndex)
                .map(d => d.expiry)
            )].sort((a, b) => new Date(a).getTime() - new Date(b).getTime()) || []
    );

    const getStrikes = (index: string, expiry: string) => {
        const data = get(marketData);
        return [...new Set(data
            .filter(d => d.index === index && d.expiry === expiry)
            .map(d => d.strike)
        )].sort((a, b) => a - b);
    };

    async function initializeSelection(marketData: MarketData[]) {
        const index = 'NIFTY';
        const filteredData = marketData.filter(d => d.index === index);
        
        // Get nearest expiry
        const expiryDates = [...new Set(filteredData.map(d => d.expiry))]
            .sort((a, b) => new Date(a).getTime() - new Date(b).getTime());
        const nearestExpiry = expiryDates[0];

        // Get available strikes for this expiry
        const strikes = [...new Set(filteredData
            .filter(d => d.expiry === nearestExpiry)
            .map(d => d.strike)
        )].sort((a, b) => a - b);

        // Get quote or use default
        let quote;
        try {
            const response = await fetch(`/api/quote/${index}`);
            quote = await response.json();
        } catch (error) {
            console.error('Failed to fetch quote:', error);
            quote = 24000; // Default value for NIFTY
        }

        // Find closest strike to current quote
        const closestStrike = findClosestStrike(strikes, quote);

        // Set initial selections
        selectedIndex.set(index);
        selectedExpiry.set(nearestExpiry);
        selectedStrike.set(closestStrike.toString());

        return { index, expiry: nearestExpiry, strike: closestStrike };
    }

    async function loadData() {
        loading.set(true);
        try {
            const response = await fetch('/api/market-data');
            const data: MarketData[] = await response.json();
            set(data);
            lastUpdate.set(new Date());
            
            // Initialize selection with proper values
            await initializeSelection(data);
            
            // Update quotes
            await updateQuotes();
        } catch (error) {
            console.error('Failed to load market data:', error);
        } finally {
            loading.set(false);
        }
    }

    const DEFAULT_VALUES = {
        'NIFTY': 24000,
        'BANKNIFTY': 50000,
        'SENSEX': 60000,
        'BANKEX': 50000,
        'MIDCAPNIFTY': 12000
    };

    async function updateQuotes() {
        const currentIndices = get(indices);
        const quotes: QuoteMap = {};
        
        await Promise.all(currentIndices.map(async (index) => {
            try {
                const response = await fetch(`/api/quote/${index}`);
                const quote = await response.json();
                quotes[index] = quote || DEFAULT_VALUES[index] || 0;
            } catch (error) {
                console.error(`Failed to fetch quote for ${index}:`, error);
                quotes[index] = DEFAULT_VALUES[index] || 0;
            }
        }));
        
        quotes.set(quotes);
    }

    function setSelections(index: string, expiry: string, strike: string) {
        selectedIndex.set(index);
        selectedExpiry.set(expiry);
        selectedStrike.set(strike);
    }

    return {
        subscribe,
        indices,
        expiryDates,
        strikes: getStrikes,
        quotes: { subscribe: quotes.subscribe },
        isLoading: { subscribe: loading.subscribe },
        lastUpdate: { subscribe: lastUpdate.subscribe },
        loadData,
        updateQuotes,
        selected: {
            index: { subscribe: selectedIndex.subscribe, set: selectedIndex.set },
            expiry: { subscribe: selectedExpiry.subscribe, set: selectedExpiry.set },
            strike: { subscribe: selectedStrike.subscribe, set: selectedStrike.set }
        },
        setSelections
    };
}
export const marketStore = createMarketStore();
