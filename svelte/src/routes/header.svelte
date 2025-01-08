<script lang="ts">
    import * as Select from "$lib/components/ui/select";
  
    // Optional: You could store these options in a separate file or use constants
    const indexOptions = [
        { value: "NIFTY", label: "NIFTY" },
        { value: "BANKNIFTY", label: "BANKNIFTY" },
        { value: "SENSEX", label: "SENSEX" },
        { value: "BANKEX", label: "BANKEX" },
        { value: "MIDCAPNIFTY", label: "MIDCAPNIFTY" },
    ];
    
    const option2Options = [
        { value: "option1", label: "Option 1"},
        { value: "option2", label: "Option 2"},
    ]
    
    const option3Options = [
        { value: "optionA", label:"Option A"},
        { value: "optionB", label:"Option B"},
    ]
    
    let selectedIndex: string | null = null;
    let selectedOption2: string | null = null;
    let selectedOption3: string | null = null;

    function handleSelect(value: string | null, selectType: 'index'|'option2'|'option3'){
        if (selectType === 'index'){
            selectedIndex = value;
        }
        if (selectType === 'option2'){
            selectedOption2 = value;
        }
         if (selectType === 'option3'){
            selectedOption3 = value;
        }
        console.log(`Selected ${selectType}: `,value);
    }


  </script>
  
  <header class="bg-gray-100 p-4 flex space-x-4 shadow-md">
    <!-- First Select: INDEX -->
    <Select.Root onValueChange={(e)=>handleSelect(e.detail.value,'index')}>
      <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200">
        <Select.Value placeholder="Select INDEX" />
      </Select.Trigger>
      <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
        {#each indexOptions as option}
          <Select.Item value={option.value}>{option.label}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  
    <!-- Second Select: Add your options here -->
    <Select.Root onValueChange={(e)=>handleSelect(e.detail.value,'option2')}>
      <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200">
        <Select.Value placeholder="Select Option 2" />
      </Select.Trigger>
      <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
          {#each option2Options as option}
              <Select.Item value={option.value}>{option.label}</Select.Item>
          {/each}
      </Select.Content>
    </Select.Root>
  
    <!-- Third Select: Add your options here -->
    <Select.Root onValueChange={(e)=>handleSelect(e.detail.value,'option3')}>
      <Select.Trigger class="w-[180px] border border-gray-300 rounded p-2 bg-white hover:bg-gray-50 focus:outline-none focus:ring focus:ring-blue-200">
        <Select.Value placeholder="Select Option 3" />
      </Select.Trigger>
      <Select.Content class="bg-white border border-gray-300 rounded shadow-md">
        {#each option3Options as option}
            <Select.Item value={option.value}>{option.label}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </header>