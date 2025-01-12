import { json } from '@sveltejs/kit';
import { mkdir } from 'fs/promises';
import { join } from 'path';
import type { RequestHandler } from './$types';
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';
import type { MarketData } from '$lib/types/market';

export const GET: RequestHandler = async () => {
    try {
        // Create data directory if it doesn't exist
        const dataDir = join(process.cwd(), 'backend', 'data');
        await mkdir(dataDir, { recursive: true });

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
        return json({ error: 'Failed to read market data' }, { status: 500 });
    }
};