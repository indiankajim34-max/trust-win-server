from flask import Flask, render_template_string, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'trustwin_ultimate_secret_key_2026'

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trust Win VIP - Login</title>
    <style>
        body { background-color: #080808; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; height: 100vh; }
        .login-card { background: linear-gradient(145deg, #121212, #1a1a1a); border: 2px solid #d4af37; border-radius: 20px; padding: 25px; width: 100%; max-width: 350px; box-shadow: 0 0 30px rgba(212, 175, 55, 0.4); }
        .title { font-size: 18px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
        .sub { font-size: 11px; color: #888; margin-bottom: 20px; }
        .input-box { width: 100%; padding: 12px; background: #161616; border: 1px solid #444; border-radius: 10px; color: #fff; font-size: 14px; text-align: center; margin-bottom: 15px; box-sizing: border-box; outline: none; }
        .input-box:focus { border-color: #d4af37; box-shadow: 0 0 10px rgba(212, 175, 55, 0.3); }
        .btn { background: linear-gradient(45deg, #d4af37, #ffdf73); color: #000; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(212,175,55,0.4); }
        .error { color: #ff4444; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="title">👑 TRUST WIN VIP 👑</div>
        <div class="sub">ENTER CREDENTIALS TO UNLOCK</div>
        <form method="POST">
            <input type="text" name="username" class="input-box" placeholder="Username (trustwin)" required autocomplete="off">
            <input type="password" name="password" class="input-box" placeholder="Password (trust143)" required autocomplete="off">
            <button type="submit" class="btn">LOGIN TO RADAR</button>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            0% { box-shadow: 0 0 10px rgba(0,255,136,0.3); }
            50% { box-shadow: 0 0 25px rgba(0,255,136,0.8); }
            100% { box-shadow: 0 0 10px rgba(0,255,136,0.3); }
        }
        @keyframes text-flash {
            0% { opacity: 0.3; }
            50% { opacity: 1; color: #00ff88; text-shadow: 0 0 15px #00ff88; }
            100% { opacity: 0.3; }
        }
        body { background-color: #0c0c0c; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 8px; }
        .container { max-width: 410px; margin: auto; background: linear-gradient(145deg, #121212, #181818); border: 2px solid #d4af37; border-radius: 20px; padding: 12px; animation: glow 4s infinite ease-in-out; position: relative; padding-bottom: 75px; min-height: 600px; box-sizing: border-box; }
        
        .top-banner { background: #181818; border: 1px solid #333; border-radius: 14px; padding: 10px; margin-bottom: 8px; }
        .vip-header { display: flex; justify-content: space-between; align-items: center; font-size: 12px; font-weight: bold; color: #d4af37; border-bottom: 1px solid #282828; padding-bottom: 6px; margin-bottom: 6px; }
        .live-dot { height: 8px; width: 8px; background-color: #00ff88; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #00ff88; }
        
        .main-title { font-size: 16px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
        .sub-engine { font-size: 10px; color: #888; margin-top: 2px; letter-spacing: 0.5px; }
        .time-row { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-top: 6px; padding: 0 4px; }

        .huge-last-result { background: linear-gradient(145deg, #161616, #202020); border: 2px solid #ffdf73; border-radius: 12px; padding: 10px; margin: 8px 0; box-shadow: 0 0 15px rgba(255,223,115,0.2); }
        .huge-last-title { font-size: 10px; color: #ffdf73; font-weight: bold; letter-spacing: 1.5px; margin-bottom: 4px; }
        .huge-last-val { font-size: 18px; font-weight: bold; color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.5); letter-spacing: 0.5px; }

        .host-box { background: #161616; border: 1px solid #333; border-radius: 10px; padding: 8px 12px; margin: 8px 0; display: flex; justify-content: space-between; align-items: center; font-size: 11px; }
        .host-left { text-align: left; }
        .host-right { text-align: right; color: #00ff88; font-weight: bold; }

        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin: 8px 0; }
        .stat-card { background: #181818; border: 1px solid #333; padding: 8px 4px; border-radius: 10px; }
        .stat-card .lbl { font-size: 9px; color: #888; }
        .stat-card .val { font-size: 15px; font-weight: bold; color: #fff; margin-top: 2px; display: block; }

        .period-box { background: #161616; border: 1px solid #333; border-radius: 10px; padding: 10px; margin: 8px 0; display: flex; justify-content: space-between; align-items: center; }
        .period-box div { text-align: left; font-size: 11px; color: #aaa; }
        .period-box span { font-size: 14px; font-weight: bold; color: #fff; display: block; letter-spacing: 0.5px; }
        .countdown { font-size: 18px !important; font-weight: bold; color: #ffcc00 !important; font-family: monospace; }

        .guard-banner { background: rgba(212, 175, 55, 0.08); border: 1px dashed #d4af37; border-radius: 8px; padding: 6px; font-size: 11px; font-weight: bold; color: #d4af37; margin: 8px 0; letter-spacing: 0.5px; }

        .radar-box { background: #141414; border: 1px solid #333; border-radius: 14px; padding: 15px 10px; margin-top: 8px; position: relative; overflow: hidden; }
        .radar-title { font-size: 10px; color: #777; letter-spacing: 1px; }
        .radar-sub { font-size: 9px; color: #aaa; margin-top: 2px; }
        
        .radar-circle-wrap { width: 140px; height: 140px; margin: 12px auto; border: 1px dashed rgba(212,175,55,0.4); border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; animation: radar-pulse 3s infinite ease-in-out; }
        .radar-circle-inner { width: 95px; height: 95px; border: 1px solid rgba(212,175,55,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; text-align: center; padding: 5px; }
        .prediction-display { font-size: 19px; font-weight: bold; color: #00ff88; text-shadow: 0 0 12px rgba(0,255,136,0.6); }
        .analyzing-text { font-size: 11px; font-weight: bold; color: #00ff88; animation: text-flash 1s infinite; line-height: 1.3; }

        .reveal-btn { background: linear-gradient(45deg, #00ff88, #00cc66); color: #000; border: none; width: 100%; padding: 13px; font-size: 14px; font-weight: bold; border-radius: 30px; cursor: pointer; margin-top: 10px; animation: btn-glow 2s infinite; transition: 0.2s; }
        .reveal-btn:active { transform: scale(0.96); }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .log-list { max-height: 280px; overflow-y: auto; text-align: left; font-size: 11px; margin-top: 10px; }
        .log-item { background: #161616; border: 1px solid #333; border-radius: 8px; padding: 8px 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
        .badge-win { color: #00ff88; font-weight: bold; background: rgba(0,255,136,0.1); padding: 2px 6px; border-radius: 4px; }
        .badge-loss { color: #ff4444; font-weight: bold; background: rgba(255,68,68,0.1); padding: 2px 6px; border-radius: 4px; }

        .profile-card { background: #161616; border: 1px solid #333; border-radius: 12px; padding: 15px; margin-top: 15px; text-align: left; font-size: 12px; }
        .profile-card p { margin: 8px 0; color: #bbb; }
        .profile-card span { color: #fff; font-weight: bold; }

        .bottom-nav { position: absolute; bottom: 0; left: 0; right: 0; background: #111; border-top: 1px solid #333; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; display: grid; grid-template-columns: repeat(4, 1fr); padding: 8px 0; }
        .nav-item { font-size: 10px; color: #888; cursor: pointer; transition: 0.2s; text-decoration: none; }
        .nav-item.active { color: #d4af37; font-weight: bold; }
        .nav-item div { font-size: 14px; margin-bottom: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-banner">
            <div class="vip-header">
                <span>👑 TRUST WIN VIP</span>
                <span><span class="live-dot"></span> DIRECT WORKER LIVE</span>
            </div>
            <div class="main-title">🍁 TRUST WIN 🍁</div>
            <div class="sub-engine">WINGO 1M DIRECT PROXY ENGINE</div>
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
                <div style="font-size:9px; color:#888;">HOST: RENDER NODE</div>
                <div style="font-size:10px; color:#ccc;">DIRECT CLIENT SYNC</div>
            </div>
            <div class="host-right">
                <div style="font-size:9px; color:#888;">PING</div>
                <div>12 ms</div>
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
                <b id="periodVal" style="color:#fff; font-size:12px;">Syncing Live...</b>
            </div>
            <div style="text-align: right;">
                <span>NEXT SIGNAL IN</span>
                <div class="countdown" id="timer">00:45</div>
            </div>
        </div>

        <div class="guard-banner">
            🛡️ DIRECT WORKER PROXY SYNCHRONIZED
        </div>

        <!-- TERMINAL TAB -->
        <div id="tab-terminal" class="tab-content active">
            <div class="radar-box">
                <div class="radar-title">AI ORACLE RADAR TERMINAL</div>
                <div class="radar-sub">MOMENTUM RIDER & WORKER PROXY</div>
                
                <div class="radar-circle-wrap">
                    <div class="radar-circle-inner" id="radarInner">
                        <div class="prediction-display" id="predDisplay">
                            🔒 LOCKED
                        </div>
                    </div>
                </div>

                <button type="button" class="reveal-btn" id="revealBtn" onclick="revealPrediction()">🎯 CHECK NEXT RESULT (REVEAL)</button>
            </div>
        </div>

        <!-- LOG TAB -->
        <div id="tab-log" class="tab-content">
            <div class="radar-box" style="text-align: left;">
                <div class="radar-title" style="text-align: center; margin-bottom: 8px;">📜 REAL HISTORY LOG</div>
                <div class="log-list" id="logList">
                    <div style="text-align:center; color:#777; padding:20px;">Waiting for real round completion...</div>
                </div>
            </div>
        </div>

        <!-- STATS TAB -->
        <div id="tab-stats" class="tab-content">
            <div class="radar-box">
                <div class="radar-title">📊 PERFORMANCE METRICS</div>
                <div style="background:#161616; border-radius:10px; padding:12px; margin-top:10px; text-align:left; font-size:12px;">
                    <p style="display:flex; justify-content:space-between; margin:6px 0;"><span>Total Rounds:</span> <b id="statTotal2" style="color:#fff;">0</b></p>
                    <p style="display:flex; justify-content:space-between; margin:6px 0;"><span>Real Accuracy:</span> <b id="statAccuracy" style="color:#00ff88;">0.0%</b></p>
                    <p style="display:flex; justify-content:space-between; margin:6px 0;"><span>Engine Status:</span> <b style="color:#00ff88;">Direct Worker Proxy Active</b></p>
                </div>
            </div>
        </div>

        <!-- PROFILE TAB -->
        <div id="tab-profile" class="tab-content">
            <div class="radar-box" style="text-align: left;">
                <div class="radar-title" style="text-align: center;">👑 USER PROFILE</div>
                <div class="profile-card">
                    <p>Username: <span>trustwin</span></p>
                    <p>License Status: <span style="color:#00ff88;">Active VIP (Lifetime)</span></p>
                    <p>Server Connected: <span>Cloud Dedicated Node</span></p>
                    <br>
                    <a href="/logout" style="display:block; text-align:center; background:#ff4444; color:#000; text-decoration:none; padding:10px; border-radius:8px; font-weight:bold;">LOGOUT ACCOUNT</a>
                </div>
            </div>
        </div>

        <!-- BOTTOM NAV -->
        <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('terminal', this)">
                <div>📈</div>TERMINAL
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
            const btn = document.getElementById('revealBtn');
            btn.disabled = true;
            btn.style.opacity = "0.5";

            inner.innerHTML = '<div class="analyzing-text">👑 TRUST WIN<br>ANALYSING...<br>[WORKER SCANNING]</div>';

            setTimeout(() => {
                isRevealed = true;
                inner.innerHTML = `<div class="prediction-display">${currentPredType} : ${currentPredNum}</div>`;
                btn.style.opacity = "1";
                btn.disabled = false;
            }, 3000);
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
                        document.getElementById('radarInner').innerHTML = '<div class="prediction-display" id="predDisplay">🔒 LOCKED</div>';
                    }

                    const nextPeriod = String(parseInt(actIssue, 10) + 1);
                    document.getElementById('periodVal').innerText = nextPeriod;

                    const recentNumbers = items.slice(0, 20).map(x => parseInt(x.number, 10));
                    const recentTypes = recentNumbers.map(n => n >= 5 ? "BIG" : "SMALL");
                    
                    let streakCount = 1;
                    for (let i = 1; i < recentTypes.length; i++) {
                        if (recentTypes[i] === recentTypes[0]) streakCount++;
                        else break;
                    }

                    let predT = streakCount >= 6 ? (recentTypes[0] === "BIG" ? "SMALL" : "BIG") : recentTypes[0];
                    let subPool = predT === "BIG" ? [5, 6, 7, 8, 9] : [0, 1, 2, 3, 4];
                    let seedVal = (parseInt(actIssue, 10) + recentNumbers[0]) % subPool.length;
                    let predN = subPool[seedVal];

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
                        <div style="color:#aaa; font-size:10px;">Period: ${log.issue}</div>
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
        }
        setInterval(updateTimer, 1000);
        updateTimer();

        fetchLotteryData();
        setInterval(fetchLotteryData, 8000);
    </script>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == 'trustwin' and pwd == 'trust143':
            session['authenticated'] = True
            return redirect(url_for('home'))
        else:
            error = 'Invalid Username or Password!'
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
