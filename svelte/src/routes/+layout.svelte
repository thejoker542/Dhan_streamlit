<script lang="ts">
  import "../app.pcss";
  import { onMount } from 'svelte';
  import { marketStore } from '$lib/stores/marketStore';

  onMount(() => {
    marketStore.loadData();
    
    // Check for updates every 5 minutes
    const interval = setInterval(() => marketStore.loadData(), 5 * 60 * 1000);
    return () => clearInterval(interval);
  });
</script>

<div class="min-h-screen bg-background">
  <slot />
</div>

