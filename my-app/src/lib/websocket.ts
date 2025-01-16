import { io, Socket } from 'socket.io-client';

class WebSocketClient {
    private socket: Socket | null = null;
    private subscribers: Map<string, Set<(data: any) => void>> = new Map();

    constructor() {
        this.connect();
    }

    private connect() {
        this.socket = io('http://localhost:8000', {
            transports: ['websocket'],
            upgrade: false
        });

        this.socket.on('connect', () => {
            console.log('Connected to Socket.IO server');
        });

        this.socket.on('market_update', (data) => {
            if (data && data.symbol) {
                const callbacks = this.subscribers.get(data.symbol);
                if (callbacks) {
                    callbacks.forEach(callback => callback(data));
                }
            }
        });

        this.socket.on('error', (error) => {
            console.error('Socket.IO error:', error);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from Socket.IO server');
        });
    }

    async subscribe(symbols: string[], callback: (data: any) => void) {
        try {
            const response = await fetch('http://localhost:8000/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbols })
            });

            if (!response.ok) {
                throw new Error(`Failed to subscribe: ${response.statusText}`);
            }

            // Register callback for each symbol
            symbols.forEach(symbol => {
                if (!this.subscribers.has(symbol)) {
                    this.subscribers.set(symbol, new Set());
                }
                this.subscribers.get(symbol)?.add(callback);
            });

            const result = await response.json();
            console.log('Subscription successful:', result);
        } catch (error) {
            console.error('Error subscribing to market data:', error);
            throw error;
        }
    }

    async unsubscribe(symbols: string[], callback: (data: any) => void) {
        try {
            const response = await fetch('http://localhost:8000/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbols })
            });

            if (!response.ok) {
                throw new Error(`Failed to unsubscribe: ${response.statusText}`);
            }

            // Remove callback for each symbol
            symbols.forEach(symbol => {
                this.subscribers.get(symbol)?.delete(callback);
                if (this.subscribers.get(symbol)?.size === 0) {
                    this.subscribers.delete(symbol);
                }
            });

            const result = await response.json();
            console.log('Unsubscription successful:', result);
        } catch (error) {
            console.error('Error unsubscribing from market data:', error);
            throw error;
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.subscribers.clear();
    }
}

// Create a singleton instance
export const wsClient = new WebSocketClient(); 