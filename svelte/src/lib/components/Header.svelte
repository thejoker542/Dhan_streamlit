<script lang="ts">
    import * as Select from "$lib/components/ui/select";
    import { Button } from "$lib/components/ui/button";
    import { marketStore } from '../stores/marketStore';
    import { onMount } from 'svelte';
    import type { Selection } from '../types/market';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{ chartClick: Selection }>();
    
    // Subscribe to store values with null checks
    $: index = $marketStore?.selected?.index?.subscribe ? $marketStore.selected.index : '';
    $: expiry = $marketStore?.selected?.expiry?.subscribe ? $marketStore.selected.expiry : '';
    $: strike = $marketStore?.selected?.strike?.subscribe ? $marketStore.selected.strike : '';
    
    // Get available options with null checks
    $: indices = $marketStore?.indices?.subscribe ? $marketStore.indices : [];
    $: expiryDates = $marketStore?.expiryDates?.subscribe ? $marketStore.expiryDates : [];
    $: availableStrikes = index && expiry ? marketStore.strikes(index, expiry) : [];

    function handleSelect(value: string, type: keyof Selection) {
        if (!marketStore?.selected) return;
        
        switch(type) {
            case 'index':
                marketStore.selected.index.set(value);
                // Reset dependent fields
                marketStore.selected.expiry.set('');
                marketStore.selected.strike.set('');
                break;
            case 'expiry':
                marketStore.selected.expiry.set(value);
                marketStore.selected.strike.set('');
                break;
            case 'strike':
                marketStore.selected.strike.set(value);
                break;
        }
    }

    onMount(async () => {
        await marketStore.loadData();
    });
</script>

<header class="bg-gray-100 p-4 flex items-center space-x-4">
    <Select.Root value={$index} onValueChange={e => handleSelect(e, 'index')}>
        <Select.Trigger>
            <Select.Value placeholder="Select Index" />
        </Select.Trigger>
        <Select.Content>
            {#each $indices as idx}
                <Select.Item value={idx}>{idx}</Select.Item>
            {/each}
        </Select.Content>
    </Select.Root>

    <Select.Root 
        value={$expiry}
        onValueChange={e => handleSelect(e, 'expiry')}
        disabled={!$index}
    >
        <Select.Trigger>
            <Select.Value placeholder="Select Expiry" />
        </Select.Trigger>
        <Select.Content>
            {#each $expiryDates as date}
                <Select.Item value={date}>{date}</Select.Item>
            {/each}
        </Select.Content>
    </Select.Root>

    <Select.Root 
        value={$strike}
        onValueChange={e => handleSelect(e, 'strike')}
        disabled={!$expiry}
    >
        <Select.Trigger>
            <Select.Value placeholder="Select Strike" />
        </Select.Trigger>
        <Select.Content>
            {#each availableStrikes as s}
                <Select.Item value={s.toString()}>{s}</Select.Item>
            {/each}
        </Select.Content>
    </Select.Root>

    <Button 
        disabled={!$index || !$expiry || !$strike}
        on:click={() => dispatch('chartClick', { index: $index, expiry: $expiry, strike: $strike })}
    >
        Chart
    </Button>
</header>