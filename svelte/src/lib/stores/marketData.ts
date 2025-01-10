import { writable } from 'svelte/store';

export const masterData = writable<any[]>([]);
export const quotes = writable<Record<string, any>>({});
export const lastUpdate = writable<Date | null>(null);
export const isLoading = writable(false);

const INDICES = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'BANKEX', 'MIDCAPNIFTY'];

export async function loadMarketData() {
    const now = new Date();
    const lastUpdateTime = get(lastUpdate);
    
    // Check if reload is needed:
    // 1. If no last update
    // 2. If it's past 8:30 AM IST and last update was > 10 hours ago
    const needsReload = !lastUpdateTime || (
        now.getHours() >= 8 && now.getMinutes() >= 30 && 
        (now.getTime() - lastUpdateTime.getTime()) > 10 * 60 * 60 * 1000
    );

    if (needsReload) {
        isLoading.set(true);
        try {
            // Load master file
            const masterResponse = await fetch('/api/master-data');
            const masterJson = await masterResponse.json();
            masterData.set(masterJson);

            // Load quotes for each index
            const quotesData: Record<string, any> = {};
            await Promise.all(INDICES.map(async (index) => {
                const quoteResponse = await fetch(`/api/quote/${index}`);
                quotesData[index] = await quoteResponse.json();
            }));
            quotes.set(quotesData);

            lastUpdate.set(now);
        } catch (error) {
            console.error('Failed to load market data:', error);
        } finally {
            isLoading.set(false);
        }
    }
}
