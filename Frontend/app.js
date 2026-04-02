/*
 * AgriGuard AI — Frontend Logic
 * Powered by Clevatec
 * Developed by Olakunle Sunday Olalekan
 */

const API = 'https://agriguard-ai-engine.onrender.com';

// ── Helpers ──────────────────────────────────────────────────────────────────

function now() {
    return new Date().toLocaleTimeString('en-GB', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

function addLog(msg, type = 'info') {
    const logs = document.getElementById('ai-logs');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<div class="log-time">${now()}</div><div class="log-msg">${msg}</div>`;
    logs.prepend(entry);
    while (logs.children.length > 20) logs.removeChild(logs.lastChild);
}

function setLoading(btnId, resultId, loading) {
    const btn = document.getElementById(btnId);
    const res = document.getElementById(resultId);
    if (loading) {
        btn.disabled = true;
        res.innerHTML = `<span class="spinner"></span><span style="color:#4a7a5a;font-family:var(--mono);font-size:0.7rem">PROCESSING...</span>`;
    } else {
        btn.disabled = false;
    }
}

function urgencyClass(urgency) {
    const map = { 'Critical': 'critical', 'High': 'high', 'Medium': 'medium', 'None': 'none', 'Normal': 'none' };
    return map[urgency] || 'none';
}

function ratingColor(rating) {
    const map = { 'Excellent': 'green', 'Good': '', 'Fair': 'amber', 'Poor': 'red' };
    return map[rating] || '';
}

function updateStatTime() {
    document.getElementById('stat-time').textContent = now();
}

// ── Disease Prediction ────────────────────────────────────────────────────────

async function runDisease() {
    setLoading('btn-disease', 'result-disease', true);
    addLog('Initiating disease scan...', 'info');

    const body = {
        temp:         parseFloat(document.getElementById('d-temp').value),
        humidity:     parseFloat(document.getElementById('d-humidity').value),
        soil_ph:      parseFloat(document.getElementById('d-ph').value),
        rainfall:     parseFloat(document.getElementById('d-rain').value),
        wind_speed:   parseFloat(document.getElementById('d-wind').value),
        leaf_wetness: parseFloat(document.getElementById('d-wet').value)
    };

    try {
        const res  = await fetch(`${API}/predict_disease`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        const uClass    = urgencyClass(data.urgency);
        const pct       = Math.round(data.confidence * 100);
        const isDisease = data.disease !== 'Healthy';

        document.getElementById('result-disease').innerHTML = `
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">PATHOGEN</span>
                <span class="result-val ${isDisease ? 'red' : ''}">${data.disease}</span>
            </div>
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">CONFIDENCE</span>
                <span class="result-val">${pct}%</span>
            </div>
            <div class="result-row">
                <span class="result-key">URGENCY</span>
                <span class="badge ${uClass}">${data.urgency}</span>
            </div>
        `;

        document.getElementById('stat-risk').textContent = `${pct}%`;

        const logType = data.urgency === 'Critical' ? 'error'
                      : data.urgency === 'High'     ? 'warn' : 'ok';
        addLog(`Disease scan: <strong>${data.disease}</strong> — ${pct}% confidence`, logType);
        updateStatTime();

    } catch (err) {
        document.getElementById('result-disease').innerHTML =
            `<span style="color:var(--red);font-family:var(--mono);font-size:0.7rem">
                ❌ ENGINE OFFLINE — Is Flask running on port 5001?
            </span>`;
        addLog('Connection failed. Check that model_engine.py is running.', 'error');
    }

    setLoading('btn-disease', 'result-disease', false);
}

// ── Yield Prediction ──────────────────────────────────────────────────────────

async function runYield() {
    setLoading('btn-yield', 'result-yield', true);
    addLog('Computing yield forecast...', 'info');

    const body = {
        temp:          parseFloat(document.getElementById('y-temp').value),
        humidity:      parseFloat(document.getElementById('y-humidity').value),
        soil_ph:       parseFloat(document.getElementById('y-ph').value),
        rainfall:      parseFloat(document.getElementById('y-rain').value),
        fertilizer_kg: parseFloat(document.getElementById('y-fert').value),
        sunlight_hrs:  parseFloat(document.getElementById('y-sun').value)
    };

    try {
        const res  = await fetch(`${API}/predict_yield`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        const rColor = ratingColor(data.rating);
        const tons   = (data.yield_kg_per_hectare / 1000).toFixed(2);

        document.getElementById('result-yield').innerHTML = `
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">YIELD</span>
                <span class="result-val">${data.yield_kg_per_hectare.toLocaleString()} kg/ha</span>
            </div>
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">RATING</span>
                <span class="result-val ${rColor}">${data.rating}</span>
            </div>
            <div class="result-row">
                <span class="result-key">ADVICE</span>
                <span style="color:#8aaa9a;font-size:0.7rem;text-align:right;max-width:60%">
                    ${data.advice}
                </span>
            </div>
        `;

        document.getElementById('stat-yield').textContent = `${tons}T`;
        addLog(`Yield forecast: <strong>${data.yield_kg_per_hectare.toLocaleString()} kg/ha</strong> — ${data.rating}`, 'ok');
        updateStatTime();

    } catch (err) {
        document.getElementById('result-yield').innerHTML =
            `<span style="color:var(--red);font-family:var(--mono);font-size:0.7rem">
                ❌ ENGINE OFFLINE — Is Flask running on port 5001?
            </span>`;
        addLog('Connection failed. Check that model_engine.py is running.', 'error');
    }

    setLoading('btn-yield', 'result-yield', false);
}

// ── Fertilizer Recommendation ─────────────────────────────────────────────────

async function runFertilizer() {
    setLoading('btn-fert', 'result-fert', true);
    addLog('Analysing soil nutrient profile...', 'info');

    const body = {
        crop_type:  document.getElementById('f-crop').value,
        soil_ph:    parseFloat(document.getElementById('f-ph').value),
        nitrogen:   parseFloat(document.getElementById('f-n').value),
        phosphorus: parseFloat(document.getElementById('f-p').value),
        potassium:  parseFloat(document.getElementById('f-k').value),
        moisture:   parseFloat(document.getElementById('f-moisture').value)
    };

    try {
        const res  = await fetch(`${API}/recommend_fertilizer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        const pct = Math.round(data.confidence * 100);

        document.getElementById('result-fert').innerHTML = `
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">FERTILIZER</span>
                <span class="result-val blue">${data.recommended_fertilizer}</span>
            </div>
            <div class="result-row" style="margin-bottom:8px">
                <span class="result-key">CONFIDENCE</span>
                <span class="result-val">${pct}%</span>
            </div>
            <div style="color:#8aaa9a;font-size:0.68rem;line-height:1.6;
                        border-top:1px solid var(--border);padding-top:8px">
                ${data.dosage_guide}
            </div>
        `;

        document.getElementById('stat-fert').textContent = data.recommended_fertilizer;
        addLog(`Fertilizer for <strong>${data.crop}</strong>: <strong>${data.recommended_fertilizer}</strong> (${pct}%)`, 'ok');
        updateStatTime();

    } catch (err) {
        document.getElementById('result-fert').innerHTML =
            `<span style="color:var(--red);font-family:var(--mono);font-size:0.7rem">
                ❌ ENGINE OFFLINE — Is Flask running on port 5001?
            </span>`;
        addLog('Connection failed. Check that model_engine.py is running.', 'error');
    }

    setLoading('btn-fert', 'result-fert', false);
}

// ── Sensor Chart ──────────────────────────────────────────────────────────────

function initSensorChart() {
    const ctx = document.getElementById('sensorChart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: [22, 24, 27, 29, 31, 33, 32, 30, 28, 26, 24, 22],
                    borderColor: '#ff3b3b',
                    backgroundColor: 'rgba(255,59,59,0.05)',
                    tension: 0.4, pointRadius: 3,
                    pointBackgroundColor: '#ff3b3b'
                },
                {
                    label: 'Humidity (%)',
                    data: [58, 62, 68, 72, 75, 80, 78, 74, 70, 65, 60, 56],
                    borderColor: '#00aaff',
                    backgroundColor: 'rgba(0,170,255,0.05)',
                    tension: 0.4, pointRadius: 3,
                    pointBackgroundColor: '#00aaff'
                },
                {
                    label: 'Rainfall (mm)',
                    data: [40, 55, 80, 110, 140, 200, 180, 160, 120, 90, 60, 45],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0,255,136,0.05)',
                    tension: 0.4, pointRadius: 3,
                    pointBackgroundColor: '#00ff88'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    labels: {
                        color: '#4a7a5a',
                        font: { family: "'Share Tech Mono', monospace", size: 10 },
                        boxWidth: 12
                    }
                }
            },
            scales: {
                y: {
                    grid: { color: '#1a2e20' },
                    ticks: { color: '#4a7a5a', font: { family: "'Share Tech Mono', monospace", size: 10 } }
                },
                x: {
                    grid: { color: '#1a2e20' },
                    ticks: { color: '#4a7a5a', font: { family: "'Share Tech Mono', monospace", size: 10 } }
                }
            }
        }
    });
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initSensorChart();
    addLog('Engine handshake complete. All 3 AI modules loaded.', 'ok');
});
