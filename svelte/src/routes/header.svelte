<script lang="ts">
    import { onMount } from 'svelte';
    import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "$lib/components/ui/select";
    import { Button } from "$lib/components/ui/button";
    import { createEventDispatcher } from 'svelte';
    
    const dispatch = createEventDispatcher();
    const indices = ['NIFTY', 'BANKNIFTY', 'MIDCAPNIFTY', 'SENSEX', 'BANKEX'];

    // State management
    let masterData = $state([]);
    let lastQuotes = $state({
        NIFTY: 19500,
        BANKNIFTY: 44000,
        MIDCAPNIFTY: 8000,
        SENSEX: 65000,
        BANKEX: 44500
    });
    
    let selectedIndex = $state('NIFTY');
    let selectedExpiry = $state('');
    let selectedStrike = $state(0);

    // Computed values
    let expiryDates = $derived(() => {
        if (!masterData.length) return [];
        return [...new Set(
            masterData
                .filter(row => row.exSymbol === selectedIndex)
                .map(row => row.expiryDate)
        )].sort((a, b) => new Date(b) - new Date(a));
    });

    let availableStrikes = $derived(() => {
        if (!masterData.length || !selectedExpiry) return [];
        return [...new Set(
            masterData
                .filter(row => 
                    row.exSymbol === selectedIndex && 
                    row.expiryDate === selectedExpiry
                )
                .map(row => Number(row.strikePrice))
        )].sort((a, b) => a - b);
    });

    let visibleStrikes = $derived(() => {
        if (!availableStrikes.length) return [];
        const currentPrice = lastQuotes[selectedIndex];
        const closestStrike = findClosestStrike(currentPrice);
        const strikeIndex = availableStrikes.indexOf(closestStrike);
        
        // Get 5 strikes below and 5 above
        const start = Math.max(0, strikeIndex - 5);
        const end = Math.min(availableStrikes.length, strikeIndex + 6);
        return availableStrikes.slice(start, end);
    });

    function findClosestStrike(price: number) {
        return availableStrikes.reduce((prev, curr) => 
            Math.abs(curr - price) < Math.abs(prev - price) ? curr : prev
        );
    }

    async function fetchLatestQuotes() {
        try {
            const response = await fetch('/api/quotes');
            const quotes = await response.json();
            lastQuotes = quotes;
        } catch (error) {
            console.error('Error fetching quotes:', error);
            // Keep using last saved quotes
        }
    }

    onMount(async () => {
        try {
            // Load master file data
            const response = await fetch('/backend/data/master_file.csv');
            const text = await response.text();
            masterData = text.split('\n').slice(1).map(row => {
                const [symbol, exSymbol, segment, exchange, expiryDate, strikePrice, exSymName] = row.split(',');
                return { symbol, exSymbol, segment, exchange, expiryDate, strikePrice: Number(strikePrice), exSymName };
            });

            // Fetch latest quotes
            await fetchLatestQuotes();

            // Set defaults
            selectedExpiry = expiryDates[0]; // Latest expiry
            selectedStrike = findClosestStrike(lastQuotes[selectedIndex]); // Closest strike to current price

            // Trigger initial chart
            handleChartClick();
        } catch (error) {
            console.error('Error in initialization:', error);
        }
    });

    function handleChartClick() {
        dispatch('chartClick', {
            index: selectedIndex,
            expiry: selectedExpiry,
            strike: selectedStrike
        });
    }
</script>

<div class="flex items-center gap-4 p-4 bg-background border-b">
    <Select value={selectedIndex} onValueChange={(value) => selectedIndex = value}>
        <SelectTrigger class="w-[180px]">
            <SelectValue placeholder="Select Index" />
        </SelectTrigger>
        <SelectContent>
            {#each indices as index}
                <SelectItem value={index}>{index}</SelectItem>
            {/each}
        </SelectContent>
    </Select>

    <Select value={selectedExpiry} onValueChange={(value) => selectedExpiry = value}>
        <SelectTrigger class="w-[180px]">
            <SelectValue placeholder="Select Expiry" />
        </SelectTrigger>
        <SelectContent>
            {#each expiryDates as date}
                <SelectItem value={date}>{date}</SelectItem>
            {/each}
        </SelectContent>
    </Select>

    <Select value={selectedStrike} onValueChange={(value) => selectedStrike = value}>
        <SelectTrigger class="w-[180px]">
            <SelectValue placeholder="Select Strike" />
        </SelectTrigger>
        <SelectContent>
            {#each visibleStrikes as strike}
                <SelectItem value={strike}>{strike}</SelectItem>
            {/each}
        </SelectContent>
    </Select>

    <Button on:click={handleChartClick}>Show Chart</Button>
</div>