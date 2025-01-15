<script lang="ts">
  import * as echarts from 'echarts';
  import { onMount, onDestroy } from 'svelte';
  import { Button } from "$lib/components/ui/button";

  type OHLCData = {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
  };

  const props = $props<{
    straddleData: OHLCData[];
    ceData: OHLCData[];
    peData: OHLCData[];
  }>();

  let chart: echarts.ECharts | null = null;
  let chartContainer: HTMLDivElement;
  let showCE = $state(true);
  let showPE = $state(true);

  onMount(() => {
    chart = echarts.init(chartContainer);
    updateChart();

    const resizeObserver = new ResizeObserver(() => {
      chart?.resize();
    });
    resizeObserver.observe(chartContainer);

    return () => {
      resizeObserver.disconnect();
    };
  });

  $effect.root(() => {
    if (chart) {
      updateChart();
    }
  });

  onDestroy(() => {
    if (chart) {
      chart.dispose();
    }
  });

  function updateChart() {
    if (!chart) return;

    const option = {
      animation: false,
      legend: {
        data: ['Straddle', 'CE', 'PE'],
        selected: {
          'CE': showCE,
          'PE': showPE
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%'
      },
      xAxis: {
        type: 'time',
        axisLine: { lineStyle: { color: '#e0e7ff' } },
        splitLine: { lineStyle: { color: '#f5f7ff' } }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#e0e7ff' } },
        splitLine: { lineStyle: { color: '#f5f7ff' } }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          show: true,
          type: 'slider',
          bottom: '5%',
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: 'Straddle',
          type: 'candlestick',
          data: props.straddleData.map( (item: OHLCData) => [
            item.timestamp,
            item.open,
            item.close,
            item.low,
            item.high
          ]),
          itemStyle: {
            color: '#ef4444',
            color0: '#22c55e',
            borderColor: '#ef4444',
            borderColor0: '#22c55e'
          }
        },
        {
          name: 'CE',
          type: 'line',
          data: props.ceData.map((item: OHLCData) => [item.timestamp, item.close]),
          showSymbol: false,
          lineStyle: {
            width: 1,
            color: '#2563eb'
          },
          emphasis: {
            lineStyle: {
              width: 2
            }
          }
        },
        {
          name: 'PE',
          type: 'line',
          data: props.peData.map((item: OHLCData) => [item.timestamp, item.close]),
          showSymbol: false,
          lineStyle: {
            width: 1,
            color: '#7c3aed'
          },
          emphasis: {
            lineStyle: {
              width: 2
            }
          }
        }
      ]
    };

    chart.setOption(option);
  }

  function toggleCE() {
    showCE = !showCE;
    updateChart();
  }

  function togglePE() {
    showPE = !showPE;
    updateChart();
  }
</script>

<div class="chart-container">
  <div bind:this={chartContainer} style="width: 100%; height: 600px;"></div>

  <div class="flex gap-2 mt-4">
    <Button 
      variant="outline" 
      on:click={toggleCE}
      class={`border-primary text-primary hover:bg-accent font-inter ${showCE ? 'bg-accent' : ''}`}
    >
      Toggle CE
    </Button>
    <Button 
      variant="outline" 
      on:click={togglePE}
      class={`border-primary text-primary hover:bg-accent font-inter ${showPE ? 'bg-accent' : ''}`}
    >
      Toggle PE
    </Button>
  </div>
</div>