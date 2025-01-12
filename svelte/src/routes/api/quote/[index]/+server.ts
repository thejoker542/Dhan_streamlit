import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
    try {
        // Mock quote data for now
        const quote = {
            last: 19000 + Math.random() * 1000,
            change: (Math.random() - 0.5) * 2,
            volume: Math.floor(Math.random() * 1000000),
            timestamp: new Date().toISOString()
        };

        return json(quote);
    } catch (error) {
        console.error(`Error fetching quote for ${params.index}:`, error);
        return new Response('Failed to fetch quote', { status: 500 });
    }
};