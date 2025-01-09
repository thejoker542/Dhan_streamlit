<script lang="ts">
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { Button } from "$lib/components/ui/button";
    import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "$lib/components/ui/select";
    
    interface StraddleData {
        timestamp: string;
        straddle_price: number;
    }

    let chart: any;
    let selectedSymbol = 'NIFTY';
    let chartEl: HTMLElement;
    let loading = false;
    let showMA = false;
    let maPeriod = 20;
    let intervalId: number;
    let windowSize = 100; // Number of points to show in view
    let lastX = Date.now(); // Track the latest timestamp

    // Generate initial sample data
    const sampleData: StraddleData[] = Array.from({ length: 50 }, (_, i) => ({
        timestamp: new Date(Date.now() - i * 3600000).toISOString(),
        straddle_price: Number((Math.random() * 100 + 200).toFixed(2))
    }));

    let chartData = [...sampleData];

    function calculateMA(data: {x: number, y: number}[], period: number) {
        console.log('Calculating MA with period:', period, 'Data length:', data.length);
        const result = data.map((point, index) => {
            if (index < period - 1) return null;
            const slice = data.slice(index - period + 1, index + 1);
            const sum = slice.reduce((acc, curr) => acc + curr.y, 0);
            return {
                x: point.x,
                y: Number((sum / period).toFixed(2))
            };
        });
        console.log('MA calculation result:', result);
        return result;
    }

    const options: any = {
        series: [{
            name: 'Straddle Price',
            data: []
        }],
        chart: {
            type: 'line',
            height: 500,
            animations: {
                enabled: true,
                dynamicAnimation: {
                    speed: 350
                }
            },
            zoom: {
                enabled: true,
                type: 'x'
            },
            toolbar: {
                show: true
            }
        },
        stroke: {
            curve: 'smooth',
            width: 2
        },
        xaxis: {
            type: 'datetime',
            labels: {
                datetimeUTC: false
            },
            tickAmount: 6
        },
        yaxis: {
            labels: {
                formatter: (value: number) => value.toFixed(2)
            },
            tickAmount: 5
        }
    };

    function simulateLiveData() {
        const newTimestamp = new Date().getTime();
        const newData: StraddleData = {
            timestamp: new Date(newTimestamp).toISOString(),
            straddle_price: Number((Math.random() * 100 + 200).toFixed(2))
        };
        console.log('New data point:', newData);
        
        chartData = [...chartData, newData];
        if (chartData.length > 500) {
            console.log('Trimming data points, current length:', chartData.length);
            chartData = chartData.slice(-500);
        }
        lastX = newTimestamp;
        updateChart();
    }

    function updateChart() {
        if (!chart) {
            console.warn('Chart not initialized yet');
            return;
        }
        
        console.log('Updating chart with data length:', chartData.length);
        const processedData = chartData
            .map(item => ({
                x: new Date(item.timestamp).getTime(),
                y: item.straddle_price
            }))
            .sort((a, b) => a.x - b.x);

        console.log('Processed data:', processedData);

        const series: { name: string; data: { x: number; y: number; }[]; type?: string }[] = [{
            name: `${selectedSymbol} Straddle`,
            data: processedData
        }];

        if (showMA) {
            console.log('Adding MA series with period:', maPeriod);
            const maData = calculateMA(processedData, maPeriod);
            const filteredMA = maData.filter((point): point is {x: number, y: number} => point !== null);
            console.log('Filtered MA data points:', filteredMA.length);
            series.push({
                name: `MA(${maPeriod})`,
                type: 'line',
                data: filteredMA
            });
        }

        console.log('Updating series:', series);
        chart.updateSeries(series);
    }

    function toggleMA() {
        showMA = !showMA;
        console.log('Toggle MA:', showMA);
        updateChart();
    }

    async function fetchData() {
        if (!browser) return;
        loading = true;
        console.log('Fetching data for symbol:', selectedSymbol);
        try {
            chartData = sampleData;
            console.log('Received data points:', chartData.length);
            updateChart();
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        let mounted = false;

        const initializeChart = async () => {
            if (!browser || mounted) return;
            mounted = true;

            try {
                const ApexCharts = (await import('apexcharts')).default;
                
                const initialData = sampleData
                    .map(item => ({
                        x: new Date(item.timestamp).getTime(),
                        y: item.straddle_price
                    }))
                    .sort((a, b) => a.x - b.x);

                options.series[0].data = initialData;
                
                if (chartEl && !chart) {
                    chart = new ApexCharts(chartEl, options);
                    await chart.render();
                    intervalId = setInterval(simulateLiveData, 2000);
                }
            } catch (error) {
                console.error('Error initializing chart:', error);
            }
        };

        initializeChart();

        return () => {
            if (intervalId) clearInterval(intervalId);
            if (chart) {
                chart.destroy();
                chart = null;
            }
        };
    });

    type Selected<T> = T;
    function handleSymbolChange(event: string) {
        if (!event) return;
        console.log('Symbol changed to:', event);
        selectedSymbol = event;
        fetchData();
    }

    function updateMAPeriod(event: Event) {
        const newPeriod = parseInt((event.target as HTMLInputElement).value);
        maPeriod = newPeriod;
        updateChart();
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
        <div bind:this={chartEl}></div>
    </div>
</div>