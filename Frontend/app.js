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
    if (!logs) return;
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<div class="log-time">${now()}</div><div class="log-msg">${msg}</div>`;
    logs.prepend(entry);
    while (logs.children.length > 20) logs.removeChild(logs.lastChild);
}

function setLoading(btnId, resultId, loading) {
    const btn = document.getElementById(btnId);
    const res = document.getElementById(resultId);
    if (!btn || !res) return;

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
    const statTime = document.getElementById('stat-time');
    if (statTime) statTime.textContent = now();
}

// ── Disease Prediction ────────────────────────────────────────────────────────

async function runDisease() {
    setLoading('btn-disease', 'result-disease', true);
    addLog('Initiating cloud disease scan...', 'info');

    const body = {
        temp:         parseFloat(document.getElementById('d-temp').value) || 0,
        humidity:     parseFloat(document.getElementById('d-humidity').value) || 0,
        soil_ph:      parseFloat(document.getElementById('d-ph').value) || 0,
        rainfall:     parseFloat(document.getElementById('d-rain').value) || 0,
        wind_speed:   parseFloat(document.getElementById('d-wind').value) || 0,
        leaf_wetness: parseFloat(document.getElementById('d-wet').value) || 0
    };

    try {
        const res  = await fetch(`${API}/predict_disease`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        const uClass    = urgencyClass(data.urgency);
        const pct       = Math.round((data.confidence || 0) * 100);
        const isDisease = data.disease !== 'Healthy';

        document.getElementById('result-disease').innerHTML = `
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">PATHOGEN</span>
                <span class="result-val ${isDisease ? 'red' : ''}">${data.disease || 'Unknown'}</span>
            </div>
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">CONFIDENCE</span>
                <span class="result-val">${pct}%</span>
            </div>
            <div class="result-row">
                <span class="result-key">URGENCY</span>
                <span class="badge ${uClass}">${data.urgency || 'Normal'}</span>
            </div>
        `;

        const statRisk = document.getElementById('stat-risk');
        if (statRisk) statRisk.textContent = `${pct}%`;

        const logType = data.urgency === 'Critical' ? 'error' : (data.urgency === 'High' ? 'warn' : 'ok');
        addLog(`Disease scan: <strong>${data.disease}</strong> — ${pct}% confidence`, logType);
        updateStatTime();

    } catch (err) {
        document.getElementById('result-disease').innerHTML = 
            `<span style="color:var(--red);font-family:var(--mono);font-size:0.7rem">❌ CLOUD ENGINE OFFLINE — Check Render status.</span>`;
        addLog('Cloud connection failed. Check your internet or Render dashboard.', 'error');
    }
    setLoading('btn-disease', 'result-disease', false);
}

// ── Yield Prediction ──────────────────────────────────────────────────────────

async function runYield() {
    setLoading('btn-yield', 'result-yield', true);
    addLog('Computing cloud yield forecast...', 'info');

    const body = {
        temp:          parseFloat(document.getElementById('y-temp').value) || 0,
        humidity:      parseFloat(document.getElementById('y-humidity').value) || 0,
        soil_ph:       parseFloat(document.getElementById('y-ph').value) || 0,
        rainfall:      parseFloat(document.getElementById('y-rain').value) || 0,
        fertilizer_kg: parseFloat(document.getElementById('y-fert').value) || 0,
        sunlight_hrs:  parseFloat(document.getElementById('y-sun').value) || 0
    };

    try {
        const res  = await fetch(`${API}/predict_yield`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();

        const rColor = ratingColor(data.rating);
        const yieldVal = data.yield_kg_per_hectare || 0;
        const tons   = (yieldVal / 1000).toFixed(2);

        document.getElementById('result-yield').innerHTML = `
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">YIELD</span>
                <span class="result-val">${yieldVal.toLocaleString()} kg/ha</span>
            </div>
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">RATING</span>
                <span class="result-val ${rColor}">${data.rating || 'N/A'}</span>
            </div>
            <div class="result-row">
                <span class="result-key">ADVICE</span>
                <span style="color:#8aaa9a;font-size:0.7rem;text-align:right;max-width:60%">
                    ${data.advice || 'No specific advice available.'}
                </span>
            </div>
        `;

        const statYield = document.getElementById('stat-yield');
        if (statYield) statYield.textContent = `${tons}T`;
        addLog(`Yield forecast: <strong>${yieldVal.toLocaleString()} kg/ha</strong> — ${data.rating}`, 'ok');
        updateStatTime();

    } catch (err) {
        document.getElementById('result-yield').innerHTML = 
            `<span style="color:var(--red);font-family:var(--mono);font-size:0.7rem">❌ CLOUD ENGINE OFFLINE</span>`;
        addLog('Yield computation failed. Check Render logs.', 'error');
    }
    setLoading('btn-yield', 'result-yield', false);
}

// ── Fertilizer Recommendation ─────────────────────────────────────────────────

async function runFertilizer() {
    setLoading('btn-fert', 'result-fert', true);
    addLog('Analysing cloud nutrient profile...', 'info');

    const body = {
        crop_type:  document.getElementById('f-crop').value,
        soil_ph:    parseFloat(document.getElementById('f-ph').value) || 0,
        nitrogen:   parseFloat(document.getElementById('f-n').value) || 0,
        phosphorus: parseFloat(document.getElementById('f-p').value) || 0,
        potassium:  parseFloat(document.getElementById('f-k').value) || 0,
        moisture:   parseFloat(document.getElementById('f-moisture').value) || 0
    };

    try {
        const res  = await fetch(`${API}/recommend_fertilizer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        const pct = Math.round((data.confidence || 0) * 100);

        document.getElementById('result-fert').innerHTML = `
            <div class="result-row" style="margin-bottom:6px">
                <span class="result-key">FERTILIZER</span>
                <span class="result-val blue">${data.recommended_fertilizer || 'Unknown'}</span>
            </div>
            <div class="result-row" style="margin-bottom:8px">
                <span class="result-key">CONFIDENCE</span>
                <span class="result-val">${pct}%</span>
            </div>
            <div style="color:#8aaa9a;font-size:0.68rem;line-height:1.6; border-top:1px solid var(--border);padding-top:8px">
                ${data.dosage_guide || 'Follow general N-P-K guidelines.'}
            </div>
        `;

        const statFert = document.getElementById('stat-fert');
        if (statFert) statFert.textContent = data.recommended_fertilizer;
        addLog(`AI Recommendation: <strong>${data.recommended_fertilizer}</strong> (${pct}%)`, 'ok');
        updateStatTime();

    } catch (err) {
        document.getElementById('result-fert').innerHTML = 
            `<span style="color:var(--red);font-family:var(--mono);font-size:0.7rem">❌ CLOUD ENGINE OFFLINE</span>`;
        addLog('Fertilizer analysis failed. API unreachable.', 'error');
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
