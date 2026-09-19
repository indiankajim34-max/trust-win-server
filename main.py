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
            display: flex; 
            align-items: center; 
            justify-content: center; 
            gap: 6px; 
            margin-top: 18px; 
            padding: 12px; 
            width: 100%; 
            background: linear-gradient(45deg, #00c853, #00ff88); 
            color: #000; 
            font-size: 13px; 
            font-weight: 900; 
            text-decoration: none; 
            border-radius: 10px; 
            box-sizing: border-box; 
            animation: pulse-btn 2s infinite ease-in-out; 
            letter-spacing: 0.5px;
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

        <!-- ANIMATED BUY NEW KEY BUTTON REDIRECTING TO ADMIN DASHBOARD -->
        <a href="https://admin-panel-0mra.onrender.com/" target="_blank" class="buy-btn">
            🛒 BUY NEW VIP KEY 🔑
        </a>
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
        /* CASINO DRAGON TIGER POWER SHAKE ANIMATION */
        @keyframes casino-power-anim {
            0% { transform: scale(1); box-shadow: 0 0 20px #00ff88; border-color: #00ff88; }
            30% { transform: scale(1.08); box-shadow: 0 0 35px #ffcc00; border-color: #ffcc00; }
            60% { transform: scale(0.96); box-shadow: 0 0 45px #00e5ff; border-color: #00e5ff; }
            100% { transform: scale(1); box-shadow: 0 0 20px #00ff88; border-color: #00ff88; }
        }
        .pedestal-active-power {
            animation: casino-power-anim 0.25s infinite ease-in-out !important;
        }

        @keyframes bg-glow-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes text-flash {
            0% { opacity: 0.4; }
            50% { opacity: 1; color: #00ff88; text-shadow: 0 0 15px #00ff88; }
            100% { opacity: 0.4; }
        }
        * { box-sizing: border-box; }
        body { background-color: #0c0c0c; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 4px; overflow: hidden; position: fixed; width: 100%; height: 100%; }
        .container { max-width: 420px; height: 100%; margin: auto; background: linear-gradient(145deg, #121212, #181818); border: 2px solid #d4af37; border-radius: 16px; padding: 6px 6px 52px 6px; animation: glow 4s infinite ease-in-out; position: relative; display: flex; flex-direction: column; overflow: hidden; }
        
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
        
        /* LEFT VIP PREDICTOR CARD WITH MULTI-COLOR ANIMATED BACKGROUND */
        .predictor-box { 
            background: linear-gradient(135deg, #071510, #130026, #001f18, #180d00);
            background-size: 400% 400%;
            animation: bg-glow-shift 10s infinite ease;
            border: 1px solid #00ff88aa; 
            border-radius: 10px; 
            padding: 5px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: space-between; 
            position: relative; 
            box-shadow: 0 0 20px rgba(0,255,136,0.25), inset 0 0 15px rgba(155,89,182,0.3); 
        }
        .wings-banner { background: linear-gradient(90deg, transparent, #00ff8833, transparent); border: 1px solid #ffcc00; border-radius: 12px; padding: 3px 6px; color: #ffcc00; font-size: 8px; font-weight: bold; letter-spacing: 1px; width: 92%; margin-top: 1px; }
        
        .glowing-pedestal { width: 115px; height: 115px; border-radius: 50%; border: 3px solid #00ff88; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(0,255,136,0.35) 0%, transparent 75%); animation: radar-pulse 3s infinite ease-in-out; margin: auto; cursor: pointer; transition: 0.2s; }
        .leaf-icon { font-size: 18px; color: #00ff88; margin-bottom: 2px; }
        .prediction-display { font-size: 15px; font-weight: 900; color: #00ff88; text-shadow: 0 0 10px #00ff88; text-align: center; }
        .analyzing-text { font-size: 8px; font-weight: bold; color: #00ff88; animation: text-flash 0.5s infinite; line-height: 1.2; text-align: center; }
        .winner-badge { background: linear-gradient(45deg, #111, #222); border: 1px solid #ffcc00; color: #ffcc00; border-radius: 8px; padding: 3px 8px; font-size: 8px; font-weight: bold; width: 85%; margin-bottom: 2px; }

        /* RIGHT CALCULATOR CARD (Vibrant Colors & Big Buttons) */
        .calc-box { background: #0a0d12; border: 1px solid #00a2ff66; border-radius: 10px; padding: 5px; display: flex; flex-direction: column; justify-content: space-between; font-size: 9px; }
        .calc-header { display: flex; justify-content: space-between; align-items: center; color: #00a2ff; font-weight: bold; font-size: 8px; margin-bottom: 2px; }
        .calc-display { background: #000; border: 1px solid #333; border-radius: 4px; color: #00ff88; font-size: 13px; font-weight: bold; text-align: right; padding: 4px 6px; margin-bottom: 4px; min-height: 24px; word-break: break-all; }
        
        /* Vibrant Color-Coded Numpad Buttons */
        .calc-pad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px; margin-bottom: 4px; }
        .calc-btn { border-radius: 4px; padding: 6px 0; font-size: 11px; font-weight: 900; cursor: pointer; border: 1px solid #333; transition: 0.1s; }
        .calc-btn:active { transform: scale(0.92); }
        .calc-btn.n1 { background: #ff336622; border-color: #ff3366; color: #ff6688; }
        .calc-btn.n2 { background: #00e5ff22; border-color: #00e5ff; color: #33efff; }
        .calc-btn.n3 { background: #ffcc0022; border-color: #ffcc00; color: #ffdd33; }
        .calc-btn.n4 { background: #a855f722; border-color: #a855f7; color: #c084fc; }
        .calc-btn.n5 { background: #22c55e22; border-color: #22c55e; color: #4ade80; }
        .calc-btn.n6 { background: #f9731622; border-color: #f97316; color: #fb923c; }
        .calc-btn.n7 { background: #ec489922; border-color: #ec4899; color: #f472b6; }
        .calc-btn.n8 { background: #3b82f622; border-color: #3b82f6; color: #60a5fa; }
        .calc-btn.n9 { background: #eab30822; border-color: #eab308; color: #fde047; }
        .calc-btn.n0 { background: #06b6d422; border-color: #06b6d4; color: #22d3ee; }
        .calc-btn.dot { background: #64748b22; border-color: #64748b; color: #94a3b8; }
        .calc-btn.clr { background: #ef444422; border-color: #ef4444; color: #f87171; }
        
        .save-invest-btn { background: linear-gradient(90deg, #00cc66, #00ff88); color: #000; border: none; border-radius: 5px; padding: 5px; font-size: 10px; font-weight: 900; cursor: pointer; margin-bottom: 4px; width: 100%; box-shadow: 0 0 10px rgba(0,255,136,0.5); }

        /* TWO LARGE SUMMARY BUTTONS (BET AMOUNT & WIN AMOUNT) */
        .summary-two-grid { display: flex; flex-direction: column; gap: 4px; width: 100%; margin-top: 2px; }
        .big-summary-btn { background: #0b1522; border: 1.5px solid #00a2ff; border-radius: 6px; padding: 4px 6px; text-align: center; box-shadow: 0 0 8px rgba(0,162,255,0.25); }
        .big-summary-btn.win-card { border-color: #00ff88; box-shadow: 0 0 8px rgba(0,255,136,0.25); }
        .big-summary-btn.loss-card { border-color: #ff4444; box-shadow: 0 0 8px rgba(255,68,68,0.25); }
        .big-sum-title { font-size: 7px; font-weight: 900; color: #aaa; letter-spacing: 0.5px; }
        .big-sum-val { font-size: 12px; font-weight: 900; color: #fff; margin-top: 1px; }

        .reset-btn { background: #161e2b; color: #00a2ff; border: 1px solid #00a2ff66; border-radius: 4px; padding: 3px; font-size: 8px; font-weight: bold; cursor: pointer; margin-top: 3px; width: 100%; }

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

        /* FIXED & RAISED BOTTOM NAVIGATION BAR */
        .bottom-nav { position: absolute; bottom: 14px; left: 0; right: 0; background: #111; border-top: 1px solid #333; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; display: grid; grid-template-columns: repeat(5, 1fr); padding: 6px 0 10px 0; z-index: 25; box-shadow: 0 -5px 12px rgba(0,0,0,0.85); }
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
                <!-- LEFT VIP PREDICTOR CARD WITH ANIMATED MULTI-COLOR BACKGROUND -->
                <div class="predictor-box">
                    <div class="wings-banner">👑 CHECK RESULT 👑</div>
                    
                    <div class="glowing-pedestal" onclick="revealPrediction()">
                        <div class="leaf-icon">🍁</div>
                        <div class="prediction-display" id="predDisplay">🔒 LOCKED</div>
                    </div>

                    <div class="winner-badge">👑 WINNER 👑</div>
                </div>

                <!-- RIGHT CALCULATOR & BET/WIN AMOUNT TRACKER -->
                <div class="calc-box">
                    <div class="calc-header">
                        <span>🧮 AMOUNT CALCULATOR</span>
                        <span style="cursor:pointer;" onclick="clearCalc()" title="Clear">🔄</span>
                    </div>
                    <div class="calc-display" id="calcDisplay">0</div>

                    <!-- COLORFUL NUMPAD BUTTONS -->
                    <div class="calc-pad">
                        <button class="calc-btn n7" onclick="pressCalc('7')">7</button>
                        <button class="calc-btn n8" onclick="pressCalc('8')">8</button>
                        <button class="calc-btn n9" onclick="pressCalc('9')">9</button>

                        <button class="calc-btn n4" onclick="pressCalc('4')">4</button>
                        <button class="calc-btn n5" onclick="pressCalc('5')">5</button>
                        <button class="calc-btn n6" onclick="pressCalc('6')">6</button>

                        <button class="calc-btn n1" onclick="pressCalc('1')">1</button>
                        <button class="calc-btn n2" onclick="pressCalc('2')">2</button>
                        <button class="calc-btn n3" onclick="pressCalc('3')">3</button>

                        <button class="calc-btn n0" onclick="pressCalc('0')">0</button>
                        <button class="calc-btn dot" onclick="pressCalc('.')">.</button>
                        <button class="calc-btn clr" onclick="clearCalc()">⌫</button>
                    </div>

                    <button class="save-invest-btn" onclick="saveInvestAmount()">💾 SAVE INVEST AMOUNT</button>

                    <!-- 2 LARGE SUMMARY BUTTONS (BET AMOUNT & WIN AMOUNT) -->
                    <div class="summary-two-grid">
                        <div class="big-summary-btn">
                            <span class="big-sum-title">🎰 BET AMOUNT</span>
                            <div class="big-sum-val" style="color:#00a2ff;" id="betAmountVal">₹ 0</div>
                        </div>

                        <div class="big-summary-btn win-card" id="winCardBox">
                            <span class="big-sum-title" id="winCardTitle">🏆 WIN AMOUNT (NET)</span>
                            <div class="big-sum-val" style="color:#00ff88;" id="winAmountVal">₹ 0</div>
                        </div>
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

        <!-- 5-ITEM RAISED BOTTOM NAV BAR -->
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

        // CALCULATOR & BET / WIN TRACKER LOGIC
        let calcExpr = "";
        let totalInvested = 0;
        let totalPayout = 0;
        let lastRoundBet = 0;
        let netWinAmount = 0;

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
                lastRoundBet = amt;
                document.getElementById('betAmountVal').innerText = `₹ ${Math.round(lastRoundBet)}`;
                clearCalc();
            }
        }

        function updateWinCardUI() {
            const cardBox = document.getElementById('winCardBox');
            const cardVal = document.getElementById('winAmountVal');
            
            if (netWinAmount < 0) {
                cardBox.className = "big-summary-btn loss-card";
                cardVal.style.color = "#ff4444";
                cardVal.innerText = `- ₹ ${Math.abs(Math.round(netWinAmount))}`;
            } else {
                cardBox.className = "big-summary-btn win-card";
                cardVal.style.color = "#00ff88";
                cardVal.innerText = `+ ₹ ${Math.round(netWinAmount)}`;
            }
        }

        function resetSummary() {
            totalInvested = 0;
            totalPayout = 0;
            lastRoundBet = 0;
            netWinAmount = 0;
            document.getElementById('betAmountVal').innerText = "₹ 0";
            updateWinCardUI();
            clearCalc();
        }

        // FIXED LICENSE KEY TIMER WITH SAFE PARSING & BUFFER
        function updateRealKeyTimer() {
            let labelText = "VIP ACTIVE";
            if (KEY_EXPIRE_ISO && KEY_EXPIRE_ISO !== "" && KEY_EXPIRE_ISO !== "None") {
                let formattedIso = KEY_EXPIRE_ISO.replace(" ", "T");
                if (!formattedIso.endsWith("Z") && !formattedIso.includes("+")) {
                    formattedIso += "Z";
                }
                const expireDate = new Date(formattedIso);
                
                if (isNaN(expireDate.getTime())) {
                    document.getElementById('keyTimer').innerText = labelText;
                    return;
                }

                const now = new Date();
                const diffMs = expireDate.getTime() - now.getTime();

                // 10-second grace buffer to prevent instant logout on tiny clock drift
                if (diffMs <= -10000) {
                    labelText = "EXPIRED";
                    document.getElementById('keyTimer').innerText = labelText;
                    window.location.href = '/logout';
                    return;
                } else if (diffMs <= 0) {
                    labelText = "00m 00s";
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

        // PROFESSIONAL DRAGON TIGER STYLE CASINO UNLOCK SOUND
        function revealPrediction() {
            const pedestal = document.querySelector('.glowing-pedestal');
            const inner = document.getElementById('predDisplay');

            // Play Fast, High-Energy Dragon-Tiger Casino Reveal Sound
            try {
                const dtAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3");
                dtAudio.volume = 1.0;
                dtAudio.play().catch(e => console.log("Audio play deferred:", e));
            } catch(e) {}

            // Trigger Fast Casino Power Animation
            if (pedestal) pedestal.classList.add('pedestal-active-power');

            inner.innerHTML = '<div class="analyzing-text">TRUST AI<br>ANALYSING...</div>';

            setTimeout(() => {
                if (pedestal) pedestal.classList.remove('pedestal-active-power');
                isRevealed = true;
                inner.innerHTML = `${currentPredType} : ${currentPredNum}`;
            }, 1000);
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

                        if (lastRoundBet > 0) {
                            totalInvested += lastRoundBet;
                            if (statusRes === "WIN" || statusRes === "JACKPOT") {
                                let totalReturnVal = lastRoundBet * 1.96;
                                totalPayout += totalReturnVal;
                            }
                            netWinAmount = totalPayout - totalInvested;

                            lastRoundBet = 0;
                            document.getElementById('betAmountVal').innerText = "₹ 0";
                            updateWinCardUI();
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
        key = request.form.get('license_key', '').strip()
        if not key:
            error = 'Please enter a valid License Key!'
        else:
            if db:
                try:
                    # Case-Insensitive Document Lookup Logic
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

                            # ACCURATE DECIMAL DURATION CALCULATOR (float() conversion fixes 10m/20m/30m bug)
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

                            # STRICT BACKEND EXPIRE CHECK BEFORE SETTING SESSION
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
