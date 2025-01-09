<script lang="ts">
  import "../app.pcss";  // This is correct since you're using PostCSS
  import Navigation from '$lib/components/Navigation.svelte';
</script>

<div class="min-h-screen bg-background">
  <Navigation />
  <main class="container mx-auto p-4">
    <slot />
  </main>
</div>

