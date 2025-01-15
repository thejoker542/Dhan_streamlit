<script lang="ts">
  import HeaderSelection from '../components/HeaderSelection.svelte';
  import StraddleChart from '../components/StraddleChart.svelte';
  import { onMount, onDestroy } from 'svelte';

  interface OHLCData {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
  }

  let ceData: OHLCData[] = [];
  let peData: OHLCData[] = [];
  let straddleData: OHLCData[] = [];

  let liveCeData: { [key: string]: { open: number | null, high: number | null, low: number | null, close: number | null, volume: number } } = {};
  let livePeData: { [key: string]: { open: number | null, high: number | null, low: number | null, close: number | null, volume: number } } = {};

  let selectedTimeframe = 5; // Default timeframe
  let rawCeData: { timestamp: string; ltp: number }[] = [];
  let rawPeData: { timestamp: string; ltp: number }[] = [];

  async function fetchHistoricalData(ceSymbol: string, peSymbol: string) {
    const days = 10;
    const baseUrl = 'http://localhost:8000'; // Assuming FastAPI is running on port 8000

    try {
      const ceResponse = await fetch(`${baseUrl}/history/${ceSymbol}/${days}`);
      const historicalCeData = await ceResponse.json() as OHLCData[];
      ceData = historicalCeData;

      const peResponse = await fetch(`${baseUrl}/history/${peSymbol}/${days}`);
      const historicalPeData = await peResponse.json() as OHLCData[];
      peData = historicalPeData;

      calculateStraddleData();
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
    } else {
      console.error('CE and PE data lengths do not match');
    }
  }

  function handleChartButtonClick(event: CustomEvent<{ exSymbol: string, expiryDate: string, strikePrice: number }>) {
    const { exSymbol, expiryDate, strikePrice } = event.detail;
    const formattedExpiryDate = expiryDate.split('-').join('').slice(2);
    const ceSymbol = `NSE:${exSymbol}${formattedExpiryDate}${strikePrice}CE`;
    const peSymbol = `NSE:${exSymbol}${formattedExpiryDate}${strikePrice}PE`;
    fetchHistoricalData(ceSymbol, peSymbol);
  }

  function updateLiveData(symbol: string, timestamp: string, ltp: number) {
    if (symbol.endsWith('CE')) {
      rawCeData = [...rawCeData, { timestamp, ltp }];
    } else if (symbol.endsWith('PE')) {
      rawPeData = [...rawPeData, { timestamp, ltp }];
    }
    resampleData();
  }

  function resampleData() {
    const interval = selectedTimeframe * 60 * 1000;

    const resampledCeData: OHLCData[] = [];
    const resampledPeData: OHLCData[] = [];

    if (rawCeData.length > 0) {
      let currentIntervalStart = Math.floor(new Date(rawCeData[0].timestamp).getTime() / interval) * interval;
      let currentBatch: { timestamp: string; ltp: number }[] = [];
      for (const item of rawCeData) {
        const itemTime = new Date(item.timestamp).getTime();
        if (itemTime >= currentIntervalStart && itemTime < currentIntervalStart + interval) {
          currentBatch.push(item);
        } else {
          if (currentBatch.length > 0) {
            resampledCeData.push(calculateOHLC(currentBatch, new Date(currentIntervalStart).toISOString()));
          }
          currentIntervalStart = Math.floor(itemTime / interval) * interval;
          currentBatch = [item];
        }
      }
      if (currentBatch.length > 0) {
        resampledCeData.push(calculateOHLC(currentBatch, new Date(currentIntervalStart).toISOString()));
      }
    }

    if (rawPeData.length > 0) {
      let currentIntervalStart = Math.floor(new Date(rawPeData[0].timestamp).getTime() / interval) * interval;
      let currentBatch: { timestamp: string; ltp: number }[] = [];
      for (const item of rawPeData) {
        const itemTime = new Date(item.timestamp).getTime();
        if (itemTime >= currentIntervalStart && itemTime < currentIntervalStart + interval) {
          currentBatch.push(item);
        } else {
          if (currentBatch.length > 0) {
            resampledPeData.push(calculateOHLC(currentBatch, new Date(currentIntervalStart).toISOString()));
          }
          currentIntervalStart = Math.floor(itemTime / interval) * interval;
          currentBatch = [item];
        }
      }
      if (currentBatch.length > 0) {
        resampledPeData.push(calculateOHLC(currentBatch, new Date(currentIntervalStart).toISOString()));
      }
    }

    ceData = resampledCeData;
    peData = resampledPeData;
    calculateStraddleData();
  }

  

  function calculateOHLC(data: { timestamp: string; ltp: number }[], intervalStart: string): OHLCData {
    const open = data[0].ltp;
    let high = data[0].ltp;
    let low = data[0].ltp;
    const close = data[data.length - 1].ltp;
    for (const item of data) {
      high = Math.max(high, item.ltp);
      low = Math.min(low, item.ltp);
    }
    return { timestamp: intervalStart, open, high, low, close };
  }

  function handleTimeframeChange(event: CustomEvent<{ timeframe: number }>) {
    selectedTimeframe = event.detail.timeframe;
    resampleData();
  }

  let websocket: WebSocket;

  onMount(() => {
    websocket = new WebSocket('ws://localhost:8000/market_data');

    websocket.onopen = () => {
      console.log('WebSocket connection opened');
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
  });

  onDestroy(() => {
    if (websocket) {
      websocket.close();
    }
  });
</script>

<main>
  <HeaderSelection on:chartButtonClick={handleChartButtonClick} on:timeframeChange={handleTimeframeChange} />
  <StraddleChart straddleData={straddleData} ceData={ceData} peData={peData} />
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
</style>
