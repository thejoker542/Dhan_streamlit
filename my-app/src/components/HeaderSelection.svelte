<script lang="ts">
  // Import statements
  import * as Select from "$lib/components/ui/select";  // Imports all exports from select component
  import { Button } from "$lib/components/ui/button";   // Imports Button component
  import { onMount } from 'svelte';                     // Lifecycle function that runs when component mounts
  import { createEventDispatcher } from 'svelte';       // Creates type-safe event dispatcher
  import type { Selected } from "$lib/components/ui/select"; // Add this import

  // Define TypeScript types for events
  type ChartEvent = {                                  // Type for chart click events
      exSymbol: string;                               // Exchange symbol (e.g., NIFTY)
      expiryDate: string;                             // Option expiry date
      strikePrice: number;                            // Strike price of option
  };

  type TimeframeEvent = {                             // Type for timeframe change events
      timeframe: number;                              // Timeframe in minutes
  };

  // Create type-safe event dispatcher
  const dispatch = createEventDispatcher<{             // Creates dispatcher with two event types
      chartButtonClick: ChartEvent;                   // Event for chart button clicks
      timeframeChange: TimeframeEvent;                // Event for timeframe changes
  }>();

  // Define constant arrays with literal types
  const exSymbols = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'BANKEX'] as const;  // Available exchange symbols
  const timeframes = [1, 3, 5, 15, 30] as const;                           // Available timeframes in minutes

  // Create type aliases from the constant arrays
  type ExSymbol = typeof exSymbols[number];           // Type for exchange symbols
  type Timeframe = typeof timeframes[number];         // Type for timeframes

  // Set default values for state variables
  let selectedExSymbol = $state<ExSymbol>('NIFTY');  // Changed to have default value
  let selectedExpiryDate = $state<string | undefined>(undefined);
  let selectedStrikePrice = $state<number | undefined>(undefined);
  let selectedTimeframe = $state<Timeframe>(5);  // Default to 5min timeframe

  // Additional state variables for data
  let expiryDates = $state<string[]>([]);            // Available expiry dates for selected symbol
  let strikePrices = $state<number[]>([]);           // Available strike prices
  let defaultStrike = $state<number>(24000);         // Default strike price value

  async function fetchMasterData() {
    try {
      if (!selectedExSymbol) return;
      
      const response = await fetch(`http://localhost:8000/master-data/${selectedExSymbol}`);
      const data = await response.json();
      expiryDates = data.expiry_dates;
      strikePrices = data.strike_prices;
      defaultStrike = data.default_strike;
      
      // Set defaults
      selectedExpiryDate = expiryDates[0]; // Latest date
      selectedStrikePrice = defaultStrike;
      
      // Initial chart load
      fetchData();
    } catch (error) {
      console.error('Error fetching master data:', error);
    }
  }

  async function fetchData() {
    if (!selectedExpiryDate || !selectedExSymbol || !selectedStrikePrice) return;

    dispatch('chartButtonClick', {
      exSymbol: selectedExSymbol,
      expiryDate: selectedExpiryDate,
      strikePrice: selectedStrikePrice,
    });
  }

  function handleTimeframeChange() {
    if (!selectedTimeframe) return;
    dispatch('timeframeChange', { timeframe: selectedTimeframe });
  }

  function getVisibleStrikePrices() {
    if (!selectedStrikePrice || !strikePrices.length) return [];
    const index = strikePrices.indexOf(selectedStrikePrice);
    const start = Math.max(0, index - 5);
    const end = Math.min(strikePrices.length, index + 6);
    return strikePrices.slice(start, end);
  }

  $effect.root(() => {
    if (selectedExSymbol) {
      fetchMasterData();
    }
  });

  onMount(() => {
    // No need to set selectedExSymbol here since it has default value
    // Just trigger the data fetch
    fetchMasterData();
  });
</script>

<div class="controls-container pt-3">
  <div class="flex items-center justify-center space-x-3 flex-nowrap overflow-x-auto px-4">
    <Select.Root 
      selected={selectedExSymbol} 
      onSelectedChange={(value) => selectedExSymbol = value}
    >
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedExSymbol ?? "Select ExSymbol"}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each exSymbols as symbol}
          <Select.Item value={symbol} class="hover:bg-accent">
            {symbol}
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Select.Root 
      selected={selectedExpiryDate as Selected<string>} 
      onSelectedChange={(value) => selectedExpiryDate = value}
    >
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedExpiryDate ?? "Select Expiry"}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each expiryDates as date}
          <Select.Item value={date} class="hover:bg-accent">
            {date}
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Select.Root 
      selected={selectedStrikePrice as Selected<number>} 
      onSelectedChange={(value) => selectedStrikePrice = value}
    >
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedStrikePrice ?? "Strike Price"}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each getVisibleStrikePrices() as price}
          <Select.Item value={price} class="hover:bg-accent">
            {price}
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Select.Root 
      selected={selectedTimeframe as Selected<number>} 
      onSelectedChange={(value) => { selectedTimeframe = value; handleTimeframeChange(); }}
    >
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedTimeframe ? `${selectedTimeframe} min` : "Timeframe"}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each timeframes as timeframe}
          <Select.Item value={timeframe} class="hover:bg-accent">
            {timeframe} min
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Button 
      variant="default" 
      on:click={fetchData}
      class="w-[100px] bg-primary hover:bg-primary/90 text-primary-foreground font-inter font-medium whitespace-nowrap"
    >
      Chart
    </Button>
  </div>
</div>