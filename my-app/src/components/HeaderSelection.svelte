<script lang="ts">
  // Import statements
  import * as Select from "$lib/components/ui/select";
  import { Button } from "$lib/components/ui/button";
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';

  type ChartEvent = {
    exSymbol: string;
    expiryDate: string;
    strikePrice: number;
  };

  type TimeframeEvent = {
    timeframe: number;
  };

  const dispatch = createEventDispatcher<{
    chartButtonClick: ChartEvent;
    timeframeChange: TimeframeEvent;
  }>();

  // Define constant arrays
  const exSymbols = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'BANKEX'] as const;
  const timeframes = [1, 3, 5, 15, 30] as const;

  type ExSymbol = typeof exSymbols[number];
  type Timeframe = typeof timeframes[number];

  // Set default values for state variables
  let selectedExSymbol = $state<ExSymbol>('NIFTY');
  let selectedExpiryDate = $state<string>('');
  let selectedStrikePrice = $state<number>(24000);
  let selectedTimeframe = $state<Timeframe>(5);

  // Additional state variables for data
  let expiryDates = $state<string[]>([]);
  let strikePrices = $state<number[]>([]);
  let defaultStrike = $state<number>(24000);

  async function fetchMasterData() {
    try {
      if (!selectedExSymbol) return;
      
      const response = await fetch(`http://localhost:8000/master-data/${selectedExSymbol}`);
      const data = await response.json();
      expiryDates = data.expiry_dates;
      strikePrices = data.strikePrices;
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
    dispatch('timeframeChange', {
      timeframe: selectedTimeframe
    });
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
    fetchMasterData();
  });
</script>

<div class="controls-container mt-4 mb-8">
  <div class="flex items-center justify-center space-x-4 flex-nowrap overflow-x-auto px-6 py-4">
    <Select.Root>
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedExSymbol}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each exSymbols as symbol}
          <Select.Item class="hover:bg-accent" on:click={() => selectedExSymbol = symbol}>
            {symbol}
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Select.Root>
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedExpiryDate || 'Select Expiry'}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each expiryDates as date}
          <Select.Item class="hover:bg-accent" on:click={() => selectedExpiryDate = date}>
            {date}
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Select.Root>
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedStrikePrice || 'Strike Price'}</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each getVisibleStrikePrices() as price}
          <Select.Item class="hover:bg-accent" on:click={() => selectedStrikePrice = price}>
            {price}
          </Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>

    <Select.Root>
      <Select.Trigger class="w-[140px] bg-card text-foreground border-border hover:bg-accent font-inter">
        <Select.Value>{selectedTimeframe} min</Select.Value>
      </Select.Trigger>
      <Select.Content class="bg-card text-foreground border-border font-inter">
        {#each timeframes as timeframe}
          <Select.Item class="hover:bg-accent" on:click={() => {
            selectedTimeframe = timeframe;
            handleTimeframeChange();
          }}>
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