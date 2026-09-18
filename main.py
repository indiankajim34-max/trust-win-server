from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta

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
            0% { transform: scale(0.95); opacity: 0.85; box-shadow: 0 0 15px #00ff88, inset 0 0 10px #00ff88; }
            50% { transform: scale(1.03); opacity: 1; box-shadow: 0 0 30px #00ff88, inset 0 0 20px #00ff88; }
            100% { transform: scale(0.95); opacity: 0.85; box-shadow: 0 0 15px #00ff88, inset 0 0 10px #00ff88; }
        }
        @keyframes text-flash {
            0% { opacity: 0.4; }
            50% { opacity: 1; color: #00ff88; text-shadow: 0 0 15px #00ff88; }
            100% { opacity: 0.4; }
        }
        * { box-sizing: border-box; }
        body { background-color: #0c0c0c; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 4px; overflow: hidden; position: fixed; width: 100%; height: 100%; }
        .container { max-width: 420px; height: 100%; margin: auto; background: linear-gradient(145deg, #121212, #181818); border: 2px solid #d4af37; border-radius: 16px; padding: 6px 6px 48px 6px; animation: glow 4s infinite ease-in-out; position: relative; display: flex; flex-direction: column; overflow: hidden; }
        
        .top-banner { background: #181818; border: 1px solid #333; border-radius: 10px; padding: 5px; margin-bottom: 3px; flex-shrink: 0; }
        .vip-header { display: flex; justify-content: space-between; align-items: center; font-size: 9px; font-weight: bold; color: #d4af37; border-bottom: 1px solid #282828; padding-bottom: 2px; margin-bottom: 2px; }
        
        .main-title { font-size: 14px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
        .sub-engine { font-size: 8px; color: #888; margin-top: 1px; }
        .time-row { display: flex; justify-content: space-between; font-size: 9px; color: #aaa; margin-top: 2px; padding: 0 4px; }

        .huge-last-result { background: linear-gradient(145deg, #161616, #202020); border: 2px solid #ffdf73; border-radius: 8px; padding: 4px; margin: 3px 0; box-shadow: 0 0 10px rgba(255,223,115,0.2); flex-shrink: 0; }
        .huge-last-title { font-size: 8px; color: #ffdf73; font-weight: bold; letter-spacing: 1px; }
        .huge-last-val { font-size: 14px; font-weight: bold; color: #00ff88; text-shadow: 0 0 8px rgba(0,255,136,0.5); }

        .host-box { background: #161616; border: 1px solid #333; border-radius: 6px; padding: 3px 6px; margin: 2px 0; display: flex; justify-content: space-between; align-items: center; font-size: 8px; flex-shrink: 0; }
        .host-left { text-align: left; }
        .host-right { text-align: right; color: #00ff88; font-weight: bold; }

        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3px; margin: 2px 0; flex-shrink: 0; }
        .stat-card { background: #181818; border: 1px solid #333; padding: 3px 1px; border-radius: 6px; }
        .stat-card .lbl { font-size: 7px; color: #888; }
        .stat-card .val { font-size: 11px; font-weight: bold; color: #fff; margin-top: 1px; display: block; }

        .period-box { background: #161616; border: 1px solid #333; border-radius: 6px; padding: 4px 6px; margin: 2px 0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
        .period-box div { text-align: left; font-size: 8px; color: #aaa; }
        .period-box span { font-size: 11px; font-weight: bold; color: #fff; display: block; }
        .countdown { font-size: 14px !important; font-weight: bold; color: #ffcc00 !important; font-family: monospace; }

        /* TAB CONTENT & SPLIT CONTAINER */
        .tab-content { display: none; height: 100%; flex-direction: column; flex-grow: 1; overflow: hidden; }
        .tab-content.active { display: flex; }

        .terminal-split-container { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top: 3px; flex-grow: 1; min-height: 0; }
        
        /* LEFT VIP PREDICTOR CARD (As Per Screenshot) */
        .predictor-box { background: #080e0a; border: 1px solid #00ff8866; border-radius: 10px; padding: 5px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; position: relative; box-shadow: 0 0 15px rgba(0,255,136,0.12); }
        .wings-banner { background: linear-gradient(90deg, transparent, #00ff8822, transparent); border: 1px solid #ffcc00; border-radius: 12px; padding: 3px 6px; color: #ffcc00; font-size: 8px; font-weight: bold; letter-spacing: 1px; width: 92%; margin-top: 1px; }
        
        .glowing-pedestal { width: 115px; height: 115px; border-radius: 50%; border: 3px solid #00ff88; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(0,255,136,0.25) 0%, transparent 75%); animation: radar-pulse 3s infinite ease-in-out; margin: auto; cursor: pointer; }
        .leaf-icon { font-size: 18px; color: #00ff88; margin-bottom: 2px; }
        .prediction-display { font-size: 15px; font-weight: 900; color: #00ff88; text-shadow: 0 0 10px #00ff88; text-align: center; }
        .analyzing-text { font-size: 8px; font-weight: bold; color: #00ff88; animation: text-flash 1s infinite; line-height: 1.2; text-align: center; }
        .winner-badge { background: linear-gradient(45deg, #111, #222); border: 1px solid #ffcc00; color: #ffcc00; border-radius: 8px; padding: 3px 8px; font-size: 8px; font-weight: bold; width: 85%; margin-bottom: 2px; }

        /* RIGHT CALCULATOR CARD (Simplified Numpad + Save Invest) */
        .calc-box { background: #0a0d12; border: 1px solid #00a2ff66; border-radius: 10px; padding: 5px; display: flex; flex-direction: column; justify-content: space-between; font-size: 9px; }
        .calc-header { display: flex; justify-content: space-between; align-items: center; color: #00a2ff; font-weight: bold; font-size: 8px; margin-bottom: 2px; }
        .calc-display { background: #000; border: 1px solid #333; border-radius: 4px; color: #00ff88; font-size: 12px; font-weight: bold; text-align: right; padding: 3px 6px; margin-bottom: 3px; min-height: 22px; word-break: break-all; }
        
        .calc-pad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; margin-bottom: 3px; }
        .calc-btn { background: #141922; border: 1px solid #222c3a; color: #fff; border-radius: 3px; padding: 4px 0; font-size: 9px; font-weight: bold; cursor: pointer; }
        .calc-btn:active { background: #00a2ff; color: #000; }
        .calc-btn.clr { background: #ff444422; color: #ff4444; border-color: #ff444488; }
        
        .save-invest-btn { background: linear-gradient(90deg, #00cc66, #00ff88); color: #000; border: none; border-radius: 4px; padding: 4px; font-size: 9px; font-weight: 900; cursor: pointer; margin-bottom: 3px; width: 100%; box-shadow: 0 0 8px rgba(0,255,136,0.4); }

        .summary-title { font-size: 7px; font-weight: bold; color: #aaa; text-align: left; margin-bottom: 2px; }
        .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }
        .sum-card { background: #10141c; border: 1px solid #1a2230; border-radius: 3px; padding: 2px; text-align: center; }
        .sum-lbl { font-size: 6px; color: #888; display: block; }
        .sum-val { font-size: 8px; font-weight: bold; color: #fff; }

        .reset-btn { background: #1a2230; color: #00a2ff; border: 1px solid #00a2ff66; border-radius: 4px; padding: 3px; font-size: 8px; font-weight: bold; cursor: pointer; margin-top: 2px; width: 100%; }

        /* BDG CHART STYLES */
        .chart-scroll-area { flex-grow: 1; overflow-y: auto; overflow-x: hidden; max-height: calc(100vh - 270px); position: relative; padding-right: 2px; margin-top: 3px; }
        .tiranga-row { background: #161616; border: 1px solid #333; border-radius: 5px; padding: 3px; margin-bottom: 3px; display: flex; justify-content: space-between; align-items: center; font-size: 8px; }
        .tiranga-period { color: #aaa; font-family: monospace; font-size: 7px; text-align: left; width: 60px; flex-shrink: 0; }
        .tiranga-nums { display: flex; gap: 2px; align-items: center; justify-content: space-between; flex-grow: 1; padding: 0 2px; }
        
        .t-num-circle { width: 15px; height: 15px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 7px; font-weight: bold; background: #1f1f1f; color: #555; border: 1px solid #333; }
        .t-num-circle.c-violet { background: #9b59b6 !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 4px #9b59b6; }
        .t-num-circle.c-green { background: #2ecc71 !important; color: #000 !important; border-color: #fff !important; box-shadow: 0 0 4px #2ecc71; }
        .t-num-circle.c-red { background: #e74c3c !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 4px #e74c3c; }

        .badge-big-bdg { background: #f1c40f; color: #000; padding: 1px 3px; border-radius: 2px; font-weight: bold; font-size: 7px; width: 15px; text-align: center; flex-shrink: 0; }
        .badge-small-bdg { background: #3498db; color: #fff; padding: 1px 3px; border-radius: 2px; font-weight: bold; font-size: 7px; width: 15px; text-align: center; flex-shrink: 0; }

        .log-list { flex-grow: 1; overflow-y: auto; text-align: left; font-size: 8px; margin-top: 3px; }
        .log-item { background: #161616; border: 1px solid #333; border-radius: 5px; padding: 4px; margin-bottom: 3px; display: flex; justify-content: space-between; align-items: center; }
        .badge-win { color: #00ff88; font-weight: bold; background: rgba(0,255,136,0.1); padding: 1px 3px; border-radius: 2px; }
        .badge-loss { color: #ff4444; font-weight: bold; background: rgba(255,68,68,0.1); padding: 1px 3px; border-radius: 2px; }

        .profile-card { background: #161616; border: 1px solid #333; border-radius: 8px; padding: 8px; margin-top: 6px; text-align: left; font-size: 9px; }
        .profile-card p { margin: 4px 0; color: #bbb; }
        .profile-card span { color: #fff; font-weight: bold; }

        /* FIXED & RAISED BOTTOM NAVIGATION BAR (Shifted UP to avoid back/home gesture bar) */
        .bottom-nav { position: absolute; bottom: 12px; left: 0; right: 0; background: #111; border-top: 1px solid #333; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; display: grid; grid-template-columns: repeat(5, 1fr); padding: 5px 0 8px 0; z-index: 20; box-shadow: 0 -4px 10px rgba(0,0,0,0.8); }
        .nav-item { font-size: 7px; color: #888; cursor: pointer; transition: 0.2s; text-decoration: none; }
        .nav-item.active { color: #d4af37; font-weight: bold; }
        .nav-item div { font-size: 11px; margin-bottom: 1px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-banner">
            <div class="vip-header">
                <span>👑 TRUST WIN VIP</span>
                <span>🔑 KEY: <span style="color:#00ff88;">ACTIVE</span> (<span id="keyTimer" style="color:#ffdf73;">Syncing...</span>)</span>
            </div>
            <div class="main-title">🍁 TRUST WIN 🍁</div>
            <div class="sub-engine">300-RESULTS SEQUENTIAL PATTERN ENGINE</div>
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
                <div style="font-size:7px; color:#888;">PERIOD SYNC</div>
                <div style="font-size:8px; color:#ccc;">UTC CLOCK STRICT +1</div>
            </div>
            <div class="host-right" style="color:#00ff88;">
                <div style="font-size:7px; color:#888;">ZIGZAG LINE</div>
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
                <b id="periodVal" style="color:#fff; font-size:10px;">Syncing...</b>
            </div>
            <div style="text-align: right;">
                <span>NEXT SIGNAL IN</span>
                <div class="countdown" id="timer">00:60</div>
            </div>
        </div>

        <!-- TERMINAL TAB -->
        <div id="tab-terminal" class="tab-content active">
            <div class="terminal-split-container">
                <!-- LEFT VIP PREDICTOR CARD -->
                <div class="predictor-box">
                    <div class="wings-banner">👑 CHECK RESULT 👑</div>
                    
                    <div class="glowing-pedestal" onclick="revealPrediction()">
                        <div class="leaf-icon">🍁</div>
                        <div class="prediction-display" id="predDisplay">🔒 LOCKED</div>
                    </div>

                    <div class="winner-badge">👑 WINNER 👑</div>
                </div>

                <!-- RIGHT CALCULATOR & INVEST SUMMARY CARD -->
                <div class="calc-box">
                    <div class="calc-header">
                        <span>🧮 AMOUNT CALCULATOR</span>
                        <span style="cursor:pointer;" onclick="clearCalc()" title="Clear">🔄</span>
                    </div>
                    <div class="calc-display" id="calcDisplay">0</div>

                    <div class="calc-pad">
                        <button class="calc-btn" onclick="pressCalc('7')">7</button>
                        <button class="calc-btn" onclick="pressCalc('8')">8</button>
                        <button class="calc-btn" onclick="pressCalc('9')">9</button>

                        <button class="calc-btn" onclick="pressCalc('4')">4</button>
                        <button class="calc-btn" onclick="pressCalc('5')">5</button>
                        <button class="calc-btn" onclick="pressCalc('6')">6</button>

                        <button class="calc-btn" onclick="pressCalc('1')">1</button>
                        <button class="calc-btn" onclick="pressCalc('2')">2</button>
                        <button class="calc-btn" onclick="pressCalc('3')">3</button>

                        <button class="calc-btn" onclick="pressCalc('0')">0</button>
                        <button class="calc-btn" onclick="pressCalc('.')">.</button>
                        <button class="calc-btn clr" onclick="clearCalc()">⌫</button>
                    </div>

                    <button class="save-invest-btn" onclick="saveInvestAmount()">💾 SAVE INVEST AMOUNT</button>

                    <div class="summary-title">📊 PROFIT / LOSS SUMMARY</div>
                    <div class="summary-grid">
                        <div class="sum-card"><span class="sum-lbl">TOTAL INVEST</span><span class="sum-val" style="color:#00a2ff;" id="totInvest">₹ 0</span></div>
                        <div class="sum-card"><span class="sum-lbl">TOTAL RETURN</span><span class="sum-val" style="color:#00ff88;" id="totReturn">₹ 0</span></div>
                        <div class="sum-card"><span class="sum-lbl">TOTAL PROFIT</span><span class="sum-val" style="color:#00ff88;" id="totProfit">₹ 0</span></div>
                        <div class="sum-card"><span class="sum-lbl">TOTAL LOSS</span><span class="sum-val" style="color:#ff4444;" id="totLoss">₹ 0</span></div>
                    </div>

                    <button class="reset-btn" onclick="resetSummary()">🔄 RESET STATS</button>
                </div>
            </div>
        </div>

        <!-- PATTERN TAB -->
        <div id="tab-pattern" class="tab-content">
            <div style="background:#141414; border:1px solid #333; border-radius:8px; padding:5px; display:block; height:100%;">
                <div style="font-size:9px; color:#aaa; text-align:center; margin-bottom:2px;">📊 BDG CHART & ZIGZAG TREND</div>
                <div style="font-size:8px; color:#777; text-align:center; margin-bottom:3px;">EXACT COLOR MAPPING & ALIGNED LINE</div>
                <div class="chart-scroll-area" id="tirangaPatternList">
                    <div style="text-align:center; color:#777; padding:20px;">Loading BDG Chart Data...</div>
                </div>
            </div>
        </div>

        <!-- LOG TAB -->
        <div id="tab-log" class="tab-content">
            <div style="background:#141414; border:1px solid #333; border-radius:8px; padding:5px; display:block; height:100%;">
                <div style="font-size:9px; color:#aaa; text-align:center; margin-bottom:3px;">📜 REAL HISTORY LOG</div>
                <div class="log-list" id="logList">
                    <div style="text-align:center; color:#777; padding:20px;">Waiting for real round completion...</div>
                </div>
            </div>
        </div>

        <!-- STATS TAB -->
        <div id="tab-stats" class="tab-content">
            <div style="background:#141414; border:1px solid #333; border-radius:8px; padding:6px; display:block;">
                <div style="font-size:9px; color:#aaa; margin-bottom:4px;">📊 PERFORMANCE METRICS</div>
                <div style="background:#161616; border-radius:6px; padding:6px; text-align:left; font-size:9px;">
                    <p style="display:flex; justify-content:space-between; margin:3px 0;"><span>Total Rounds:</span> <b id="statTotal2" style="color:#fff;">0</b></p>
                    <p style="display:flex; justify-content:space-between; margin:3px 0;"><span>Real Accuracy:</span> <b id="statAccuracy" style="color:#00ff88;">0.0%</b></p>
                    <p style="display:flex; justify-content:space-between; margin:3px 0;"><span>Engine Status:</span> <b style="color:#00ff88;">300-Result Transition Engine Active</b></p>
                </div>
            </div>
        </div>

        <!-- PROFILE TAB -->
        <div id="tab-profile" class="tab-content">
            <div style="background:#141414; border:1px solid #333; border-radius:8px; padding:6px; text-align:left;">
                <div style="font-size:9px; color:#aaa; text-align:center; margin-bottom:4px;">👑 USER PROFILE</div>
                <div class="profile-card">
                    <p>Active Key: <span style="color:#00ff88;">{{ session.get('active_key', 'N/A') }}</span></p>
                    <p>License Status: <span style="color:#00ff88;">Active VIP</span></p>
                    <p>Time Remaining: <span id="profileKeyTimer" style="color:#ffdf73;">Calculating...</span></p>
                    <p>Server Connected: <span>Cloud Dedicated Node</span></p>
                    <br>
                    <a href="/logout" style="display:block; text-align:center; background:#ff4444; color:#000; text-decoration:none; padding:5px; border-radius:4px; font-weight:bold;">LOGOUT ACCOUNT</a>
                </div>
            </div>
        </div>

        <!-- 5-ITEM RAISED BOTTOM NAV (NO OVERLAP WITH BACK BUTTON) -->
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
        const KEY_EXPIRE_ISO = "{{ session.get('key_expire_iso', '') }}";

        let totalRounds = 0;
        let winsCount = 0;
        let lossesCount = 0;
        let jackpotsCount = 0;
        let historyLogs = [];
        let isRevealed = false;
        let currentPredType = "WAITING";
        let currentPredNum = 0;
        let lastEvaluatedIssue = null;

        // CALCULATOR & INVEST TRACKER LOGIC
        let calcExpr = "";
        let pendingBetAmount = 0;
        let totalInvest = 0;
        let totalReturn = 0;
        let totalProfit = 0;
        let totalLoss = 0;

        function pressCalc(val) {
            if (calcExpr === "0") calcExpr = "";
            calcExpr += val;
            document.getElementById('calcDisplay').innerText = calcExpr || "0";
        }

        function clearCalc() {
            calcExpr = "";
            document.getElementById('calcDisplay').innerText = "0";
        }

        function saveInvestAmount() {
            let amt = parseFloat(calcExpr);
            if (!isNaN(amt) && amt > 0) {
                pendingBetAmount += amt;
                totalInvest += amt;
                document.getElementById('totInvest').innerText = `₹ ${totalInvest}`;
                clearCalc();
            }
        }

        function resetSummary() {
            pendingBetAmount = 0;
            totalInvest = 0;
            totalReturn = 0;
            totalProfit = 0;
            totalLoss = 0;
            document.getElementById('totInvest').innerText = "₹ 0";
            document.getElementById('totReturn').innerText = "₹ 0";
            document.getElementById('totProfit').innerText = "₹ 0";
            document.getElementById('totLoss').innerText = "₹ 0";
            clearCalc();
        }

        // DYNAMIC LICENSE KEY TIMER WITH AUTO-LOGOUT
        function updateRealKeyTimer() {
            let labelText = "VIP ACTIVE";
            if (KEY_EXPIRE_ISO && KEY_EXPIRE_ISO !== "" && KEY_EXPIRE_ISO !== "None") {
                const expireDate = new Date(KEY_EXPIRE_ISO);
                const now = new Date();
                const diffMs = expireDate - now;

                if (diffMs <= 0) {
                    labelText = "EXPIRED";
                    document.getElementById('keyTimer').innerText = labelText;
                    window.location.href = '/logout';
                    return;
                } else {
                    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    const secs = Math.floor((diffMs % (1000 * 60)) / 1000);

                    if (days > 0) {
                        labelText = `${days}d ${hours}h ${mins}m`;
                    } else if (hours > 0) {
                        labelText = `${hours}h ${mins}m ${secs}s`;
                    } else {
                        labelText = `${mins}m ${secs}s`;
                    }
                }
            } else {
                labelText = "UNLIMITED VIP";
            }
            document.getElementById('keyTimer').innerText = labelText;
            const profTimer = document.getElementById('profileKeyTimer');
            if (profTimer) profTimer.innerText = labelText;
        }
        setInterval(updateRealKeyTimer, 1000);
        updateRealKeyTimer();

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
            const inner = document.getElementById('predDisplay');
            inner.innerHTML = '<div class="analyzing-text">TRUST AI<br>ANALYSING...</div>';

            setTimeout(() => {
                isRevealed = true;
                inner.innerHTML = `${currentPredType} : ${currentPredNum}`;
            }, 2000);
        }

        function getLiveUTCPeriod() {
            const now = new Date();
            const yyyy = now.getUTCFullYear();
            const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
            const dd = String(now.getUTCDate()).padStart(2, '0');
            const hours = now.getUTCHours();
            const mins = now.getUTCMinutes();
            const totalMins = hours * 60 + mins;
            const serial = 10000 + totalMins + 1;
            return `${yyyy}${mm}${dd}1000${serial}`;
        }

        async function fetch300Results() {
            let combinedList = [];
            try {
                const res1 = await fetch(WORKER_URL + "?pageSize=100&pageNo=1");
                const data1 = await res1.json();
                if (data1 && data1.data && data1.data.list) {
                    combinedList = combinedList.concat(data1.data.list);
                }
            } catch(e) {}

            if (combinedList.length === 0) {
                try {
                    const resDef = await fetch(WORKER_URL);
                    const dataDef = await resDef.json();
                    if (dataDef && dataDef.data && dataDef.data.list) {
                        combinedList = dataDef.data.list;
                    }
                } catch(e) {}
            }

            if (combinedList.length > 0 && combinedList.length < 300) {
                try {
                    const res2 = await fetch(WORKER_URL + "?pageSize=100&pageNo=2");
                    const data2 = await res2.json();
                    if (data2 && data2.data && data2.data.list) combinedList = combinedList.concat(data2.data.list);
                    const res3 = await fetch(WORKER_URL + "?pageSize=100&pageNo=3");
                    const data3 = await res3.json();
                    if (data3 && data3.data && data3.data.list) combinedList = combinedList.concat(data3.data.list);
                } catch(e) {}
            }
            return combinedList;
        }

        async function fetchLotteryData() {
            try {
                const items = await fetch300Results();
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
                            jackpotsCount++; winsCount++; statusRes = "JACKPOT";
                        } else if (currentPredType === actType) {
                            winsCount++; statusRes = "WIN";
                        } else {
                            lossesCount++; statusRes = "LOSS";
                        }

                        // INVEST PROFIT/LOSS CALCULATION ON ROUND RESULT
                        if (pendingBetAmount > 0) {
                            if (statusRes === "WIN" || statusRes === "JACKPOT") {
                                let retVal = pendingBetAmount * 1.96;
                                totalReturn += retVal;
                                totalProfit += (retVal - pendingBetAmount);
                            } else {
                                totalLoss += pendingBetAmount;
                            }
                            pendingBetAmount = 0;
                            document.getElementById('totReturn').innerText = `₹ ${Math.round(totalReturn)}`;
                            document.getElementById('totProfit').innerText = `₹ ${Math.round(totalProfit)}`;
                            document.getElementById('totLoss').innerText = `₹ ${Math.round(totalLoss)}`;
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
                        document.getElementById('predDisplay').innerHTML = `🔒 LOCKED`;
                    }

                    updateBdgChartUI(items);

                    // 300-RESULT SEQUENTIAL TRANSITION + FULL DEEP FALLBACK ENGINE
                    const analysisPool = items.slice(0, 300);
                    const lastNum = parseInt(items[0].number, 10);
                    const lastType = lastNum >= 5 ? "BIG" : "SMALL";

                    let nextNumFreq = {};
                    for (let i = 0; i <= 9; i++) nextNumFreq[i] = 0;
                    let nextBigCount = 0;
                    let nextSmallCount = 0;
                    let transitionMatches = 0;

                    for (let i = 0; i < analysisPool.length - 1; i++) {
                        let histPrevNum = parseInt(analysisPool[i + 1].number, 10);
                        let histNextNum = parseInt(analysisPool[i].number, 10);
                        
                        if (histPrevNum === lastNum) {
                            transitionMatches++;
                            nextNumFreq[histNextNum]++;
                            if (histNextNum >= 5) nextBigCount++;
                            else nextSmallCount++;
                        }
                    }

                    let predT = lastType;
                    let predN = 0;

                    if (transitionMatches >= 2) {
                        predT = nextBigCount >= nextSmallCount ? "BIG" : "SMALL";
                        let subPool = predT === "BIG" ? [5, 6, 7, 8, 9] : [0, 1, 2, 3, 4];
                        subPool.sort((a, b) => nextNumFreq[b] - nextNumFreq[a]);
                        predN = subPool[0];
                    } else {
                        let overallBig = 0, overallSmall = 0;
                        let overallDigitFreq = {};
                        for(let i=0; i<=9; i++) overallDigitFreq[i] = 0;

                        analysisPool.forEach(item => {
                            let n = parseInt(item.number, 10);
                            if (!isNaN(n)) {
                                overallDigitFreq[n]++;
                                if (n >= 5) overallBig++; else overallSmall++;
                            }
                        });

                        const recentTypes = analysisPool.slice(0, 10).map(x => parseInt(x.number, 10) >= 5 ? "BIG" : "SMALL");
                        let streak = 1;
                        for (let k = 1; k < recentTypes.length; k++) {
                            if (recentTypes[k] === recentTypes[0]) streak++; else break;
                        }

                        if (streak >= 4) {
                            predT = lastType === "BIG" ? "SMALL" : "BIG";
                        } else {
                            if (overallBig > overallSmall + 10) predT = "SMALL";
                            else if (overallSmall > overallBig + 10) predT = "BIG";
                            else predT = lastType;
                        }
                        let subPool = predT === "BIG" ? [5, 6, 7, 8, 9] : [0, 1, 2, 3, 4];
                        subPool.sort((a, b) => overallDigitFreq[a] - overallDigitFreq[b]);
                        predN = subPool[0];
                    }

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
                        <div style="color:#aaa; font-size:7px;">Period: ${log.issue}</div>
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
                            expire_iso = None
                            if 'expiresAt' in data and data['expiresAt']:
                                exp_val = data['expiresAt']
                                if hasattr(exp_val, 'isoformat'):
                                    expire_iso = exp_val.isoformat()
                                else:
                                    expire_iso = str(exp_val)
                            elif 'expire_time' in data and data['expire_time']:
                                expire_iso = str(data['expire_time'])
                            elif 'durationMinutes' in data or 'durationHours' in data or 'validDays' in data or 'createdAt' in data:
                                created_val = data.get('createdAt', datetime.now(timezone.utc))
                                if hasattr(created_val, 'timestamp'):
                                    base_ts = created_val.timestamp()
                                else:
                                    base_ts = datetime.now(timezone.utc).timestamp()
                                
                                add_secs = 0
                                if 'durationMinutes' in data: add_secs += int(data['durationMinutes']) * 60
                                elif 'durationHours' in data: add_secs += int(data['durationHours']) * 3600
                                else: add_secs += int(data.get('validDays', 30)) * 86400
                                
                                expire_iso = datetime.fromtimestamp(base_ts + add_secs, tz=timezone.utc).isoformat()

                            session['authenticated'] = True
                            session['active_key'] = key
                            session['key_expire_iso'] = expire_iso
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
    session.pop('key_expire_iso', None)
    return redirect(url_for('login'))

@app.route('/keepalive')
def keepalive():
    return "I am awake!", 200

@app.route('/')
def home():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
