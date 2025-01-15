<script lang="ts">
  import * as echarts from 'echarts';
  import { onMount, onDestroy } from 'svelte';
  import { Button } from "$lib/components/ui/button";

  export let straddleData: { timestamp: string; open: number; high: number; low: number; close: number; }[] = [];
  export let ceData: { timestamp: string; open: number; high: number; low: number; close: number; }[] = [];
  export let peData: { timestamp: string; open: number; high: number; low: number; close: number; }[] = [];

  let chart: echarts.ECharts | null = null;
  let chartContainer: HTMLDivElement;
  let showCE = true;
  let showPE = true;

  onMount(() => {
    chart = echarts.init(chartContainer);
    updateChart();
  });

  $: if (chart) {
    updateChart();
  }

  onDestroy(() => {
    if (chart) {
      chart.dispose();
    }
  });

  function updateChart() {
    if (chart) {
      chart.setOption({
        xAxis: {
          type: 'time',
        },
        yAxis: {
          type: 'value',
        },
        series: [
          {
            name: 'Straddle',
            data: straddleData.map(item => [item.timestamp, item.open, item.close, item.low, item.high]),
            type: 'candlestick'
          },
          {
            name: 'CE',
            data: ceData.map(item => [item.timestamp, item.open, item.close, item.low, item.high]),
            type: 'line',
            showSymbol: false,
            lineStyle: {
              width: 1
            }
          },
          {
            name: 'PE',
            data: peData.map(item => [item.timestamp, item.open, item.close, item.low, item.high]),
            type: 'line',
            showSymbol: false,
            lineStyle: {
              width: 1
            }
          }
        ].map(series => ({ ...series, silent: (series.name === 'CE' && !showCE) || (series.name === 'PE' && !showPE) }))
      });
    }
  }

  function toggleCE() {
    showCE = !showCE;
  }

  function togglePE() {
    showPE = !showPE;
  }
</script>

<div bind:this={chartContainer} style="width: 800px; height: 400px;"></div>

<div id="controls" class="flex gap-2 mt-4">
  <Button variant="outline" on:click={toggleCE}>Toggle CE</Button>
  <Button variant="outline" on:click={togglePE}>Toggle PE</Button>
</div>