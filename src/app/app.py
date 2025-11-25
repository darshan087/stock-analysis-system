"""Flask application factory"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask, render_template_string
from src.config.settings import get_config
from src.app.routes import api


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Register blueprints
    app.register_blueprint(api)
    
    @app.route("/", methods=["GET"])
    def index():
        html = """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Stock Analysis</title>
            <style>
                body {
                    font-family: Arial, Helvetica, sans-serif;
                    margin: 0;
                    color: #111;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 40px;
                    background: linear-gradient(135deg, #ff7eb3 0%, #ff65a3 25%, #7afcff 75%, #65d6ff 100%);
                    background-attachment: fixed;
                }
                .card {
                    background: rgba(255, 255, 255, 0.92);
                    padding: 24px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.18);
                    max-width: 900px;
                    width: 100%;
                    border: 1px solid rgba(255,255,255,0.6);
                }
                h1 { color: #2b2b2b }
                label { display:block; margin-top:10px }
                input[type=text], input[type=number] { padding:8px; width:200px; border-radius:4px; border:1px solid #ddd }
                button { margin-top:12px; padding:8px 12px; border-radius:6px; background:#667eea; color:white; border:none; cursor:pointer }
                button:hover { background:#5566d6 }
                pre { background: rgba(246,246,246,0.9); padding:12px; border-radius:6px; white-space:pre-wrap; overflow:auto }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Stock Analysis</h1>
                <p>This API uses local stock files found in <code>data/Stocks/</code> when available. Use the API endpoints under <code>/api/</code> to interact with the data.</p>

                <h3>Forecast</h3>
                <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
                    <div style="min-width:220px;">
                        <label style="font-weight:600; font-size:0.9rem;">Ticker</label>
                        <select id="ticker" style="width:100%; padding:10px; border-radius:8px; border:1px solid #e6e6e6; background:linear-gradient(180deg,#fff,#f8f8ff);">
                            <option>AAPL</option>
                        </select>
                    </div>

                    <div style="width:120px;">
                        <label style="font-weight:600; font-size:0.9rem;">Days</label>
                        <input id="days" type="number" value="5" min="1" max="30" style="width:100%; padding:10px; border-radius:8px; border:1px solid #e6e6e6;" />
                    </div>

                    <div style="min-width:200px;">
                        <label style="font-weight:600; font-size:0.9rem;">Method</label>
                        <select id="method" style="width:100%; padding:10px; border-radius:8px; border:1px solid #e6e6e6; background:linear-gradient(180deg,#fff,#f8f8ff);">
                            <option value="exp_smooth">Exponential Smoothing</option>
                            <option value="linear_trend">Linear Trend</option>
                        </select>
                    </div>

                    <div>
                        <button id="run" style="background:#ff6b81; display:inline-flex; align-items:center; gap:8px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 12h14" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 5l7 7-7 7" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                            Run Forecast
                        </button>
                    </div>
                </div>

                                <h4>Result</h4>
                                <div style="display:flex; gap:16px; flex-wrap:wrap; align-items:flex-start;">
                                        <div style="flex:1 1 520px; min-height:220px;">
                                                <canvas id="chart" style="width:100%; height:100%; display:block"></canvas>
                                        </div>
                                        <div style="width:260px;">
                                                <div style="background:rgba(255,255,255,0.98); padding:12px; border-radius:8px; border:1px solid rgba(0,0,0,0.04); box-shadow:0 6px 20px rgba(0,0,0,0.06);">
                                                        <h4 style="margin-top:0;">Summary</h4>
                                                        <div id="stats">No data yet.</div>
                                                </div>
                                        </div>
                                </div>
                                
            </div>

            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
            <script>
                async function fetchTickers() {
                    try {
                        const res = await fetch('/api/tickers');
                        const json = await res.json();
                        return json.tickers || [];
                    } catch (err) {
                        console.warn('Could not load local tickers', err);
                        return [];
                    }
                }

                async function runForecast(ticker, days, method) {
                    const url = `/api/forecast?ticker=${encodeURIComponent(ticker)}&days=${encodeURIComponent(days)}&method=${encodeURIComponent(method)}`;
                    try {
                        const res = await fetch(url);
                        return await res.json();
                    } catch (err) {
                        return { error: String(err) };
                    }
                }

                (async () => {
                    // populate tickers dropdown
                    const tickers = await fetchTickers();
                    const tickerSelect = document.getElementById('ticker');
                    tickerSelect.innerHTML = '';
                    if (tickers.length === 0) {
                        tickerSelect.innerHTML = '<option>AAPL</option>';
                    } else {
                        tickers.forEach(t => {
                            const opt = document.createElement('option'); opt.value = t; opt.textContent = t; tickerSelect.appendChild(opt);
                        });
                    }

                    // Chart instance
                    let chart = null;

                    document.getElementById('run').addEventListener('click', async () => {
                        const ticker = document.getElementById('ticker').value || 'AAPL';
                        const days = document.getElementById('days').value || 5;
                        const method = document.getElementById('method').value || 'exp_smooth';

                        const containerStats = document.getElementById('stats');
                        containerStats.textContent = 'Loading...';

                        const json = await runForecast(ticker, days, method);

                        if (!json || json.error) {
                            containerStats.textContent = 'Error: ' + (json && json.error ? json.error : 'Unknown');
                            if (chart) { chart.destroy(); chart = null; }
                            return;
                        }

                        const labels = (json.forecast || []).map(f => f.date);
                        const data = (json.forecast || []).map(f => f.price);

                        const ctx = document.getElementById('chart').getContext('2d');
                        if (chart) chart.destroy();
                        chart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: `${json.ticker} forecast`,
                                    data: data,
                                    borderColor: 'rgba(102,126,234,1)',
                                    backgroundColor: 'rgba(102,126,234,0.12)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.25,
                                    pointRadius: 4,
                                    pointBackgroundColor: 'white',
                                    pointBorderColor: 'rgba(102,126,234,1)'
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: { x: { display: true }, y: { display: true } },
                                plugins: { legend: { display: true }, tooltip: { mode: 'index', intersect: false } }
                            }
                        });

                        // Update stats panel
                        const avg = json.avg_forecast !== undefined ? json.avg_forecast.toFixed(4) : 'N/A';
                        const current = json.current_price !== undefined ? json.current_price.toFixed(4) : 'N/A';
                        const lastDate = json.last_date || '-';
                        containerStats.innerHTML = `\n<div><strong>Ticker:</strong> ${json.ticker}</div>\n<div><strong>Method:</strong> ${json.method}</div>\n<div><strong>Last date:</strong> ${lastDate}</div>\n<div><strong>Current price:</strong> ${current}</div>\n<div><strong>Avg forecast:</strong> ${avg}</div>\n`;
                    });
                })();
            </script>
        </body>
        </html>
        """
        return render_template_string(html)
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
