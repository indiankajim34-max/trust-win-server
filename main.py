from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import time

app = Flask(__name__)
app.secret_key = 'trustwin_ultimate_secret_key_2026'

# Secure Firebase Initialization via Render Environment Variables
if not firebase_admin._apps:
    try:
        firebase_json_str = os.environ.get('FIREBASE_CONFIG_JSON')
        if firebase_json_str:
            cred_dict = json.loads(firebase_json_str)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized securely from Environment Variable.")
        else:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
            print("Firebase initialized from local file.")
    except Exception as e:
        print(f"Firebase initialization error: {e}")

db = firestore.client() if firebase_admin._apps else None

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trust Win VIP - License Login</title>
    <style>
        body { background-color: #080808; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }
        .login-card { background: linear-gradient(145deg, #121212, #1a1a1a); border: 2px solid #d4af37; border-radius: 20px; padding: 25px; width: 100%; max-width: 350px; box-shadow: 0 0 30px rgba(212, 175, 55, 0.4); }
        .title { font-size: 18px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
        .sub { font-size: 11px; color: #888; margin-bottom: 20px; }
        .input-box { width: 100%; padding: 12px; background: #161616; border: 1px solid #444; border-radius: 10px; color: #fff; font-size: 14px; text-align: center; margin-bottom: 15px; box-sizing: border-box; outline: none; text-transform: uppercase; font-weight: bold; }
        .input-box:focus { border-color: #d4af37; box-shadow: 0 0 10px rgba(212, 175, 55, 0.3); }
        .btn { background: linear-gradient(45deg, #d4af37, #ffdf73); color: #000; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(212,175,55,0.4); }
        .error { color: #ff4444; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="title">👑 TRUST WIN VIP 👑</div>
        <div class="sub">ENTER TRUST WIN LICENSE KEY</div>
        <form method="POST">
            <input type="text" name="license_key" class="input-box" placeholder="TRUSTWIN-XXXX-XXXX" required autocomplete="off">
            <button type="submit" class="btn">VERIFY & UNLOCK</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Trust Win VIP Oracle Radar</title>
    <style>
        @keyframes glow {
            0% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.2); border-color: #d4af37; }
            50% { box-shadow: 0 0 30px rgba(212, 175, 55, 0.6); border-color: #ffdf73; }
            100% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.2); border-color: #d4af37; }
        }
        @keyframes radar-pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.05); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }
        @keyframes btn-glow {
            0% { box-shadow: 0 0 15px rgba(0,255,136,0.4); }
            50% { box-shadow: 0 0 30px rgba(0,255,136,0.9); }
            100% { box-shadow: 0 0 15px rgba(0,255,136,0.4); }
        }
        @keyframes text-flash {
            0% { opacity: 0.4; }
            50% { opacity: 1; color: #00ff88; text-shadow: 0 0 15px #00ff88; }
            100% { opacity: 0.4; }
        }
        * { box-sizing: border-box; }
        body { background-color: #0c0c0c; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 6px; overflow: hidden; position: fixed; width: 100%; height: 100%; }
        .container { max-width: 410px; height: 100%; margin: auto; background: linear-gradient(145deg, #121212, #181818); border: 2px solid #d4af37; border-radius: 16px; padding: 10px; animation: glow 4s infinite ease-in-out; position: relative; display: flex; flex-direction: column; overflow: hidden; }
        
        .top-banner { background: #181818; border: 1px solid #333; border-radius: 12px; padding: 8px; margin-bottom: 6px; flex-shrink: 0; }
        .vip-header { display: flex; justify-content: space-between; align-items: center; font-size: 10px; font-weight: bold; color: #d4af37; border-bottom: 1px solid #282828; padding-bottom: 4px; margin-bottom: 4px; }
        .live-dot { height: 7px; width: 7px; background-color: #00ff88; border-radius: 50%; display: inline-block; box-shadow: 0 0 6px #00ff88; }
        
        .main-title { font-size: 15px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
        .sub-engine { font-size: 9px; color: #888; margin-top: 2px; letter-spacing: 0.5px; }
        .time-row { display: flex; justify-content: space-between; font-size: 10px; color: #aaa; margin-top: 4px; padding: 0 4px; }

        .huge-last-result { background: linear-gradient(145deg, #161616, #202020); border: 2px solid #ffdf73; border-radius: 10px; padding: 8px; margin: 6px 0; box-shadow: 0 0 12px rgba(255,223,115,0.2); flex-shrink: 0; }
        .huge-last-title { font-size: 9px; color: #ffdf73; font-weight: bold; letter-spacing: 1.5px; margin-bottom: 2px; }
        .huge-last-val { font-size: 16px; font-weight: bold; color: #00ff88; text-shadow: 0 0 8px rgba(0,255,136,0.5); }

        .host-box { background: #161616; border: 1px solid #333; border-radius: 8px; padding: 6px 10px; margin: 6px 0; display: flex; justify-content: space-between; align-items: center; font-size: 10px; flex-shrink: 0; }
        .host-left { text-align: left; }
        .host-right { text-align: right; color: #00ff88; font-weight: bold; }

        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin: 6px 0; flex-shrink: 0; }
        .stat-card { background: #181818; border: 1px solid #333; padding: 6px 2px; border-radius: 8px; }
        .stat-card .lbl { font-size: 8px; color: #888; }
        .stat-card .val { font-size: 13px; font-weight: bold; color: #fff; margin-top: 2px; display: block; }

        .period-box { background: #161616; border: 1px solid #333; border-radius: 8px; padding: 8px; margin: 6px 0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
        .period-box div { text-align: left; font-size: 10px; color: #aaa; }
        .period-box span { font-size: 13px; font-weight: bold; color: #fff; display: block; }
        .countdown { font-size: 16px !important; font-weight: bold; color: #ffcc00 !important; font-family: monospace; }

        .radar-box { background: #141414; border: 1px solid #333; border-radius: 12px; padding: 10px; margin-top: 6px; position: relative; overflow: hidden; flex-grow: 1; display: flex; flex-direction: column; justify-content: center; }
        
        /* Terminal Header with Left-Side Premium Animated Round Button */
        .radar-header-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
        .premium-round-btn { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(45deg, #00ff88, #00cc66); border: 2px solid #fff; color: #000; font-size: 16px; font-weight: bold; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 15px rgba(0,255,136,0.8); animation: btn-glow 2s infinite; transition: 0.2s; flex-shrink: 0; }
        .premium-round-btn:active { transform: scale(0.92); }

        .radar-titles { text-align: left; flex-grow: 1; }
        .radar-title { font-size: 9px; color: #777; letter-spacing: 1px; }
        .radar-sub { font-size: 8px; color: #aaa; margin-top: 2px; }
        
        .radar-circle-wrap { width: 110px; height: 110px; margin: 6px auto; border: 1px dashed rgba(212,175,55,0.4); border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; animation: radar-pulse 3s infinite ease-in-out; }
        .radar-circle-inner { width: 75px; height: 75px; border: 1px solid rgba(212,175,55,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; text-align: center; padding: 4px; }
        .prediction-display { font-size: 16px; font-weight: bold; color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.6); }
        .analyzing-text { font-size: 9px; font-weight: bold; color: #00ff88; animation: text-flash 1s infinite; line-height: 1.2; }

        .tab-content { display: none; height: 100%; flex-direction: column; }
        .tab-content.active { display: flex; }

        /* BDG Chart Exact Layout Styles */
        .chart-scroll-area { flex-grow: 1; overflow-y: auto; overflow-x: hidden; max-height: calc(100vh - 270px); position: relative; padding-right: 2px; margin-top: 6px; }
        .tiranga-row { background: #161616; border: 1px solid #333; border-radius: 6px; padding: 5px 6px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; font-size: 9px; }
        .tiranga-period { color: #aaa; font-family: monospace; font-size: 8px; text-align: left; width: 70px; flex-shrink: 0; }
        .tiranga-nums { display: flex; gap: 2px; align-items: center; justify-content: space-between; flex-grow: 1; padding: 0 4px; }
        
        .t-num-circle { width: 17px; height: 17px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 8px; font-weight: bold; background: #1f1f1f; color: #555; border: 1px solid #333; }
        .t-num-circle.c-violet { background: #9b59b6 !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 5px #9b59b6; }
        .t-num-circle.c-green { background: #2ecc71 !important; color: #000 !important; border-color: #fff !important; box-shadow: 0 0 5px #2ecc71; }
        .t-num-circle.c-red { background: #e74c3c !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 5px #e74c3c; }

        .badge-big-bdg { background: #f1c40f; color: #000; padding: 1px 4px; border-radius: 3px; font-weight: bold; font-size: 8px; width: 18px; text-align: center; flex-shrink: 0; }
        .badge-small-bdg { background: #3498db; color: #fff; padding: 1px 4px; border-radius: 3px; font-weight: bold; font-size: 8px; width: 18px; text-align: center; flex-shrink: 0; }

        .log-list { flex-grow: 1; overflow-y: auto; text-align: left; font-size: 10px; margin-top: 6px; }
        .log-item { background: #161616; border: 1px solid #333; border-radius: 6px; padding: 6px 8px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; }
        .badge-win { color: #00ff88; font-weight: bold; background: rgba(0,255,136,0.1); padding: 2px 5px; border-radius: 3px; }
        .badge-loss { color: #ff4444; font-weight: bold; background: rgba(255,68,68,0.1); padding: 2px 5px; border-radius: 3px; }

        .profile-card { background: #161616; border: 1px solid #333; border-radius: 10px; padding: 12px; margin-top: 10px; text-align: left; font-size: 11px; }
        .profile-card p { margin: 6px 0; color: #bbb; }
        .profile-card span { color: #fff; font-weight: bold; }

        /* Fixed Bottom Navigation Bar */
        .bottom-nav { position: absolute; bottom: 0; left: 0; right: 0; background: #111; border-top: 1px solid #333; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; display: grid; grid-template-columns: repeat(5, 1fr); padding: 5px 0; z-index: 10; }
        .nav-item { font-size: 8px; color: #888; cursor: pointer; transition: 0.2s; text-decoration: none; }
        .nav-item.active { color: #d4af37; font-weight: bold; }
        .nav-item div { font-size: 12px; margin-bottom: 1px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-banner">
            <div class="vip-header">
                <span>👑 TRUST WIN VIP</span>
                <span>🔑 KEY: <span style="color:#00ff88;">ACTIVE</span> (<span id="keyTimer">30d 00h</span>)</span>
            </div>
            <div class="main-title">🍁 TRUST WIN 🍁</div>
            <div class="sub-engine">WINGO UTC CLOCK-DRIVEN ENGINE</div>
            <div class="time-row">
                <span id="currentTime">--:--:-- PM</span>
                <span id="currentDate">--/--/----</span>
            </div>
        </div>

        <div class="huge-last-result">
            <div class="huge-last-title">🔥 LIVE WINGO RESULT TRACKER 🔥</div>
            <div class="huge-last-val" id="hugeResultVal">Connecting to Worker...</div>
        </div>

        <div class="host-box">
            <div class="host-left">
                <div style="font-size:8px; color:#888;">PERIOD SYNC</div>
                <div style="font-size:9px; color:#ccc;">LIVE CLOCK TICKS</div>
            </div>
            <div class="host-right" style="color:#00ff88;">
                <div style="font-size:8px; color:#888;">ZIGZAG LINE</div>
                <div>PERFECT</div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="lbl">TOTAL</div>
                <span class="val" id="statTotal">0</span>
            </div>
            <div class="stat-card" style="border-color: #00ff8844;">
                <div class="lbl" style="color:#00ff88;">WIN</div>
                <span class="val" id="statWins" style="color: #00ff88;">0</span>
            </div>
            <div class="stat-card" style="border-color: #ff444444;">
                <div class="lbl" style="color:#ff4444;">LOSS</div>
                <span class="val" id="statLosses" style="color: #ff4444;">0</span>
            </div>
            <div class="stat-card" style="border-color: #ffcc0044;">
                <div class="lbl" style="color:#ffcc00;">JACKPOT</div>
                <span class="val" id="statJackpots" style="color: #ffcc00;">0</span>
            </div>
        </div>

        <div class="period-box">
            <div>
                <span>CURRENT PERIOD</span>
                <b id="periodVal" style="color:#fff; font-size:11px;">Syncing...</b>
            </div>
            <div style="text-align: right;">
                <span>NEXT SIGNAL IN</span>
                <div class="countdown" id="timer">00:60</div>
            </div>
        </div>

        <!-- TERMINAL TAB -->
        <div id="tab-terminal" class="tab-content active">
            <div class="radar-box">
                <!-- Header with Left-Side Premium Animated Round Button -->
                <div class="radar-header-row">
                    <button type="button" class="premium-round-btn" onclick="revealPrediction()" title="Check Result">🎯</button>
                    <div class="radar-titles">
                        <div class="radar-title">AI ORACLE RADAR TERMINAL</div>
                        <div class="radar-sub">200-RESULT FREQUENCY & PATTERN SCAN</div>
                    </div>
                </div>
                
                <div class="radar-circle-wrap">
                    <div class="radar-circle-inner" id="radarInner">
                        <div class="prediction-display" id="predDisplay">
                            🔒 LOCKED
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- PATTERN TAB (BDG WIN EXACT STYLE WITH PERFECT ZIGZAG LINE) -->
        <div id="tab-pattern" class="tab-content">
            <div class="radar-box" style="text-align: left; padding: 8px; display: block;">
                <div class="radar-title" style="text-align: center; margin-bottom: 2px;">📊 BDG CHART & ZIGZAG TREND</div>
                <div class="radar-sub" style="text-align: center; margin-bottom: 6px;">EXACT COLOR MAPPING & ALIGNED LINE</div>
                <div class="chart-scroll-area" id="tirangaPatternList">
                    <div style="text-align:center; color:#777; padding:20px;">Loading BDG Chart Data...</div>
                </div>
            </div>
        </div>

        <!-- LOG TAB -->
        <div id="tab-log" class="tab-content">
            <div class="radar-box" style="text-align: left; display: block;">
                <div class="radar-title" style="text-align: center; margin-bottom: 6px;">📜 REAL HISTORY LOG</div>
                <div class="log-list" id="logList">
                    <div style="text-align:center; color:#777; padding:20px;">Waiting for real round completion...</div>
                </div>
            </div>
        </div>

        <!-- STATS TAB -->
        <div id="tab-stats" class="tab-content">
            <div class="radar-box" style="display: block;">
                <div class="radar-title">📊 PERFORMANCE METRICS</div>
                <div style="background:#161616; border-radius:8px; padding:10px; margin-top:8px; text-align:left; font-size:11px;">
                    <p style="display:flex; justify-content:space-between; margin:5px 0;"><span>Total Rounds:</span> <b id="statTotal2" style="color:#fff;">0</b></p>
                    <p style="display:flex; justify-content:space-between; margin:5px 0;"><span>Real Accuracy:</span> <b id="statAccuracy" style="color:#00ff88;">0.0%</b></p>
                    <p style="display:flex; justify-content:space-between; margin:5px 0;"><span>Engine Status:</span> <b style="color:#00ff88;">UTC Clock-Driven Active</b></p>
                </div>
            </div>
        </div>

        <!-- PROFILE TAB -->
        <div id="tab-profile" class="tab-content">
            <div class="radar-box" style="text-align: left; display: block;">
                <div class="radar-title" style="text-align: center;">👑 USER PROFILE</div>
                <div class="profile-card">
                    <p>Active Key: <span style="color:#00ff88;">{{ session.get('active_key') }}</span></p>
                    <p>License Status: <span style="color:#00ff88;">Active VIP</span></p>
                    <p>Server Connected: <span>Cloud Dedicated Node</span></p>
                    <br>
                    <a href="/logout" style="display:block; text-align:center; background:#ff4444; color:#000; text-decoration:none; padding:8px; border-radius:6px; font-weight:bold;">LOGOUT ACCOUNT</a>
                </div>
            </div>
        </div>

        <!-- 5-ITEM BOTTOM NAV -->
        <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('terminal', this)">
                <div>📈</div>TERMINAL
            </div>
            <div class="nav-item" onclick="switchTab('pattern', this)">
                <div>📊</div>PATTERN
            </div>
            <div class="nav-item" onclick="switchTab('log', this)">
                <div>📜</div>LOG
            </div>
            <div class="nav-item" onclick="switchTab('stats', this)">
                <div>📊</div>STATS
            </div>
            <div class="nav-item" onclick="switchTab('profile', this)">
                <div>👑</div>PROFILE
            </div>
        </div>
    </div>

    <script>
        const WORKER_URL = "https://wingo-cloudflare-worker.anishanisha143love.workers.dev";

        let totalRounds = 0;
        let winsCount = 0;
        let lossesCount = 0;
        let jackpotsCount = 0;
        let historyLogs = [];
        let isRevealed = false;
        let currentPredType = "WAITING";
        let currentPredNum = 0;
        let lastEvaluatedIssue = null;

        function switchTab(tabName, element) {
            playClickSound();
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            element.classList.add('active');
        }

        function playAiSearchingSound() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                let startTime = audioCtx.currentTime;
                for(let i = 0; i < 5; i++) {
                    let osc = audioCtx.createOscillator();
                    let gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    let freq = 400 + (i * 250);
                    osc.frequency.setValueAtTime(freq, startTime + (i * 0.1));
                    osc.frequency.exponentialRampToValueAtTime(freq + 300, startTime + (i * 0.1) + 0.08);
                    gain.gain.setValueAtTime(0.08, startTime + (i * 0.1));
                    gain.gain.exponentialRampToValueAtTime(0.001, startTime + (i * 0.1) + 0.09);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start(startTime + (i * 0.1));
                    osc.stop(startTime + (i * 0.1) + 0.09);
                }
            } catch(e) {}
        }

        function playClickSound() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(587.33, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15);
                gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.2);
            } catch(e) {}
        }

        function revealPrediction() {
            playAiSearchingSound();
            const inner = document.getElementById('radarInner');
            inner.innerHTML = '<div class="analyzing-text">TRUST AI<br>ANALYSING...</div>';

            setTimeout(() => {
                isRevealed = true;
                inner.innerHTML = `<div class="prediction-display">${currentPredType} : ${currentPredNum}</div>`;
            }, 2000);
        }

        // 100% Live UTC Clock-Driven Period Generator (Never lags behind API)
        function getLiveUTCPeriod() {
            const now = new Date();
            const yyyy = now.getUTCFullYear();
            const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
            const dd = String(now.getUTCDate()).padStart(2, '0');
            const hours = now.getUTCHours();
            const mins = now.getUTCMinutes();
            const totalMins = hours * 60 + mins;
            const serial = 10000 + totalMins + 1; // Always strictly 1 step ahead
            return `${yyyy}${mm}${dd}1000${serial}`;
        }

        async function fetchLotteryData() {
            try {
                const res = await fetch(WORKER_URL);
                const data = await res.json();
                const items = data.data && data.data.list ? data.data.list : [];
                if (items.length > 0) {
                    const latest = items[0];
                    const actIssue = String(latest.issueNumber);
                    const actNum = parseInt(latest.number, 10);
                    const actType = actNum >= 5 ? "BIG" : "SMALL";

                    document.getElementById('hugeResultVal').innerText = `${actType} : ${actNum} (Period: ${actIssue.slice(-4)})`;

                    if (lastEvaluatedIssue && lastEvaluatedIssue !== actIssue) {
                        totalRounds++;
                        let statusRes = "LOSS";
                        if (currentPredType === actType && currentPredNum === actNum) {
                            jackpotsCount++;
                            winsCount++;
                            statusRes = "JACKPOT";
                        } else if (currentPredType === actType) {
                            winsCount++;
                            statusRes = "WIN";
                        } else {
                            lossesCount++;
                            statusRes = "LOSS";
                        }

                        historyLogs.unshift({
                            issue: actIssue,
                            pred: `${currentPredType} : ${currentPredNum}`,
                            act_type: actType,
                            act_num: actNum,
                            status: statusRes
                        });
                        if (historyLogs.length > 50) historyLogs.pop();
                        updateLogUI();

                        isRevealed = false;
                        document.getElementById('radarInner').innerHTML = `<div class="prediction-display" id="predDisplay">🔒 LOCKED</div>`;
                    }

                    updateBdgChartUI(items);

                    // DEEP 200-RESULT AI SCAN & ANALYSIS
                    const analysisPool = items.slice(0, 200);
                    let digitFreq = {};
                    for(let i=0; i<=9; i++) digitFreq[i] = 0;
                    let bigCount = 0;
                    let smallCount = 0;

                    analysisPool.forEach(item => {
                        let num = parseInt(item.number, 10);
                        if (!isNaN(num)) {
                            digitFreq[num]++;
                            if(num >= 5) bigCount++;
                            else smallCount++;
                        }
                    });

                    const recentNumbers = analysisPool.slice(0, 15).map(x => parseInt(x.number, 10));
                    const recentTypes = recentNumbers.map(n => n >= 5 ? "BIG" : "SMALL");
                    
                    let streakCount = 1;
                    for (let i = 1; i < recentTypes.length; i++) {
                        if (recentTypes[i] === recentTypes[0]) streakCount++;
                        else break;
                    }

                    let lastType = recentTypes[0];
                    let predT = lastType;

                    if (streakCount >= 4) {
                        predT = lastType === "BIG" ? "SMALL" : "BIG";
                    } else {
                        if (bigCount > smallCount + 12) predT = "SMALL";
                        else if (smallCount > bigCount + 12) predT = "BIG";
                        else predT = lastType;
                    }

                    let subPool = predT === "BIG" ? [5, 6, 7, 8, 9] : [0, 1, 2, 3, 4];
                    let sortedSubPool = subPool.sort((a, b) => digitFreq[a] - digitFreq[b]);
                    let predN = sortedSubPool[0];

                    currentPredType = predT;
                    currentPredNum = predN;
                    lastEvaluatedIssue = actIssue;

                    document.getElementById('statTotal').innerText = totalRounds;
                    document.getElementById('statWins').innerText = winsCount;
                    document.getElementById('statLosses').innerText = lossesCount;
                    document.getElementById('statJackpots').innerText = jackpotsCount;
                    document.getElementById('statTotal2').innerText = totalRounds;
                    
                    let acc = totalRounds > 0 ? ((winsCount / totalRounds) * 100).toFixed(1) : "0.0";
                    document.getElementById('statAccuracy').innerText = acc + "%";
                }
            } catch(e) {
                console.error("Fetch error:", e);
            }
        }

        function updateBdgChartUI(items) {
            const container = document.getElementById('tirangaPatternList');
            let html = '<div style="position:relative;" id="chartWrapper"><svg id="zigzagSvg" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:1;"></svg>';
            
            const displayItems = items.slice(0, 40);
            displayItems.forEach((item, index) => {
                let issueNum = String(item.issueNumber);
                let actualNum = parseInt(item.number, 10);
                let isBig = actualNum >= 5;
                let badgeClass = isBig ? 'badge-big-bdg' : 'badge-small-bdg';
                let badgeText = isBig ? 'B' : 'S';

                let circlesHtml = '';
                for(let i=0; i<=9; i++) {
                    let isActive = (i === actualNum);
                    let colorClass = '';
                    if (isActive) {
                        if (i === 0 || i === 5) colorClass = 'c-violet';
                        else if ([1, 3, 7, 9].includes(i)) colorClass = 'c-green';
                        else colorClass = 'c-red';
                    }
                    circlesHtml += `<div class="t-num-circle ${isActive ? 'active ' + colorClass : ''}" id="circle-${index}-${i}">${i}</div>`;
                }

                html += `
                <div class="tiranga-row" style="position:relative; z-index:2;">
                    <div class="tiranga-period">${issueNum.slice(-4)}</div>
                    <div class="tiranga-nums">${circlesHtml}</div>
                    <div class="tiranga-badge ${badgeClass}">${badgeText}</div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;

            setTimeout(() => {
                drawZigzagLine();
            }, 50);
        }

        function drawZigzagLine() {
            const svg = document.getElementById('zigzagSvg');
            const wrapper = document.getElementById('chartWrapper');
            if (!svg || !wrapper) return;
            
            svg.setAttribute('width', wrapper.scrollWidth);
            svg.setAttribute('height', wrapper.scrollHeight);
            
            let points = [];
            const activeCircles = wrapper.querySelectorAll('.t-num-circle.active');
            
            activeCircles.forEach(circle => {
                const rect = circle.getBoundingClientRect();
                const wrapperRect = wrapper.getBoundingClientRect();
                let x = rect.left + rect.width / 2 - wrapperRect.left + wrapper.scrollLeft;
                let y = rect.top + rect.height / 2 - wrapperRect.top + wrapper.scrollTop;
                points.push(`${x},${y}`);
            });
            
            if (points.length > 1) {
                svg.innerHTML = `<polyline points="${points.join(' ')}" fill="none" stroke="#e74c3c" stroke-width="2" stroke-linejoin="round" />`;
            }
        }

        function updateLogUI() {
            const listEl = document.getElementById('logList');
            if (historyLogs.length === 0) {
                listEl.innerHTML = '<div style="text-align:center; color:#777; padding:20px;">Waiting for real round completion...</div>';
                return;
            }
            let html = '';
            historyLogs.forEach(log => {
                let badge = log.status === 'WIN' ? '<span class="badge-win">WIN ✅</span>' :
                            log.status === 'JACKPOT' ? '<span class="badge-win" style="color:#ffcc00; background:rgba(255,204,0,0.1);">JACKPOT 🌟</span>' :
                            '<span class="badge-loss">LOSS ❌</span>';
                let actColor = log.act_type === 'BIG' ? '#00ff88' : '#ff4444';
                html += `
                <div class="log-item">
                    <div>
                        <div style="color:#aaa; font-size:9px;">Period: ${log.issue}</div>
                        <div style="color:#fff; font-weight:bold;">Pred: ${log.pred} | Actual: <span style="color:${actColor}">${log.act_type} (${log.act_num})</span></div>
                    </div>
                    <div>${badge}</div>
                </div>`;
            });
            listEl.innerHTML = html;
        }

        function updateClock() {
            const now = new Date();
            let hours = now.getHours();
            let minutes = now.getMinutes();
            let seconds = now.getSeconds();
            let ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            minutes = minutes < 10 ? '0' + minutes : minutes;
            seconds = seconds < 10 ? '0' + seconds : seconds;
            document.getElementById('currentTime').innerText = `${hours}:${minutes}:${seconds} ${ampm}`;
            
            let d = String(now.getDate()).padStart(2, '0');
            let m = String(now.getMonth() + 1).padStart(2, '0');
            let y = now.getFullYear();
            document.getElementById('currentDate').innerText = `${d}/${m}/${y}`;
        }
        setInterval(updateClock, 1000);
        updateClock();

        function updateTimer() {
            const now = new Date();
            let sec = now.getSeconds();
            let remaining = 60 - sec;
            if (remaining > 60) remaining = 60;
            let formatted = remaining < 10 ? '0' + remaining : remaining;
            document.getElementById('timer').innerText = `00:${formatted}`;
            
            // Period updates in real-time every second driven by live UTC clock
            document.getElementById('periodVal').innerText = getLiveUTCPeriod();

            if (remaining === 59 || remaining === 0) {
                fetchLotteryData();
            }
        }
        setInterval(updateTimer, 1000);
        updateTimer();

        // Initial calls
        document.getElementById('periodVal').innerText = getLiveUTCPeriod();
        fetchLotteryData();
        setInterval(fetchLotteryData, 3000);
    </script>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        key = request.form.get('license_key', '').strip().upper()
        if not key:
            error = 'Please enter a valid License Key!'
        else:
            if db:
                try:
                    doc_ref = db.collection('trustwin_keys').document(key)
                    doc = doc_ref.get()
                    if doc.exists:
                        data = doc.to_dict()
                        if data.get('isExpired', False):
                            error = '❌ Ye Trust Win Key Expire ho chuki hai!'
                        else:
                            session['authenticated'] = True
                            session['active_key'] = key
                            return redirect(url_for('home'))
                    else:
                        error = '❌ Trust Win ki galat Key hai!'
                except Exception as e:
                    error = f'Database Error: {str(e)}'
            else:
                error = 'Database connection error on server.'
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    session.pop('active_key', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
