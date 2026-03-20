const nInput = document.getElementById('n-input');
const sigmaInput = document.getElementById('sigma-input');
const countInput = document.getElementById('count-input');

const nVal = document.getElementById('n-val');
const sigmaVal = document.getElementById('sigma-val');
const countVal = document.getElementById('count-val');

const captureRateEl = document.getElementById('capture-rate');
const avgErrorEl = document.getElementById('avg-error');

const ctx = document.getElementById('ciChart').getContext('2d');

let chart;
const MEAN = 100;
const Z_CRITICAL = 1.96; // 95% confidence

function generateNormalSample(mean, sigma, n) {
    let sample = [];
    for (let i = 0; i < n; i++) {
        // Box-Muller transform
        let u1 = Math.random();
        let u2 = Math.random();
        let z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
        sample.push(z * sigma + mean);
    }
    return sample;
}

function runSimulation() {
    const n = parseInt(nInput.value);
    const sigma = parseFloat(sigmaInput.value);
    const count = parseInt(countInput.value);

    nVal.textContent = n;
    sigmaVal.textContent = sigma;
    countVal.textContent = count;

    const intervals = [];
    let captures = 0;
    const marginOfError = Z_CRITICAL * (sigma / Math.sqrt(n));
    avgErrorEl.textContent = marginOfError.toFixed(2);

    for (let i = 0; i < count; i++) {
        const sample = generateNormalSample(MEAN, sigma, n);
        const sampleMean = sample.reduce((a, b) => a + b) / n;
        const lower = sampleMean - marginOfError;
        const upper = sampleMean + marginOfError;
        const capturesMean = lower <= MEAN && upper >= MEAN;
        
        if (capturesMean) captures++;

        intervals.push({
            y: i,
            x: sampleMean,
            low: lower,
            high: upper,
            captures: capturesMean
        });
    }

    captureRateEl.textContent = `${Math.round((captures / count) * 100)}%`;
    captureRateEl.style.color = (captures / count) >= 0.93 ? 'var(--success)' : 'var(--danger)';

    updateChart(intervals);
}

function updateChart(data) {
    const datasets = [
        {
            label: 'Media de la Muestra',
            data: data.map(d => ({x: d.x, y: d.y})),
            pointBackgroundColor: data.map(d => d.captures ? '#818cf8' : '#ef4444'),
            borderColor: 'transparent',
            pointRadius: 4
        },
        {
            label: 'Intervalos de Confianza',
            data: data.map(d => ({x: d.low, y: d.y})), // Placeholder for bars
            showLine: false
        }
    ];

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500
            },
            scales: {
                y: {
                    display: false,
                    reverse: true
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' },
                    title: { display: true, text: 'Valor Estimado', color: '#94a3b8' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const d = data[ctx.dataIndex];
                            return `Media: ${d.x.toFixed(2)} [${d.low.toFixed(2)}, ${d.high.toFixed(2)}]`;
                        }
                    }
                },
                legend: { display: false }
            }
        },
        plugins: [{
            id: 'ciPainter',
            afterDatasetsDraw(chart) {
                const {ctx, scales: {x, y}} = chart;
                ctx.save();
                
                // Draw intervals
                data.forEach(d => {
                    ctx.beginPath();
                    ctx.strokeStyle = d.captures ? 'rgba(129, 140, 248, 0.5)' : 'rgba(239, 68, 68, 0.8)';
                    ctx.lineWidth = 2;
                    ctx.moveTo(x.getPixelForValue(d.low), y.getPixelForValue(d.y));
                    ctx.lineTo(x.getPixelForValue(d.high), y.getPixelForValue(d.y));
                    ctx.stroke();
                });

                // Draw population mean
                ctx.beginPath();
                ctx.setLineDash([5, 5]);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = 1.5;
                ctx.moveTo(x.getPixelForValue(MEAN), y.top);
                ctx.lineTo(x.getPixelForValue(MEAN), y.bottom);
                ctx.stroke();
                ctx.restore();
            }
        }]
    });
}

[nInput, sigmaInput, countInput].forEach(el => {
    el.addEventListener('input', runSimulation);
});

runSimulation();
