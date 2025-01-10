import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';
import { join } from 'path';
import type { MarketData } from '$lib/types/market';

export const GET: RequestHandler = async () => {
    try {
        const filePath = join(process.cwd(), '..', 'backend', 'data', 'master_file.csv');
        const fileContent = readFileSync(filePath, 'utf-8');
        
        // Parse CSV with headers matching your format
        const rawRecords = parse(fileContent, {
            columns: ['symbol', 'exSymbol', 'symbol2', 'exSymbol2', 'segment', 
                     'exchange', 'expiryDate', 'strikePrice', 'exSymName'],
            skip_empty_lines: true,
            trim: true
        });

        // Process records to create market data
        const marketDataMap = new Map<string, MarketData>();
        
        rawRecords.forEach((record: any) => {
            const key = `${record.exSymbol}-${record.expiryDate}-${record.strikePrice}`;
            
            if (!marketDataMap.has(key)) {
                marketDataMap.set(key, {
                    index: record.exSymbol,
                    expiry: record.expiryDate,
                    strike: parseFloat(record.strikePrice),
                    callPrice: 0,
                    putPrice: 0
                });
            }
        });

        // Convert map to array and sort
        const records = Array.from(marketDataMap.values())
            .sort((a, b) => {
                if (a.index !== b.index) return a.index.localeCompare(b.index);
                if (a.expiry !== b.expiry) return new Date(a.expiry).getTime() - new Date(b.expiry).getTime();
                return a.strike - b.strike;
            });

        return json(records);
    } catch (error) {
        console.error('Error reading market data:', error);
        return new Response('Failed to load market data', { 
            status: 500,
            statusText: error instanceof Error ? error.message : 'Unknown error'
        });
    }
};