<script lang="ts">
    import * as Select from "$lib/components/ui/select";
  </script>
  
  <header>
    <!-- First Select: INDEX -->
    <Select.Root>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select INDEX" />
      </Select.Trigger>
      <Select.Content>
        <Select.Item value="NIFTY">NIFTY</Select.Item>
        <Select.Item value="BANKNIFTY">BANKNIFTY</Select.Item>
        <Select.Item value="SENSEX">SENSEX</Select.Item>
        <Select.Item value="BANKEX">BANKEX</Select.Item>
        <Select.Item value="MIDCAPNIFTY">MIDCAPNIFTY</Select.Item>
      </Select.Content>
    </Select.Root>
  
    <!-- Second Select: Add your options here -->
    <Select.Root>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select Option 2" />
      </Select.Trigger>
      <Select.Content>
        <Select.Item value="option1">Option 1</Select.Item>
        <Select.Item value="option2">Option 2</Select.Item>
        <!-- Add more options as needed -->
      </Select.Content>
    </Select.Root>
  
    <!-- Third Select: Add your options here -->
    <Select.Root>
      <Select.Trigger class="w-[180px]">
        <Select.Value placeholder="Select Option 3" />
      </Select.Trigger>
      <Select.Content>
        <Select.Item value="optionA">Option A</Select.Item>
        <Select.Item value="optionB">Option B</Select.Item>
        <!-- Add more options as needed -->
      </Select.Content>
    </Select.Root>
  </header>