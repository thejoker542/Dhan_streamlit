<script lang="ts">
    import * as Select from "$lib/components/ui/select";
    import { Button } from "$lib/components/ui/button";
  
    const indexOptions = [
        { value: "NIFTY", label: "NIFTY" },
        { value: "BANKNIFTY", label: "BANKNIFTY" },
        { value: "SENSEX", label: "SENSEX" },
        { value: "BANKEX", label: "BANKEX" },
        { value: "MIDCAPNIFTY", label: "MIDCAPNIFTY" },
    ];
    
    // Example expiry dates (you should fetch these dynamically based on selected index)
    const expiryOptions = [
        { value: "2024-01-25", label: "25 Jan 2024" },
        { value: "2024-02-01", label: "01 Feb 2024" },
        { value: "2024-02-08", label: "08 Feb 2024" },
    ];
    
    // Example strike prices (should be fetched based on selected index and expiry)
    const strikeOptions = [
        { value: "19500", label: "19500" },
        { value: "19600", label: "19600" },
        { value: "19700", label: "19700" },
    ];
    
    let selectedIndex: string | null = null;
    let selectedExpiry: string | null = null;
    let selectedStrike: string | null = null;

    function handleSelect(value: string | null, selectType: 'index'|'expiry'|'strike') {
        if (selectType === 'index') {
            selectedIndex = value;
            // Reset dependent selections
            selectedExpiry = null;
            selectedStrike = null;
            // Here you would typically fetch new expiry dates
        }
        if (selectType === 'expiry') {
            selectedExpiry = value;
            selectedStrike = null;
            // Here you would typically fetch new strike prices
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
</script>
  
<header class="bg-gray-100 p-4 flex items-center space-x-4 shadow-md">
    <Select.Root value={selectedIndex} onValueChange={(e)=>handleSelect(e.detail.value,'index')}>
        <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200">
            <Select.Value placeholder="Select Index" />
        </Select.Trigger>
        <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
            {#each indexOptions as option}
                <Select.Item value={option.value}>{option.label}</Select.Item>
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
</header>