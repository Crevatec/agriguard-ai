/*
Powered by Clevatec
Developed by Olakunle Sunday Olalekan
*/
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet()); // Security Headers
app.use(cors());
app.use(express.json());

// Mock DB Controller Logic
app.get('/api/v1/sensors/latest', (req, res) => {
    // In production, this pulls from PostgreSQL sensor_logs
    res.json({
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        temperature: [22, 21, 24, 29, 28, 25],
        humidity: [65, 70, 68, 55, 60, 62]
    });
});

app.post('/api/v1/predict', async (req, res) => {
    const { temp, humidity } = req.body;
    
    // Logic: Interfacing with Python AI Microservice
    try {
        // This is a placeholder for a fetch() call to the Python ai-module
        const riskScore = (temp * 0.2 + humidity * 0.8) / 10; 
        res.status(200).json({ 
            risk_score: riskScore.toFixed(2),
            status: riskScore > 7 ? 'CRITICAL' : 'STABLE'
        });
    } catch (err) {
        res.status(500).json({ error: "AI Inference Service Offline" });
    }
});

app.listen(PORT, () => {
    console.log(`AgriGuard Backend Ops running on port ${PORT}`);
});