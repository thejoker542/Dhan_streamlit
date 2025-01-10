
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';
import { join } from 'path';
import type { MarketData } from '$lib/types/market';

export const GET: RequestHandler = async () => {
    try {
        const filePath = join(process.cwd(), 'backend', 'data', 'master_file.csv');
        const fileContent = readFileSync(filePath, 'utf-8');
        
        const records: MarketData[] = parse(fileContent, {
            columns: true,
            skip_empty_lines: true,
            cast: (value, context) => {
                if (context.column === 'strike') return Number(value);
                if (context.column === 'callPrice' || context.column === 'putPrice') return Number(value);
                return value;
            }
        });

        return json(records);
    } catch (error) {
        console.error('Error reading market data:', error);
        return new Response('Failed to load market data', { status: 500 });
    }
};