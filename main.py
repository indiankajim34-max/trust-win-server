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
        @keyframes pulse-btn {
            0% { transform: scale(1); box-shadow: 0 0 10px rgba(0, 255, 136, 0.4); }
            50% { transform: scale(1.03); box-shadow: 0 0 20px rgba(0, 255, 136, 0.8); }
            100% { transform: scale(1); box-shadow: 0 0 10px rgba(0, 255, 136, 0.4); }
        }
        body { background-color: #080808; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }
        .login-card { background: linear-gradient(145deg, #121212, #1a1a1a); border: 2px solid #d4af37; border-radius: 20px; padding: 25px; width: 100%; max-width: 350px; box-shadow: 0 0 30px rgba(212, 175, 55, 0.4); }
        .title { font-size: 18px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
        .sub { font-size: 11px; color: #888; margin-bottom: 20px; }
        .input-box { width: 100%; padding: 12px; background: #161616; border: 1px solid #444; border-radius: 10px; color: #fff; font-size: 14px; text-align: center; margin-bottom: 15px; box-sizing: border-box; outline: none; text-transform: uppercase; font-weight: bold; }
        .input-box:focus { border-color: #d4af37; box-shadow: 0 0 10px rgba(212, 175, 55, 0.3); }
        .btn { background: linear-gradient(45deg, #d4af37, #ffdf73); color: #000; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(212,175,55,0.4); }
        .buy-btn { 
            display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 18px; padding: 12px; width: 100%; background: linear-gradient(45deg, #00c853, #00ff88); color: #000; font-size: 13px; font-weight: 900; text-decoration: none; border-radius: 10px; box-sizing: border-box; animation: pulse-btn 2s infinite ease-in-out; letter-spacing: 0.5px;
        }
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
        <a href="https://admin-panel-0mra.onrender.com/" target="_blank" class="buy-btn">🛒 BUY NEW VIP KEY 🔑</a>
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
    <title>Trust Win VIP AI Engine</title>
    <style>
        @keyframes glow {
            0% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.2); border-color: #d4af37; }
            50% { box-shadow: 0 0 30px rgba(212, 175, 55, 0.6); border-color: #ffdf73; }
            100% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.2); border-color: #d4af37; }
        }
        @keyframes radar-pulse {
            0% { transform: scale(0.95); opacity: 0.85; box-shadow: 0 0 15px #d4af37, inset 0 0 10px #d4af37; }
            50% { transform: scale(1.03); opacity: 1; box-shadow: 0 0 30px #ffdf73, inset 0 0 20px #ffdf73; }
            100% { transform: scale(0.95); opacity: 0.85; box-shadow: 0 0 15px #d4af37, inset 0 0 10px #d4af37; }
        }
        @keyframes casino-power-anim {
            0% { transform: scale(1); box-shadow: 0 0 20px #ffdf73; border-color: #ffdf73; }
            30% { transform: scale(1.08); box-shadow: 0 0 35px #ffcc00; border-color: #ffcc00; }
            60% { transform: scale(0.96); box-shadow: 0 0 45px #d4af37; border-color: #d4af37; }
            100% { transform: scale(1); box-shadow: 0 0 20px #ffdf73; border-color: #ffdf73; }
        }
        .pedestal-active-power { animation: casino-power-anim 0.25s infinite ease-in-out !important; }

        @keyframes win-flash-anim {
            0% { box-shadow: 0 0 20px rgba(0,255,136,0.25); border-color: #00ff88aa; }
            20% { box-shadow: 0 0 50px #00ff88, inset 0 0 40px #00ff88; border-color: #00ff88; transform: scale(1.02); }
            40% { box-shadow: 0 0 20px rgba(0,255,136,0.25); border-color: #00ff88aa; transform: scale(1); }
            60% { box-shadow: 0 0 50px #00ff88, inset 0 0 40px #00ff88; border-color: #00ff88; transform: scale(1.02); }
            100% { box-shadow: 0 0 20px rgba(0,255,136,0.25); border-color: #00ff88aa; transform: scale(1); }
        }
        .win-flash-active { animation: win-flash-anim 1.5s ease-in-out !important; }

        @keyframes pulse-warn {
            0% { transform: scale(1); box-shadow: 0 0 20px #ff3300; }
            50% { transform: scale(1.03); box-shadow: 0 0 40px #ff6600; }
            100% { transform: scale(1); box-shadow: 0 0 20px #ff3300; }
        }
        @keyframes text-flash {
            0% { opacity: 0.4; }
            50% { opacity: 1; color: #ffdf73; text-shadow: 0 0 15px #ffdf73; }
            100% { opacity: 0.4; }
        }

        /* NEW ANIMATIONS: WIN TOAST & JACKPOT */
        .win-toast { position: fixed; top: -100px; left: 50%; transform: translateX(-50%); background: linear-gradient(45deg, #00ff88, #009955); color: #000; padding: 12px 40px; border-radius: 30px; font-weight: 900; font-size: 18px; z-index: 10000; transition: top 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 5px 25px rgba(0,255,136,0.8); border: 2px solid #fff; letter-spacing: 1px; }
        .win-toast.show { top: 30px; }
        
        .jackpot-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 10001; align-items: center; justify-content: center; flex-direction: column; }
        .jackpot-text { font-size: 45px; font-weight: 900; background: linear-gradient(45deg, #ffcc00, #fff, #ffcc00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px #ffcc00; animation: casino-power-anim 0.5s infinite; text-align: center; line-height: 1.2; }
        .jackpot-sub { color: #fff; font-size: 18px; margin-top: 15px; font-weight: bold; letter-spacing: 2px; }

        * { box-sizing: border-box; }
        body { background-color: #0c0c0c; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 4px; overflow: hidden; position: fixed; width: 100%; height: 100%; }
        .container { max-width: 420px; height: 100%; margin: auto; background: linear-gradient(145deg, #121212, #181818); border: 2px solid #d4af37; border-radius: 16px; padding: 6px 6px 52px 6px; animation: glow 4s infinite ease-in-out; position: relative; display: flex; flex-direction: column; overflow: hidden; }
        
        .top-banner { background: #181818; border: 1px solid #333; border-radius: 10px; padding: 5px; margin-bottom: 3px; flex-shrink: 0; }
        .vip-header { display: flex; justify-content: space-between; align-items: center; font-size: 9px; font-weight: bold; color: #d4af37; border-bottom: 1px solid #282828; padding-bottom: 2px; margin-bottom: 2px; }
        .main-title { font-size: 14px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
        .sub-engine { font-size: 8px; color: #ffdf73; margin-top: 1px; font-weight: bold; }
        .time-row { display: flex; justify-content: space-between; font-size: 9px; color: #aaa; margin-top: 2px; padding: 0 4px; }

        .huge-last-result { background: linear-gradient(145deg, #161616, #202020); border: 2px solid #ffdf73; border-radius: 8px; padding: 4px; margin: 3px 0; box-shadow: 0 0 10px rgba(255,223,115,0.2); flex-shrink: 0; }
        .huge-last-title { font-size: 8px; color: #ffdf73; font-weight: bold; letter-spacing: 1px; }
        .huge-last-val { font-size: 14px; font-weight: bold; text-shadow: 0 0 8px rgba(255,255,255,0.3); }

        .host-box { background: #161616; border: 1px solid #333; border-radius: 6px; padding: 3px 6px; margin: 2px 0; display: flex; justify-content: space-between; align-items: center; font-size: 8px; flex-shrink: 0; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3px; margin: 2px 0; flex-shrink: 0; }
        .stat-card { background: #181818; border: 1px solid #333; padding: 3px 1px; border-radius: 6px; }
        .stat-card .lbl { font-size: 7px; color: #888; }
        .stat-card .val { font-size: 11px; font-weight: bold; color: #fff; margin-top: 1px; display: block; }

        .period-box { background: #161616; border: 1px solid #333; border-radius: 6px; padding: 4px 6px; margin: 2px 0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
        .period-box div { text-align: left; font-size: 8px; color: #aaa; }
        .period-box span { font-size: 11px; font-weight: bold; color: #fff; display: block; }
        .countdown { font-size: 14px !important; font-weight: bold; color: #ffcc00 !important; font-family: monospace; }

        .tab-content { display: none; height: 100%; flex-direction: column; flex-grow: 1; overflow: hidden; }
        .tab-content.active { display: flex; }

        .terminal-split-container { display: grid; grid-template-columns: 1fr 1.2fr; gap: 5px; margin-top: 3px; flex-grow: 1; min-height: 0; }
        
        /* GOLDEN PREDICTOR BOX */
        .predictor-box { 
            background: linear-gradient(135deg, #1a1400, #261e00, #140f00);
            border: 2px solid #d4af37; 
            border-radius: 10px; 
            padding: 5px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: space-between; 
            position: relative; 
            box-shadow: 0 0 20px rgba(212,175,55,0.25), inset 0 0 15px rgba(255,223,115,0.1); 
        }
        .wings-banner { background: linear-gradient(90deg, transparent, #d4af3755, transparent); border: 1px solid #ffcc00; border-radius: 12px; padding: 3px 6px; color: #ffcc00; font-size: 8px; font-weight: bold; letter-spacing: 1px; width: 92%; margin-top: 1px; }
        .glowing-pedestal { width: 110px; height: 110px; border-radius: 50%; border: 3px solid #d4af37; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(212,175,55,0.2) 0%, transparent 75%); animation: radar-pulse 3s infinite ease-in-out; margin: auto; cursor: pointer; transition: 0.2s; }
        .leaf-icon { font-size: 22px; margin-bottom: 2px; }
        .prediction-display { font-size: 16px; font-weight: 900; text-shadow: 0 0 10px rgba(255,255,255,0.3); text-align: center; }
        .analyzing-text { font-size: 8px; font-weight: bold; color: #ffdf73; animation: text-flash 0.5s infinite; line-height: 1.2; text-align: center; }
        
        /* NEW GOLDEN ENGINE STATUS BOX (Replaced Calculator) */
        .engine-status-box { background: linear-gradient(145deg, #1c1500, #0a0800); border: 2px solid #d4af37; border-radius: 10px; padding: 6px; display: flex; flex-direction: column; box-shadow: inset 0 0 15px rgba(212,175,55,0.1); }
        .engine-header { color: #ffcc00; font-weight: bold; font-size: 9px; text-align: center; border-bottom: 1px solid #d4af3755; padding-bottom: 4px; margin-bottom: 4px; letter-spacing: 1px; }
        .engine-row { display: flex; justify-content: space-between; align-items: center; background: #000; border: 1px solid #333; border-radius: 4px; padding: 4px 6px; margin-bottom: 3px; font-size: 8px; }
        .engine-row span { color: #aaa; }
        .final-vote { background: linear-gradient(90deg, #3a2a00, #000); border-color: #ffdf73; padding: 6px; font-size: 9px; margin-top: auto; }
        
        /* MULTIPLE COLORS */
        .color-green { color: #00ff88 !important; text-shadow: 0 0 8px rgba(0,255,136,0.6) !important; }
        .color-red { color: #ff4444 !important; text-shadow: 0 0 8px rgba(255,68,68,0.6) !important; }
        .color-violet { color: #c084fc !important; text-shadow: 0 0 8px rgba(192,132,252,0.6) !important; }
        .color-wait { color: #ffcc00 !important; }

        .chart-scroll-area { flex-grow: 1; overflow-y: auto; overflow-x: hidden; max-height: calc(100vh - 270px); position: relative; padding-right: 2px; margin-top: 3px; }
        .tiranga-row { background: #161616; border: 1px solid #333; border-radius: 5px; padding: 3px; margin-bottom: 3px; display: flex; justify-content: space-between; align-items: center; font-size: 8px; }
        .tiranga-period { color: #aaa; font-family: monospace; font-size: 7px; text-align: left; width: 60px; flex-shrink: 0; }
        .tiranga-nums { display: flex; gap: 2px; align-items: center; justify-content: space-between; flex-grow: 1; padding: 0 2px; }
        .t-num-circle { width: 15px; height: 15px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 7px; font-weight: bold; background: #1f1f1f; color: #555; border: 1px solid #333; }
        .t-num-circle.c-violet { background: #9b59b6 !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 4px #9b59b6; }
        .t-num-circle.c-green { background: #2ecc71 !important; color: #000 !important; border-color: #fff !important; box-shadow: 0 0 4px #2ecc71; }
        .t-num-circle.c-red { background: #e74c3c !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 4px #e74c3c; }

        .log-list { flex-grow: 1; overflow-y: auto; text-align: left; font-size: 8px; margin-top: 3px; }
        .log-item { background: #161616; border: 1px solid #333; border-radius: 5px; padding: 4px; margin-bottom: 3px; display: flex; justify-content: space-between; align-items: center; }
        .badge-win { color: #00ff88; font-weight: bold; background: rgba(0,255,136,0.1); padding: 1px 3px; border-radius: 2px; }
        .badge-loss { color: #ff4444; font-weight: bold; background: rgba(255,68,68,0.1); padding: 1px 3px; border-radius: 2px; }

        .profile-card { background: #161616; border: 1px solid #333; border-radius: 8px; padding: 8px; margin-top: 6px; text-align: left; font-size: 9px; }
        .profile-card p { margin: 4px 0; color: #bbb; }
        .profile-card span { color: #fff; font-weight: bold; }

        .bottom-nav { position: absolute; bottom: 14px; left: 0; right: 0; background: #111; border-top: 1px solid #333; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; display: grid; grid-template-columns: repeat(5, 1fr); padding: 6px 0 10px 0; z-index: 25; box-shadow: 0 -5px 12px rgba(0,0,0,0.85); }
        .nav-item { font-size: 7px; color: #888; cursor: pointer; transition: 0.2s; text-decoration: none; }
        .nav-item.active { color: #d4af37; font-weight: bold; }
        .nav-item div { font-size: 11px; margin-bottom: 1px; }
    </style>
</head>
<body>
    <!-- WIN TOAST -->
    <div id="winToast" class="win-toast">🏆 WINNER 🏆</div>

    <!-- JACKPOT OVERLAY -->
    <div id="jackpotOverlay" class="jackpot-overlay" onclick="this.style.display='none'">
        <div class="jackpot-text">🎉 MEGA JACKPOT 🎉</div>
        <div class="jackpot-sub">TAP TO CLOSE</div>
    </div>

    <!-- KEY EXPIRY WARNING MODAL -->
    <div id="keyWarnModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.88); z-index:9999; align-items:center; justify-content:center; padding:20px; box-sizing:border-box;">
        <div style="background:linear-gradient(145deg, #220000, #3d0000); border:3px solid #ff3300; border-radius:20px; padding:20px; text-align:center; max-width:320px; box-shadow:0 0 35px #ff3300; animation:pulse-warn 1.5s infinite;">
            <div style="font-size:38px; margin-bottom:5px;">⚠️</div>
            <div style="font-size:15px; font-weight:900; color:#ff3300; letter-spacing:1px; margin-bottom:8px;" id="warnTitle">VIP KEY EXPIRING SOON</div>
            <div style="font-size:12px; color:#fff; font-weight:bold; margin-bottom:15px; line-height:1.4;" id="warnBody">Your VIP key will expire shortly!</div>
            <button onclick="dismissWarnModal()" style="background:linear-gradient(45deg, #ff3300, #ff6600); color:#fff; border:none; padding:10px 20px; font-weight:900; border-radius:8px; cursor:pointer; font-size:12px; width:100%; letter-spacing:0.5px;">OK, UNDERSTOOD</button>
        </div>
    </div>

    <div class="container">
        <div class="top-banner">
            <div class="vip-header">
                <span>👑 TRUST WIN VIP</span>
                <span>🔑 KEY: <span style="color:#00ff88;">ACTIVE</span> (<span id="keyTimer" style="color:#ffdf73;">Syncing...</span>)</span>
            </div>
            <div class="main-title">🍁 TRUST WIN 🍁</div>
            <div class="sub-engine" id="engineStatusMsg">5-ENGINE MASTER AI ENSEMBLE</div>
            <div class="time-row">
                <span id="currentTime">--:--:-- PM</span>
                <span id="currentDate">--/--/----</span>
            </div>
        </div>

        <div class="huge-last-result">
            <div class="huge-last-title">🔥 LIVE WINGO RESULT TRACKER 🔥</div>
            <div class="huge-last-val" id="hugeResultVal">Connecting to Database...</div>
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
                <div class="predictor-box" id="predictorBox">
                    <div class="wings-banner">👑 CHECK RESULT 👑</div>
                    
                    <div class="glowing-pedestal" onclick="revealPrediction()">
                        <div class="leaf-icon">👑</div>
                        <div class="prediction-display color-wait" id="predDisplay">🔒 LOCKED</div>
                    </div>
                </div>

                <div class="engine-status-box">
                    <div class="engine-header">🤖 LIVE ENGINES (500-DATA)</div>
                    <div class="engine-row"><span>Opposite:</span> <b id="uiEng1">--</b></div>
                    <div class="engine-row"><span>Statistical:</span> <b id="uiEng2">--</b></div>
                    <div class="engine-row"><span>Psychology:</span> <b id="uiEng3">--</b></div>
                    <div class="engine-row"><span>Pattern:</span> <b id="uiEng4">--</b></div>
                    <div class="engine-row final-vote"><span>FINAL (MAJORITY):</span> <b id="uiEngFinal" style="font-size:10px;">--</b></div>
                </div>
            </div>
        </div>

        <!-- PATTERN TAB -->
        <div id="tab-pattern" class="tab-content">
            <div style="background:#141414; border:1px solid #333; border-radius:8px; padding:5px; display:block; height:100%;">
                <div style="font-size:9px; color:#aaa; text-align:center; margin-bottom:2px;">📊 BDG CHART & ZIGZAG TREND</div>
                <div class="chart-scroll-area" id="tirangaPatternList">
                    <div style="text-align:center; color:#777; padding:20px;">Loading Data...</div>
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
                    <br>
                    <a href="/logout" style="display:block; text-align:center; background:#ff4444; color:#000; text-decoration:none; padding:5px; border-radius:4px; font-weight:bold;">LOGOUT ACCOUNT</a>
                </div>
            </div>
        </div>

        <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('terminal', this)"><div>📈</div>TERMINAL</div>
            <div class="nav-item" onclick="switchTab('pattern', this)"><div>📊</div>PATTERN</div>
            <div class="nav-item" onclick="switchTab('log', this)"><div>📜</div>LOG</div>
            <div class="nav-item" onclick="switchTab('stats', this)"><div>📊</div>STATS</div>
            <div class="nav-item" onclick="switchTab('profile', this)"><div>👑</div>PROFILE</div>
        </div>
    </div>

    <script>
        const WORKER_URL = "https://wingo-cloudflare-worker.anishanisha143love.workers.dev";
        const KEY_EXPIRE_ISO = "{{ session.get('key_expire_iso', '') }}";

        let totalRounds = 0, winsCount = 0, lossesCount = 0, jackpotsCount = 0;
        let historyLogs = [];
        let isRevealed = false;
        
        let lastEvaluatedIssue = null;
        let lockedPredType = null;
        let lockedPredNum = null;
        
        // Final live calculation
        let currentPredType = "WAITING";
        let currentPredNum = 0;

        // Engine states
        let oppLosses = 0; 
        let lastOppPred = null; 

        // Warning Flags
        let warnTriggered120 = false, warnTriggered90 = false, warnTriggered60 = false, warnTriggered30 = false;

        // Audio Unlock
        let audioUnlocked = false;
        function unlockAudio() {
            if (audioUnlocked) return;
            try {
                const dummyAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3");
                dummyAudio.volume = 0.01; dummyAudio.play().then(() => { audioUnlocked = true; }).catch(e => {});
            } catch(e) {}
        }
        document.addEventListener('click', unlockAudio, { once: true });
        document.addEventListener('touchstart', unlockAudio, { once: true });

        // Animations functions
        function showWinToast() {
            const toast = document.getElementById('winToast');
            toast.classList.add('show');
            try {
                const winAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3");
                winAudio.volume = 1.0; winAudio.play().catch(e => {});
            } catch(e) {}
            setTimeout(() => { toast.classList.remove('show'); }, 3000);
        }

        function showJackpotOverlay() {
            const overlay = document.getElementById('jackpotOverlay');
            overlay.style.display = 'flex';
            try {
                const jpAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3");
                jpAudio.volume = 1.0; jpAudio.play().catch(e => {});
            } catch(e) {}
            // auto hide after 5 secs
            setTimeout(() => { overlay.style.display = 'none'; }, 5000);
        }

        function playWarningBeep() {
            try {
                const alertAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3");
                alertAudio.volume = 1.0; alertAudio.play().catch(e => {});
            } catch(e) {}
        }

        function showWarnModal(msg) {
            const modal = document.getElementById('keyWarnModal');
            const body = document.getElementById('warnBody');
            if (modal && body) {
                body.innerText = msg; modal.style.display = 'flex';
                setTimeout(() => { dismissWarnModal(); }, 4500);
            }
            playWarningBeep();
        }
        function dismissWarnModal() { document.getElementById('keyWarnModal').style.display = 'none'; }

        function getColorClass(num, type) {
            if (num === 0 || num === 5) return 'color-violet';
            if (type === 'BIG') return 'color-green';
            if (type === 'SMALL') return 'color-red';
            return 'color-wait';
        }

        function updateRealKeyTimer() {
            let labelText = "VIP ACTIVE";
            if (KEY_EXPIRE_ISO && KEY_EXPIRE_ISO !== "" && KEY_EXPIRE_ISO !== "None") {
                let formattedIso = KEY_EXPIRE_ISO.replace(" ", "T");
                if (!formattedIso.endsWith("Z") && !formattedIso.includes("+")) formattedIso += "Z";
                const expireDate = new Date(formattedIso);
                if (isNaN(expireDate.getTime())) return;
                const diffMs = expireDate.getTime() - new Date().getTime();
                const diffSecs = Math.floor(diffMs / 1000);

                if (diffSecs <= 120 && diffSecs > 105 && !warnTriggered120) { warnTriggered120 = true; showWarnModal("⚠️ WARNING: YOUR VIP KEY EXPIRES IN 2 MINUTES!"); }
                else if (diffSecs <= 90 && diffSecs > 75 && !warnTriggered90) { warnTriggered90 = true; showWarnModal("⚠️ WARNING: YOUR VIP KEY EXPIRES IN 1 MINUTE 30 SECONDS!"); }
                else if (diffSecs <= 60 && diffSecs > 45 && !warnTriggered60) { warnTriggered60 = true; showWarnModal("⚠️ WARNING: YOUR VIP KEY EXPIRES IN 1 MINUTE!"); }
                else if (diffSecs <= 30 && diffSecs > 0 && !warnTriggered30) { warnTriggered30 = true; showWarnModal("🚨 FINAL WARNING: YOUR VIP KEY EXPIRES IN 30 SECONDS!"); }

                if (diffMs <= -10000) { window.location.href = '/logout'; return; }
                else if (diffMs <= 0) { labelText = "00m 00s"; }
                else {
                    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    const secs = Math.floor((diffMs % (1000 * 60)) / 1000);
                    if (days > 0) labelText = `${days}d ${hours}h ${mins}m`;
                    else if (hours > 0) labelText = `${hours}h ${mins}m ${secs}s`;
                    else labelText = `${mins}m ${secs}s`;
                }
            } else { labelText = "UNLIMITED VIP"; }
            document.getElementById('keyTimer').innerText = labelText;
            const profTimer = document.getElementById('profileKeyTimer');
            if (profTimer) profTimer.innerText = labelText;
        }
        setInterval(updateRealKeyTimer, 1000); updateRealKeyTimer();

        function switchTab(tabName, element) {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator(), gainNode = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(587.33, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15);
                gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime); gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.connect(gainNode); gainNode.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime + 0.2);
            } catch(e) {}
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            element.classList.add('active');
        }

        function revealPrediction() {
            const pedestal = document.querySelector('.glowing-pedestal');
            const inner = document.getElementById('predDisplay');
            try {
                const dtAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3");
                dtAudio.volume = 1.0; dtAudio.play().catch(e => {});
            } catch(e) {}
            if (pedestal) pedestal.classList.add('pedestal-active-power');
            inner.className = 'prediction-display color-wait';
            inner.innerHTML = '<div class="analyzing-text">TRUST AI<br>ANALYSING...</div>';

            setTimeout(() => {
                if (pedestal) pedestal.classList.remove('pedestal-active-power');
                isRevealed = true;
                lockedPredType = currentPredType;
                lockedPredNum = currentPredNum;
                
                let colClass = getColorClass(lockedPredNum, lockedPredType);
                inner.className = `prediction-display ${colClass}`;
                inner.innerHTML = `${lockedPredType} : ${lockedPredNum}`;
            }, 1000);
        }

        function getLiveUTCPeriod() {
            const now = new Date();
            const totalMins = now.getUTCHours() * 60 + now.getUTCMinutes();
            const serial = 10000 + totalMins + 1;
            return `${now.getUTCFullYear()}${String(now.getUTCMonth()+1).padStart(2,'0')}${String(now.getUTCDate()).padStart(2,'0')}1000${serial}`;
        }

        async function fetch500Results() {
            let combinedList = [];
            // Fetch up to 5 pages for 500 results
            for(let i=1; i<=5; i++) {
                try {
                    const res = await fetch(WORKER_URL + `?pageSize=100&pageNo=${i}`);
                    const data = await res.json();
                    if (data && data.data && data.data.list) combinedList = combinedList.concat(data.data.list);
                } catch(e) { break; }
            }
            return combinedList;
        }

        function updateUIEngine(elId, val) {
            const el = document.getElementById(elId);
            if (!el) return;
            if (val === "BIG") { el.innerText = "BIG"; el.className = "color-green"; }
            else if (val === "SMALL") { el.innerText = "SMALL"; el.className = "color-red"; }
            else { el.innerText = "SKIPPED"; el.className = "color-wait"; }
        }

        async function fetchLotteryData() {
            try {
                const items = await fetch500Results();
                if (items.length > 0) {
                    const latest = items[0];
                    const actIssue = String(latest.issueNumber);
                    const actNum = parseInt(latest.number, 10);
                    const actType = actNum >= 5 ? "BIG" : "SMALL";

                    const hrEl = document.getElementById('hugeResultVal');
                    hrEl.innerText = `${actType} : ${actNum} (Period: ${actIssue.slice(-4)})`;
                    hrEl.className = `huge-last-val ${getColorClass(actNum, actType)}`;

                    if (lastEvaluatedIssue && lastEvaluatedIssue !== actIssue) {
                        totalRounds++;
                        let statusRes = "LOSS";
                        let evalType = lockedPredType || currentPredType;
                        let evalNum = (lockedPredNum !== null) ? lockedPredNum : currentPredNum;

                        // Opp Engine check
                        if (lastOppPred) {
                            if (lastOppPred === actType) oppLosses = 0;
                            else oppLosses++;
                        }

                        if (evalType === actType && evalNum === actNum) {
                            jackpotsCount++; winsCount++; statusRes = "JACKPOT";
                            showJackpotOverlay();
                        } else if (evalType === actType) {
                            winsCount++; statusRes = "WIN";
                            showWinToast();
                        } else {
                            lossesCount++; statusRes = "LOSS";
                        }

                        historyLogs.unshift({ issue: actIssue, pred: `${evalType} : ${evalNum}`, act_type: actType, act_num: actNum, status: statusRes });
                        if (historyLogs.length > 50) historyLogs.pop();
                        updateLogUI();

                        lockedPredType = null; lockedPredNum = null; isRevealed = false;
                        document.getElementById('predDisplay').className = 'prediction-display color-wait';
                        document.getElementById('predDisplay').innerHTML = `🔒 LOCKED`;
                    }

                    updateBdgChartUI(items);

                    // ==========================================
                    // 5-ENGINE MASTER ENSEMBLE SYSTEM
                    // ==========================================
                    const analysisPool = items.slice(0, 500);
                    const lastN = parseInt(items[0].number, 10);
                    const lastT = lastN >= 5 ? "BIG" : "SMALL";

                    // Engine 1: Opposite Engine
                    let predE1 = null;
                    if (oppLosses < 2) {
                        predE1 = (lastT === "BIG") ? "SMALL" : "BIG";
                    }

                    // Engine 2: Statistical / Markov Engine
                    let numFreq = Array(10).fill(0);
                    let bigC = 0, smallC = 0;
                    for (let i = 0; i < analysisPool.length - 1; i++) {
                        if (parseInt(analysisPool[i + 1].number, 10) === lastN) {
                            let nxt = parseInt(analysisPool[i].number, 10);
                            numFreq[nxt]++;
                            if (nxt >= 5) bigC++; else smallC++;
                        }
                    }
                    let predE2 = bigC >= smallC ? "BIG" : "SMALL";
                    let bestNumE2 = numFreq.indexOf(Math.max(...numFreq));

                    // Engine 3: Psychology / Momentum
                    let streak = 1;
                    for(let i=1; i<10 && i<analysisPool.length; i++) {
                        let t = parseInt(analysisPool[i].number,10)>=5 ? "BIG" : "SMALL";
                        if(t === lastT) streak++; else break;
                    }
                    let predE3 = (streak >= 3) ? lastT : ((lastT === "BIG") ? "SMALL" : "BIG");

                    // Engine 4: Smart Pattern (Zigzag / Blocks)
                    let predE4 = lastT; 
                    if (analysisPool.length >= 3) {
                        let t0 = lastT;
                        let t1 = parseInt(analysisPool[1].number,10)>=5?"BIG":"SMALL";
                        let t2 = parseInt(analysisPool[2].number,10)>=5?"BIG":"SMALL";
                        if (t0 !== t1 && t1 !== t2) predE4 = (t0 === "BIG") ? "SMALL" : "BIG"; // Zigzag
                        else if (t0 === t1 && t1 !== t2) predE4 = (t0 === "BIG") ? "SMALL" : "BIG"; // Break 2-streak
                    }

                    // UPDATE UI FOR ENGINES
                    updateUIEngine('uiEng1', predE1);
                    updateUIEngine('uiEng2', predE2);
                    updateUIEngine('uiEng3', predE3);
                    updateUIEngine('uiEng4', predE4);

                    // VOTING MECHANISM
                    let validVotes = [predE1, predE2, predE3, predE4].filter(v => v !== null);
                    let voteB = validVotes.filter(v => v === "BIG").length;
                    let voteS = validVotes.filter(v => v === "SMALL").length;

                    let finalPredT = (voteB >= voteS) ? "BIG" : "SMALL";
                    
                    // Assign Target Number
                    let subPool = finalPredT === "BIG" ? [5,6,7,8,9] : [0,1,2,3,4];
                    let finalPredN = bestNumE2;
                    if (!subPool.includes(finalPredN)) finalPredN = subPool[Math.floor(Math.random()*subPool.length)];

                    updateUIEngine('uiEngFinal', finalPredT);
                    document.getElementById('uiEngFinal').innerText = `${finalPredT} (${finalPredN})`;

                    currentPredType = finalPredT;
                    currentPredNum = finalPredN;
                    lastEvaluatedIssue = actIssue;
                    lastOppPred = predE1;

                    // Update Stats
                    document.getElementById('statTotal').innerText = totalRounds;
                    document.getElementById('statWins').innerText = winsCount;
                    document.getElementById('statLosses').innerText = lossesCount;
                    document.getElementById('statJackpots').innerText = jackpotsCount;
                    document.getElementById('statTotal2').innerText = totalRounds;
                    
                    let acc = totalRounds > 0 ? ((winsCount / totalRounds) * 100).toFixed(1) : "0.0";
                    document.getElementById('statAccuracy').innerText = acc + "%";
                }
            } catch(e) { console.error("Fetch error:", e); }
        }

        function updateBdgChartUI(items) {
            const container = document.getElementById('tirangaPatternList');
            let html = '<div style="position:relative;" id="chartWrapper"><svg id="zigzagSvg" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:1;"></svg>';
            
            const displayItems = items.slice(0, 40);
            displayItems.forEach((item, index) => {
                let issueNum = String(item.issueNumber);
                let actualNum = parseInt(item.number, 10);
                let circlesHtml = '';
                for(let i=0; i<=9; i++) {
                    let isActive = (i === actualNum);
                    let colorClass = '';
                    if (isActive) {
                        if (i === 0 || i === 5) colorClass = 'c-violet';
                        else if ([1, 3, 7, 9].includes(i)) colorClass = 'c-green';
                        else colorClass = 'c-red';
                    }
                    circlesHtml += `<div class="t-num-circle ${isActive ? 'active ' + colorClass : ''}">${i}</div>`;
                }
                html += `<div class="tiranga-row" style="position:relative; z-index:2;">
                    <div class="tiranga-period">${issueNum.slice(-4)}</div>
                    <div class="tiranga-nums">${circlesHtml}</div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        function updateLogUI() {
            const listEl = document.getElementById('logList');
            if (historyLogs.length === 0) return;
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
            let hours = now.getHours(), minutes = now.getMinutes(), seconds = now.getSeconds();
            let ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12; hours = hours ? hours : 12;
            document.getElementById('currentTime').innerText = `${hours}:${minutes<10?'0'+minutes:minutes}:${seconds<10?'0'+seconds:seconds} ${ampm}`;
            document.getElementById('currentDate').innerText = `${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}/${now.getFullYear()}`;
        }
        setInterval(updateClock, 1000); updateClock();

        function updateTimer() {
            const now = new Date();
            let remaining = 60 - now.getSeconds();
            document.getElementById('timer').innerText = `00:${remaining<10?'0'+remaining:remaining}`;
            document.getElementById('periodVal').innerText = getLiveUTCPeriod();
            if (remaining === 59 || remaining === 0) fetchLotteryData();
        }
        setInterval(updateTimer, 1000); updateTimer();
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
        key = request.form.get('license_key', '').strip()
        if not key:
            error = 'Please enter a valid License Key!'
        else:
            if db:
                try:
                    doc_ref = db.collection('trustwin_keys').document(key.upper())
                    doc = doc_ref.get()

                    if not doc.exists:
                        doc_ref = db.collection('trustwin_keys').document(key.lower())
                        doc = doc_ref.get()

                    if not doc.exists:
                        doc_ref = db.collection('trustwin_keys').document(key)
                        doc = doc_ref.get()

                    if doc.exists:
                        data = doc.to_dict()
                        if data.get('isExpired', False):
                            error = '❌ Ye Trust Win Key Expire ho chuki hai!'
                        else:
                            now_utc = datetime.now(timezone.utc)
                            expire_dt = None

                            if 'expiresAt' in data and data['expiresAt']:
                                exp_val = data['expiresAt']
                                if hasattr(exp_val, 'astimezone'):
                                    expire_dt = exp_val.astimezone(timezone.utc)
                                elif isinstance(exp_val, datetime):
                                    expire_dt = exp_val.replace(tzinfo=timezone.utc) if exp_val.tzinfo is None else exp_val.astimezone(timezone.utc)
                                else:
                                    try:
                                        s_str = str(exp_val).replace(' ', 'T')
                                        if not s_str.endswith('Z') and '+' not in s_str:
                                            s_str += 'Z'
                                        expire_dt = datetime.fromisoformat(s_str.replace('Z', '+00:00'))
                                    except Exception:
                                        expire_dt = None

                            elif 'expire_time' in data and data['expire_time']:
                                try:
                                    s_str = str(data['expire_time']).replace(' ', 'T')
                                    if not s_str.endswith('Z') and '+' not in s_str:
                                        s_str += 'Z'
                                    expire_dt = datetime.fromisoformat(s_str.replace('Z', '+00:00'))
                                except Exception:
                                    expire_dt = None

                            elif 'durationHours' in data or 'durationMinutes' in data or 'validDays' in data or 'createdAt' in data:
                                created_val = data.get('createdAt', now_utc)
                                if hasattr(created_val, 'astimezone'):
                                    created_dt = created_val.astimezone(timezone.utc)
                                elif isinstance(created_val, datetime):
                                    created_dt = created_val.replace(tzinfo=timezone.utc) if created_val.tzinfo is None else created_val.astimezone(timezone.utc)
                                else:
                                    created_dt = now_utc

                                add_secs = 0.0
                                if 'durationMinutes' in data and data['durationMinutes']:
                                    add_secs += float(data['durationMinutes']) * 60.0
                                elif 'durationHours' in data and data['durationHours']:
                                    add_secs += float(data['durationHours']) * 3600.0
                                else:
                                    add_secs += float(data.get('validDays', 30)) * 86400.0

                                expire_dt = created_dt + timedelta(seconds=add_secs)

                            if expire_dt and now_utc >= expire_dt:
                                error = '❌ Ye Trust Win Key Expire ho chuki hai!'
                            else:
                                expire_iso = expire_dt.strftime('%Y-%m-%dT%H:%M:%SZ') if expire_dt else None
                                session['authenticated'] = True
                                session['active_key'] = key.upper()
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
