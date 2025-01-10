<script lang="ts">
    import * as Select from "$lib/components/ui/select";
    import { Button } from "$lib/components/ui/button";
    import { marketStore } from '$lib/stores/marketStore';
    import { onMount } from 'svelte';

    let selectedIndex: string | null = 'NIFTY'; // Default to NIFTY
    let selectedExpiry: string | null = null;
    let selectedStrike: string | null = null;

    // Use derived store values
    $: indices = $marketStore.indices;
    $: expiryOptions = selectedIndex ? 
        $marketStore.expiryDates(selectedIndex).map(date => ({
            value: date,
            label: formatDate(date)
        })) : [];
    
    $: strikeOptions = selectedIndex && selectedExpiry ?
        $marketStore.strikes(selectedIndex, selectedExpiry).map(strike => ({
            value: strike.toString(),
            label: strike.toString()
        })) : [];

    function formatDate(dateStr: string) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', { 
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
    }

    function handleSelect(value: string | null, selectType: 'index'|'expiry'|'strike') {
        if (selectType === 'index') {
            selectedIndex = value;
            // Reset dependent selections
            selectedExpiry = null;
            selectedStrike = null;
            // Fetch new expiry dates
            if (value) {
                $marketStore.fetchExpiryDates(value);
            }
        }
        if (selectType === 'expiry') {
            selectedExpiry = value;
            selectedStrike = null;
            // Fetch new strike prices
            if (value && selectedIndex) {
                $marketStore.fetchStrikes(selectedIndex, value);
            }
        }
        if (selectType === 'strike') {
            selectedStrike = value;
        }
    }

    function handleChartClick() {
        if (selectedIndex && selectedExpiry && selectedStrike) {
            console.log('Generating chart for:', { selectedIndex, selectedExpiry, selectedStrike });
            // Add your chart generation logic here
        }
    }

    onMount(async () => {
        // Fetch initial data
        await $marketStore.fetchIndices();
        await $marketStore.fetchExpiryDates(selectedIndex);
        if (selectedIndex) {
            const expiryDates = $marketStore.expiryDates(selectedIndex);
            if (expiryDates.length > 0) {
                selectedExpiry = expiryDates[0]; // Default to the nearest expiry date
                await $marketStore.fetchStrikes(selectedIndex, selectedExpiry);
                const strikes = $marketStore.strikes(selectedIndex, selectedExpiry);
                if (strikes.length > 0) {
                    // Default to the strike price closest to the quote price
                    const quote = $marketStore.quotes[selectedIndex];
                    if (quote) {
                        const closestStrike = strikes.reduce((prev, curr) => {
                            return (Math.abs(curr - quote.last) < Math.abs(prev - quote.last) ? curr : prev);
                        });
                        selectedStrike = closestStrike.toString();
                    }
                }
            }
        }
        // Automatically click the chart button to generate the initial chart
        handleChartClick();
    });
</script>
  
<header class="bg-gray-100 p-4 flex items-center space-x-4 shadow-md">
    {#if $marketStore.isLoading}
        <div class="text-sm text-gray-500">Loading market data...</div>
    {/if}

    <Select.Root value={selectedIndex} onValueChange={(e)=>handleSelect(e.detail.value,'index')}>
        <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200">
            <Select.Value placeholder="Select Index" />
        </Select.Trigger>
        <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
            {#each indices as index}
                <Select.Item value={index}>{index}</Select.Item>
            {/each}
        </Select.Content>
    </Select.Root>
  
    <Select.Root value={selectedExpiry} onValueChange={(e)=>handleSelect(e.detail.value,'expiry')}>
        <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200" disabled={!selectedIndex}>
            <Select.Value placeholder="Select Expiry" />
        </Select.Trigger>
        <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
            {#each expiryOptions as option}
                <Select.Item value={option.value}>{option.label}</Select.Item>
            {/each}
        </Select.Content>
    </Select.Root>
  
    <Select.Root value={selectedStrike} onValueChange={(e)=>handleSelect(e.detail.value,'strike')}>
        <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200" disabled={!selectedExpiry}>
            <Select.Value placeholder="Select Strike" />
        </Select.Trigger>
        <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
            {#each strikeOptions as option}
                <Select.Item value={option.value}>{option.label}</Select.Item>
            {/each}
        </Select.Content>
    </Select.Root>

    <Button 
        disabled={!selectedIndex || !selectedExpiry || !selectedStrike}
        on:click={handleChartClick}
        variant="default"
    >
        Chart
    </Button>

    {#if selectedIndex && $marketStore.quotes[selectedIndex]}
        <div class="ml-auto text-sm">
            <span class="font-semibold">{selectedIndex}:</span>
            <span class={$marketStore.quotes[selectedIndex].change >= 0 ? 'text-green-600' : 'text-red-600'}>
                {$marketStore.quotes[selectedIndex].last} ({$marketStore.quotes[selectedIndex].change}%)
            </span>
        </div>
    {/if}
</header>
