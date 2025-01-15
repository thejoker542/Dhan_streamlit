<script lang="ts">
  import HeaderSelection from '../components/HeaderSelection.svelte';
  import StraddleChart from '../components/StraddleChart.svelte';
  import { onMount, onDestroy } from 'svelte';

  type OHLCData = {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
  };

  type TickData = {
    timestamp: string;
    ltp: number;
  };

  let ceData = $state<OHLCData[]>([]);
  let peData = $state<OHLCData[]>([]);
  let straddleData = $state<OHLCData[]>([]);

  let rawCeData = $state<TickData[]>([]);
  let rawPeData = $state<TickData[]>([]);
  let selectedTimeframe = $state<number>(5);

  let websocket: WebSocket | null = null;
  let ceSymbol = $state<string>('');
  let peSymbol = $state<string>('');

  async function fetchHistoricalData(ceSymbol: string, peSymbol: string) {
    try {
      const [ceResponse, peResponse] = await Promise.all([
        fetch(`http://localhost:8000/history/${ceSymbol}`),
        fetch(`http://localhost:8000/history/${peSymbol}`)
      ]);

      const historicalCeData = await ceResponse.json();
      const historicalPeData = await peResponse.json();

      ceData = historicalCeData;
      peData = historicalPeData;

      calculateStraddleData();
      
      // Clear raw data when loading new symbols
      rawCeData = [];
      rawPeData = [];
      
      // Update WebSocket subscription
      if (websocket?.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          action: 'subscribe',
          symbols: [ceSymbol, peSymbol]
        }));
      }
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  }

  function calculateStraddleData() {
    if (ceData.length === peData.length) {
      straddleData = ceData.map((ce, index) => ({
        timestamp: ce.timestamp,
        open: ce.open + peData[index].open,
        high: ce.high + peData[index].high,
        low: ce.low + peData[index].low,
        close: ce.close + peData[index].close,
      }));
    }
  }

  function handleChartButtonClick(event: CustomEvent<{ exSymbol: string, expiryDate: string, strikePrice: number }>) {
    const { exSymbol, expiryDate, strikePrice } = event.detail;
    const formattedExpiryDate = expiryDate.split('-').join('').slice(2);
    ceSymbol = `NSE:${exSymbol}${formattedExpiryDate}${strikePrice}CE`;
    peSymbol = `NSE:${exSymbol}${formattedExpiryDate}${strikePrice}PE`;
    fetchHistoricalData(ceSymbol, peSymbol);
  }

  function updateLiveData(symbol: string, timestamp: string, ltp: number) {
    if (symbol === ceSymbol) {
      rawCeData = [...rawCeData, { timestamp, ltp }];
    } else if (symbol === peSymbol) {
      rawPeData = [...rawPeData, { timestamp, ltp }];
    }
    resampleData();
  }

  function resampleData() {
    const interval = selectedTimeframe * 60 * 1000; // Convert minutes to milliseconds

    function resampleSymbolData(rawData: TickData[]): OHLCData[] {
      if (rawData.length === 0) return [];

      const resampled: OHLCData[] = [];
      let currentIntervalStart = Math.floor(new Date(rawData[0].timestamp).getTime() / interval) * interval;
      let currentBatch: TickData[] = [];

      for (const tick of rawData) {
        const tickTime = new Date(tick.timestamp).getTime();
        if (tickTime >= currentIntervalStart && tickTime < currentIntervalStart + interval) {
          currentBatch.push(tick);
        } else {
          if (currentBatch.length > 0) {
            resampled.push(calculateOHLC(currentBatch, new Date(currentIntervalStart).toISOString()));
          }
          currentIntervalStart = Math.floor(tickTime / interval) * interval;
          currentBatch = [tick];
        }
      }

      if (currentBatch.length > 0) {
        resampled.push(calculateOHLC(currentBatch, new Date(currentIntervalStart).toISOString()));
      }

      return resampled;
    }

    const resampledCeData = resampleSymbolData(rawCeData);
    const resampledPeData = resampleSymbolData(rawPeData);

    if (resampledCeData.length > 0) {
      ceData = [...ceData, ...resampledCeData];
    }
    if (resampledPeData.length > 0) {
      peData = [...peData, ...resampledPeData];
    }

    calculateStraddleData();
  }

  function calculateOHLC(data: TickData[], intervalStart: string): OHLCData {
    const prices = data.map(d => d.ltp);
    return {
      timestamp: intervalStart,
      open: prices[0],
      high: Math.max(...prices),
      low: Math.min(...prices),
      close: prices[prices.length - 1]
    };
  }

  function handleTimeframeChange(event: CustomEvent<{ timeframe: number }>) {
    selectedTimeframe = event.detail.timeframe;
    resampleData();
  }

  function isMarketHours(): boolean {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const currentTime = hours * 100 + minutes;  // Convert to HHMM format
    
    // Check if it's a weekday (0 = Sunday, 6 = Saturday)
    const isWeekday = now.getDay() > 0 && now.getDay() < 6;
    
    // Check if time is between 9:00 AM (0900) and 4:00 PM (1600)
    const isDuringMarketHours = currentTime >= 900 && currentTime <= 1600;
    
    return isWeekday && isDuringMarketHours;
  }

  onMount(() => {
    if (isMarketHours()) {
      websocket = new WebSocket('ws://localhost:8000/market_data');

      websocket.onopen = () => {
        console.log('WebSocket connection opened during market hours');
        if (ceSymbol && peSymbol && websocket) {
          websocket.send(JSON.stringify({
            action: 'subscribe',
            symbols: [ceSymbol, peSymbol]
          }));
        }
      };

      websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message && message.timestamp && message.symbol && message.ltp) {
          updateLiveData(message.symbol, message.timestamp, message.ltp);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      websocket.onclose = () => {
        console.log('WebSocket connection closed');
      };
    } else {
      console.log('Outside market hours - WebSocket connection not initialized');
    }
  });

  onDestroy(() => {
    if (websocket?.readyState === WebSocket.OPEN) {
      websocket.close();
    }
  });
</script>

<main class="container mx-auto px-4 py-8">
  <HeaderSelection 
    on:chartButtonClick={handleChartButtonClick} 
    on:timeframeChange={handleTimeframeChange} 
  />
  <div class="mt-8">
    <StraddleChart 
      straddleData={straddleData} 
      ceData={ceData} 
      peData={peData} 
    />
  </div>
</main>

<style>
  :global(html) {
    background-color: #f9fafb;
  }
</style>
