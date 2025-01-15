<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import * as Select from "$lib/components/ui/select";
  import { Button } from "$lib/components/ui/button";

  const dispatch = createEventDispatcher();

  const exSymbols = ['NIFTY', 'BANKNIFTY', 'MIDCAPNIFTY', 'SENSEX', 'BANKEX'];
  let selectedExSymbol = 'NIFTY';

  // Parse expiry dates from the sample data
  const sampleData = "NSE:NIFTY2510930000CE,NIFTY,11,10,2025-01-09 10:00:00,30000.0,NIFTY2510930000CE";
  const expiryDateValue = sampleData.split(',')[4].split(' ')[0];
  const expiryDates = [expiryDateValue];
  let selectedExpiryDate = expiryDates[0];

  const strikePrices = Array.from({ length: 11 }, (_, i) => 24000 + (i - 5) * 100);
  let selectedStrikePrice = 24000;

  const timeframes = [1, 3, 5, 15, 30];
  let selectedTimeframe = 5;

  async function fetchData() {
    const expiryDateParts = selectedExpiryDate.split('-');
    const formattedExpiryDate = `${expiryDateParts[0].slice(-2)}${expiryDateParts[1]}${expiryDateParts[2]}`;
    const ceSymbol = `NSE:${selectedExSymbol}${formattedExpiryDate}${selectedStrikePrice}CE`;
    const peSymbol = `NSE:${selectedExSymbol}${formattedExpiryDate}${selectedStrikePrice}PE`;

    dispatch('chartButtonClick', {
      exSymbol: selectedExSymbol,
      expiryDate: selectedExpiryDate,
      strikePrice: selectedStrikePrice,
    });
  }

  function handleTimeframeChange() {
    dispatch('timeframeChange', { timeframe: selectedTimeframe });
  }

  onMount(fetchData);
</script>

<div class="flex gap-4 items-center p-4">
  <div class="grid gap-2">
    <Select.Root value={selectedExSymbol} onValueChange={(value) => selectedExSymbol = value}>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select ExSymbol" />
      </Select.Trigger>
      <Select.Content>
        {#each exSymbols as symbol}
          <Select.Item value={symbol}>{symbol}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  <div class="grid gap-2">
    <Select.Root value={selectedExpiryDate} onValueChange={(value) => selectedExpiryDate = value}>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select Expiry Date" />
      </Select.Trigger>
      <Select.Content>
        {#each expiryDates as date}
          <Select.Item value={date}>{date}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  <div class="grid gap-2">
    <Select.Root value={selectedStrikePrice} onValueChange={(value) => selectedStrikePrice = value}>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select Strike Price" />
      </Select.Trigger>
      <Select.Content>
        {#each strikePrices as price}
          <Select.Item value={price}>{price}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  <div class="grid gap-2">
    <Select.Root value={selectedTimeframe} onValueChange={(value) => { selectedTimeframe = value; handleTimeframeChange(); }}>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select Timeframe" />
      </Select.Trigger>
      <Select.Content>
        {#each timeframes as timeframe}
          <Select.Item value={timeframe}>{timeframe} min</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  <Button variant="default" on:click={fetchData}>Chart</Button>
</div>