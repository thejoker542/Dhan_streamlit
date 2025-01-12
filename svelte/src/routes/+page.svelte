<script lang="ts">
    import { onMount } from 'svelte';
    import * as echarts from 'echarts';
    import Header from "$lib/components/Header.svelte";  // Changed to correct path
    import { Button } from "$lib/components/ui/button";
    
    let chartDiv: HTMLElement;
    let chart: echarts.ECharts;
    let tickInerval: number;
    
    // State management
    let indicators = $state({
        ma: { enabled: true, period: 20 },
        rsi: { enabled: false, period: 14 },
        bollinger: { enabled: false, period: 20, deviation: 2 }
    });
    
    let chartData = $state([]);

    // Sample data generator
    function generateSampleData() {
        const now = new Date();
        return Array.from({ length: 100 }, (_, i) => {
            const time = new Date(now.getTime() - (100 - i) * 60000);
            return [
                time.toISOString(),
                Math.random() * 100 + 100
            ];
        });
    }

    function calculateMA(data: any[], period: number) {
        return data.map((_, i) => {
            if (i < period - 1) return '-';
            const sum = data
                .slice(i - period + 1, i + 1)
                .reduce((acc, val) => acc + val[1], 0);
            return sum / period;
        });
    }

    function updateChart() {
        if (!chart || !chartData.length) return;
        
        const ma = indicators.ma.enabled ? calculateMA(chartData, indicators.ma.period) : [];
        
        const option = {
            tooltip: { trigger: 'axis' },
            legend: { data: ['Price', `MA${indicators.ma.period}`] },
            xAxis: { type: 'time', boundaryGap: false },
            yAxis: { type: 'value', scale: true },
            dataZoom: [
                { type: 'inside', start: 0, end: 100 },
                { type: 'slider', start: 0, end: 100 }
            ],
            series: [
                {
                    name: 'Price',
                    type: 'line',
                    data: chartData,
                    showSymbol: false, // Remove dots
                    smooth: false
                },
                ...(indicators.ma.enabled ? [{
                    name: `MA${indicators.ma.period}`,
                    type: 'line',
                    data: ma.map((val, idx) => [chartData[idx][0], val]),
                    lineStyle: { opacity: 0.5 },
                    showSymbol: false // Remove dots
                }] : [])
            ]
        };
        
        chart.setOption(option);
    }

    function startTickDataUpdate() {
        // Clear any existing interval
        clearInterval(tickInterval);
        
        // Update every second
        tickInterval = setInterval(() => {
            const lastPoint = chartData[chartData.length - 1];
            const newTime = new Date(new Date(lastPoint[0]).getTime() + 60000);
            const newPrice = lastPoint[1] * (1 + (Math.random() - 0.5) * 0.002);
            
            chartData = [...chartData.slice(1), [newTime.toISOString(), newPrice]];
        }, 1000);
    }

    // Replace $derived with $effect for side effects
    $effect(() => {
        updateChart();
    });

    function toggleIndicator(name: string) {
        indicators[name].enabled = !indicators[name].enabled;
        updateChart();
    }

    function updateIndicatorSettings(name: string, settings: any) {
        indicators[name] = { ...indicators[name], ...settings };
        updateChart();
    }

    onMount(() => {
        chart = echarts.init(chartDiv);
        chartData = generateSampleData();
        startTickDataUpdate();
        
        return () => {
            clearInterval(tickInterval);
            chart?.dispose();
        };
    });

    async function handleHeaderChartClick(event: CustomEvent<{index?: string; expiry?: string; strike?: string}>) {
        const { index = 'NIFTY' } = event.detail || {}; // Provide default value
        
        try {
            // Fetch historical data for the selected combination
            const response = await fetch(`/api/historical-data?index=${index}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Handle empty data case
            if (!data || !data.length) {
                console.warn('No data received');
                return;
            }
            
            // Update chart data
            chartData = data.map(row => [
                new Date(row.date).toISOString(),
                row.close
            ]);
            
            startTickDataUpdate();
        } catch (error) {
            console.error('Error loading historical data:', error);
        }
    }
</script>

<div class="min-h-screen bg-background">
    <Header on:chartClick={handleHeaderChartClick} />
    
    <div class="container mx-auto p-4">
        <div class="mb-4 flex items-center gap-2">
            <Button 
                variant={indicators.ma.enabled ? "default" : "outline"}
                on:click={() => toggleIndicator('ma')}
            >
                MA
            </Button>
            <Button 
                variant={indicators.rsi.enabled ? "default" : "outline"}
                on:click={() => toggleIndicator('rsi')}
            >
                RSI
            </Button>
            <Button 
                variant={indicators.bollinger.enabled ? "default" : "outline"}
                on:click={() => toggleIndicator('bollinger')}
            >
                Bollinger
            </Button>
        </div>
        
        <div bind:this={chartDiv} class="w-full h-[600px]"></div>
    </div>
</div>