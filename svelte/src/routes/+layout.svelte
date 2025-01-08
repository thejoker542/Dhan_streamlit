<script lang="ts">
  import "../app.css";
  import Header from "./header.svelte";
</script>

<div class="min-h-screen bg-gray-50">
  <Header />
  <main class="container mx-auto p-4">
    <slot />
  </main>
</div>

