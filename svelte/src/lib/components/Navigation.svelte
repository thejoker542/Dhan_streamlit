<script lang="ts">
    import { page } from '$app/stores';
    import { Button } from './ui/button';
    
    const navItems = [
        { href: '/', label: 'ApexCharts' },
        { href: '/chartjs', label: 'Chart.js' }
    ];
</script>

<nav class="border-b mb-4">
    <div class="container mx-auto px-4">
        <div class="flex space-x-4 py-4">
            {#each navItems as item}
                <Button 
                    variant={$page.url.pathname === item.href ? 'default' : 'outline'}
                    href={item.href}
                >
                    {item.label}
                </Button>
            {/each}
        </div>
    </div>
</nav>
