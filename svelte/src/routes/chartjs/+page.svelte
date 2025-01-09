<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { Button } from "$lib/components/ui/button";
    import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "$lib/components/ui/select";
    import type { ChartConfiguration } from 'chart.js';
    
    interface StraddleData {
        timestamp: string;
        straddle_price: number;
    }

    let chart: any;
    let selectedSymbol = 'NIFTY';
    let chartEl: HTMLCanvasElement;
    let loading = false;
    let showMA = false;
    let maPeriod = 20;
    let intervalId: number;
    let windowSize = 100;
    let lastX = Date.now();

    // Generate initial sample data
    const sampleData: StraddleData[] = Array.from({ length: 50 }, (_, i) => ({
        timestamp: new Date(Date.now() - i * 3600000).toISOString(),
        straddle_price: Number((Math.random() * 100 + 200).toFixed(2))
    }));

    let chartData = [...sampleData];

    function calculateMA(data: number[], period: number): number[] {
        return data.map((_, index) => {
            if (index < period - 1) return NaN;
            const slice = data.slice(index - period + 1, index + 1);
            const sum = slice.reduce((acc, curr) => acc + curr, 0);
            return Number((sum / period).toFixed(2));
        });
    }

    const chartConfig: ChartConfiguration = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Straddle Price',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.3,
                pointRadius: 0.5
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 350
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    ticks: {
                        maxTicksLimit: 6
                    }
                },
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: (value) => Number(value).toFixed(2)
                    }
                }
            },
            plugins: {
                zoom: {
                    zoom: {
                        wheel: { enabled: true },
                        pinch: { enabled: true },
                        mode: 'x'
                    },
                    pan: {
                        enabled: true,
                        mode: 'x'
                    }
                },
                legend: {
                    position: 'top'
                }
            }
        }
    };

    function updateChart() {
        if (!chart) return;

        const timestamps = chartData.map(item => new Date(item.timestamp));
        const prices = chartData.map(item => item.straddle_price);
        
        chart.data.labels = timestamps;
        chart.data.datasets = [{
            label: `${selectedSymbol} Straddle`,
            data: prices,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.3,
            pointRadius: 0.5
        }];

        if (showMA) {
            const maData = calculateMA(prices, maPeriod);
            chart.data.datasets.push({
                label: `MA(${maPeriod})`,
                data: maData,
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.3,
                pointRadius: 0.5
            });
        }

        chart.update('none');
    }

    function simulateLiveData() {
        const newTimestamp = new Date().getTime();
        const newData: StraddleData = {
            timestamp: new Date(newTimestamp).toISOString(),
            straddle_price: Number((Math.random() * 100 + 200).toFixed(2))
        };
        
        chartData = [...chartData, newData];
        if (chartData.length > 500) {
            chartData = chartData.slice(-500);
        }
        lastX = newTimestamp;
        updateChart();
    }

    async function fetchData() {
        if (!browser) return;
        loading = true;
        console.log('Fetching data for symbol:', selectedSymbol);
        try {
            chartData = sampleData;
            updateChart();
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            loading = false;
        }
    }

    async function initializeChart() {
        if (!browser) return;

        try {
            const { Chart, TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } = await import('chart.js');
            const zoomPlugin = await import('chartjs-plugin-zoom');
            const adapter = await import('chartjs-adapter-date-fns');
            
            Chart.register(
                TimeScale, LinearScale, PointElement, LineElement,
                Title, Tooltip, Legend, zoomPlugin.default,
                adapter.default
            );

            if (chartEl && !chart) {
                chart = new Chart(chartEl, chartConfig);
                updateChart();
                intervalId = setInterval(simulateLiveData, 2000);
            }
        } catch (error) {
            console.error('Error initializing chart:', error);
        }
    }

    onMount(() => {
        initializeChart();

        return () => {
            if (intervalId) clearInterval(intervalId);
            if (chart) {
                chart.destroy();
                chart = null;
            }
        };
    });

    function handleSymbolChange(value: string | undefined) {
        if (!value) return;
        selectedSymbol = value;
        fetchData();
    }

    function toggleMA() {
        showMA = !showMA;
        updateChart();
    }

    function updateMAPeriod(event: Event) {
        const newPeriod = parseInt((event.target as HTMLInputElement).value);
        maPeriod = newPeriod;
        if (showMA) updateChart();
    }
</script>

<div class="flex flex-col gap-4 p-4">
    <div class="flex items-center gap-4">
        <Select selected={selectedSymbol} onSelectedChange={handleSymbolChange}>
            <SelectTrigger class="w-48">
                <SelectValue placeholder="Select Symbol" />
            </SelectTrigger>
            <SelectContent>
                {#each ['NIFTY', 'BANKNIFTY', 'FINNIFTY'] as symbol}
                    <SelectItem value={symbol}>{symbol}</SelectItem>
                {/each}
            </SelectContent>
        </Select>
        <Button on:click={fetchData} disabled={loading}>
            {loading ? 'Loading...' : 'Refresh Data'}
        </Button>
        <Button on:click={toggleMA}>
            {showMA ? 'Hide MA' : 'Show MA'}
        </Button>
        <div class="flex items-center gap-2">
            <label for="maPeriod">MA Period:</label>
            <input
                type="number"
                id="maPeriod"
                min="2"
                max="50"
                value={maPeriod}
                on:change={updateMAPeriod}
                class="w-20 px-2 py-1 border rounded"
            />
        </div>
    </div>
    
    <div class="border rounded-lg p-4 bg-white">
        <canvas bind:this={chartEl}></canvas>
    </div>
</div>