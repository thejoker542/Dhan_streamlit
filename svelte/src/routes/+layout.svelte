<script lang="ts">
    import { onMount } from 'svelte';
    import { marketStore } from '$lib/stores/marketStore';
    import "../../src/app.postcss";

    onMount(async () => {
        await marketStore.loadData();
        
        // Set up periodic quote updates (every 5 minutes)
        const interval = setInterval(() => {
            marketStore.updateQuotes();
        }, 5 * 60 * 1000);

        return () => clearInterval(interval);
    });
</script>

<slot />

