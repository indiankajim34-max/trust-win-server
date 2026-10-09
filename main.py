from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.secret_key = 'trustwin_ultimate_secret_key_2026_engine_wins'

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
        body { 
            background-color: #080808; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; 
            height: 100vh; overflow: hidden; position: relative;
        }
        .video-bg {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1; opacity: 0.7;
        }
        .login-card { 
            background: linear-gradient(145deg, rgba(18,18,18,0.7), rgba(26,26,26,0.7)); backdrop-filter: blur(12px);
            border: 2px solid #d4af37; border-radius: 20px; padding: 25px; width: 100%; max-width: 350px; 
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.4); z-index: 2; position: relative;
        }
        .title { font-size: 18px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
        .sub { font-size: 11px; color: #ccc; margin-bottom: 20px; font-weight:bold; }
        .input-box { width: 100%; padding: 12px; background: rgba(0,0,0,0.6); border: 1px solid #d4af37; border-radius: 10px; color: #fff; font-size: 14px; text-align: center; margin-bottom: 15px; box-sizing: border-box; outline: none; text-transform: uppercase; font-weight: bold; }
        .input-box:focus { border-color: #ffdf73; box-shadow: 0 0 15px rgba(255, 223, 115, 0.5); }
        .btn { background: linear-gradient(45deg, #d4af37, #ffdf73); color: #000; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(212,175,55,0.4); }
        .buy-btn { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 18px; padding: 12px; width: 100%; background: linear-gradient(45deg, #00c853, #00ff88); color: #000; font-size: 13px; font-weight: 900; text-decoration: none; border-radius: 10px; box-sizing: border-box; animation: pulse-btn 2s infinite ease-in-out; letter-spacing: 0.5px; }
        .error { color: #ff4444; font-size: 13px; margin-top: 15px; font-weight:bold; text-shadow: 0 0 5px rgba(255,0,0,0.5); }
    </style>
</head>
<body>
    <video autoplay loop muted playsinline class="video-bg">
        <source src="https://www.image2url.com/r2/default/videos/1785310888502-2cf6edf9-e8da-4acd-9499-49cf0bafddf2.mp4" type="video/mp4">
    </video>
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
    <title>Trust Win VIP - Engine Win-Tracking AI</title>
    <style>
        @keyframes glow {
            0% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.3); border-color: #d4af37; }
            50% { box-shadow: 0 0 35px rgba(212, 175, 55, 0.8); border-color: #ffdf73; }
            100% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.3); border-color: #d4af37; }
        }
        @keyframes radar-pulse {
            0% { transform: scale(0.95); opacity: 0.85; box-shadow: 0 0 20px #ffdf73, inset 0 0 15px #ffdf73; }
            50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 60px #ffdf73, inset 0 0 30px #ffdf73; }
            100% { transform: scale(0.95); opacity: 0.85; box-shadow: 0 0 20px #ffdf73, inset 0 0 15px #ffdf73; }
        }
        @keyframes win-flash-anim {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(0,255,136,0.6); border-color: #00ff88; }
            50% { transform: scale(1.1); box-shadow: 0 0 90px #00ff88, inset 0 0 40px #00ff88; border-color: #00ff88; }
            100% { transform: scale(1); box-shadow: 0 0 20px rgba(0,255,136,0.6); border-color: #00ff88; }
        }
        .pedestal-win-flash {
            animation: win-flash-anim 1.5s ease-in-out !important;
            border-color: #00ff88 !important;
            background: radial-gradient(circle, rgba(0,255,136,0.4) 0%, rgba(0,0,0,0.6) 80%) !important;
        }

        @keyframes pulse-warn {
            0% { transform: scale(1); box-shadow: 0 0 20px #ff3300; }
            50% { transform: scale(1.03); box-shadow: 0 0 40px #ff6600; }
            100% { transform: scale(1); box-shadow: 0 0 20px #ff3300; }
        }

        @keyframes rainbow-glow {
            0% { border-color: #ff0055; box-shadow: 0 0 30px #ff0055, inset 0 0 20px #ff0055; }
            33% { border-color: #00ff88; box-shadow: 0 0 30px #00ff88, inset 0 0 20px #00ff88; }
            66% { border-color: #00ccff; box-shadow: 0 0 30px #00ccff, inset 0 0 20px #00ccff; }
            100% { border-color: #ff0055; box-shadow: 0 0 30px #ff0055, inset 0 0 20px #ff0055; }
        }

        .analyzing-effect {
            animation: rainbow-glow 1s infinite linear !important;
            background: radial-gradient(circle, rgba(192,132,252,0.35) 0%, rgba(0,0,0,0.7) 80%) !important;
        }

        .win-toast {
            position: fixed; top: -100px; left: 50%; transform: translateX(-50%);
            background: linear-gradient(45deg, #00ff88, #009955); color: #000;
            padding: 15px 40px; border-radius: 30px; font-weight: 900; font-size: 22px;
            z-index: 10000; transition: top 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 5px 30px rgba(0,255,136,0.8); border: 2px solid #fff; letter-spacing: 2px;
        }
        .win-toast.show { top: 30px; }

        .jackpot-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.95); z-index: 10001; align-items: center; justify-content: center; flex-direction: column;
        }
        .jackpot-text {
            font-size: 42px; font-weight: 900; background: linear-gradient(45deg, #ffcc00, #fff, #ffcc00);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px #ffcc00;
            animation: radar-pulse 0.5s infinite; text-align: center; line-height: 1.3; padding: 0 20px;
        }

        * { box-sizing: border-box; }
        body { 
            background-color: #0c0c0c; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; margin: 0; padding: 4px; overflow: hidden; position: fixed; width: 100%; height: 100%; 
        }

        .video-bg {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            object-fit: cover; z-index: -1; opacity: 0.8; filter: contrast(1.2) brightness(0.9);
        }

        .container { 
            max-width: 420px; height: 100%; margin: auto; 
            background: rgba(10, 10, 10, 0.4); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
            border: 2px solid rgba(212, 175, 55, 0.7); border-radius: 16px; padding: 6px 6px 52px 6px; 
            position: relative; display: flex; flex-direction: column; overflow: hidden; 
            box-shadow: 0 0 35px rgba(0,0,0,0.8);
        }
        
        .top-banner { 
            background: rgba(18,18,18,0.5); backdrop-filter: blur(6px); border: 1px solid #d4af37; border-radius: 10px; 
            padding: 5px; margin-bottom: 3px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }
        .vip-header { display: flex; justify-content: space-between; align-items: center; font-size: 9px; font-weight: bold; color: #d4af37; border-bottom: 1px solid rgba(212,175,55,0.4); padding-bottom: 2px; margin-bottom: 2px; }
        
        .main-title { font-size: 15px; font-weight: 900; background: linear-gradient(45deg, #d4af37, #fff, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
        .sub-engine { font-size: 9px; color: #00ff88; margin-top: 1px; font-weight: bold; letter-spacing: 1px; }
        .time-row { display: flex; justify-content: space-between; font-size: 9px; color: #ccc; margin-top: 2px; padding: 0 4px; font-weight:bold; }

        .huge-last-result { 
            background: rgba(0,0,0,0.5); backdrop-filter: blur(6px); border: 2px solid #ffdf73; border-radius: 8px; 
            padding: 4px; margin: 3px 0; box-shadow: 0 0 15px rgba(255,223,115,0.3); flex-shrink: 0; 
        }
        .huge-last-title { font-size: 9px; color: #ffdf73; font-weight: bold; letter-spacing: 1px; }
        .huge-last-val { font-size: 15px; font-weight: 900; text-shadow: 0 0 10px rgba(255,255,255,0.3); margin-top:2px; }

        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3px; margin: 2px 0; flex-shrink: 0; }
        .stat-card { background: rgba(18,18,18,0.5); backdrop-filter: blur(6px); border: 1px solid #d4af3755; padding: 4px 2px; border-radius: 6px; }
        .stat-card .lbl { font-size: 8px; color: #ccc; font-weight:bold; }
        .stat-card .val { font-size: 12px; font-weight: 900; color: #fff; margin-top: 1px; display: block; }

        .period-box { 
            background: rgba(18,18,18,0.5); backdrop-filter: blur(6px); border: 1px solid #d4af37; border-radius: 6px; 
            padding: 5px 8px; margin: 2px 0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; 
        }
        .period-box div { text-align: left; font-size: 9px; color: #ccc; font-weight:bold; }
        .period-box span { font-size: 12px; font-weight: 900; color: #fff; display: block; margin-top:1px; }
        .countdown { font-size: 16px !important; font-weight: 900; color: #ffcc00 !important; font-family: monospace; text-shadow: 0 0 8px #ffcc00;}

        .tab-content { display: none; height: 100%; flex-direction: column; flex-grow: 1; overflow: hidden; }
        .tab-content.active { display: flex; }

        .giant-predictor { 
            flex-grow: 1; margin-top: 5px; 
            background: rgba(10, 5, 0, 0.3); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
            border: 2px solid #d4af37; border-radius: 12px; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            position: relative; box-shadow: 0 0 25px rgba(212,175,55,0.3), inset 0 0 15px rgba(255,223,115,0.1); 
            padding: 15px;
        }
        .wings-banner { 
            background: linear-gradient(90deg, transparent, rgba(212,175,55,0.5), transparent); 
            border: 1px solid #ffcc00; border-radius: 20px; padding: 5px 25px; color: #ffcc00; 
            font-size: 12px; font-weight: 900; letter-spacing: 2px; position: absolute; top: 15px; 
        }
        
        .glowing-pedestal { 
            width: 175px; height: 175px; border-radius: 50%; border: 4px solid #ffdf73; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            background: radial-gradient(circle, rgba(212,175,55,0.2) 0%, rgba(0,0,0,0.5) 80%); 
            animation: radar-pulse 3s infinite ease-in-out; cursor: pointer; transition: 0.3s; 
            box-shadow: 0 0 30px #d4af37; z-index: 2;
        }
        .leaf-icon { font-size: 42px; margin-bottom: 3px; filter: drop-shadow(0 0 10px #ffdf73); }
        .prediction-display { font-size: 17px; font-weight: 900; text-shadow: 0 0 15px rgba(255,255,255,0.5); text-align: center; letter-spacing: 0.5px; }

        .color-green { color: #00ff88 !important; text-shadow: 0 0 15px rgba(0,255,136,0.8) !important; font-size: 24px !important; }
        .color-red { color: #ff4444 !important; text-shadow: 0 0 15px rgba(255,68,68,0.8) !important; font-size: 24px !important; }
        .color-violet { color: #c084fc !important; text-shadow: 0 0 15px rgba(192,132,252,0.8) !important; font-size: 24px !important; }
        .color-wait { color: #ffcc00 !important; }

        .engine-status-box { 
            background: rgba(0,0,0,0.6); backdrop-filter: blur(6px); border: 2px solid #d4af37; border-radius: 10px; 
            padding: 10px; display: flex; flex-direction: column; width: 100%; margin-top: 10px; 
        }
        .engine-header { color: #ffcc00; font-weight: 900; font-size: 11px; text-align: center; border-bottom: 2px solid #d4af3755; padding-bottom: 6px; margin-bottom: 6px; letter-spacing: 1px; }
        .engine-row { display: flex; justify-content: space-between; align-items: center; background: rgba(20,20,20,0.8); border: 1px solid #444; border-radius: 6px; padding: 6px 10px; margin-bottom: 4px; font-size: 10px; font-weight: bold; }
        .engine-row span { color: #ccc; }
        .final-vote { background: linear-gradient(90deg, #3a2a00, #000); border-color: #ffdf73; padding: 8px; font-size: 11px; margin-top: 5px; box-shadow: inset 0 0 10px rgba(255,223,115,0.2); }

        .chart-scroll-area { flex-grow: 1; overflow-y: auto; overflow-x: hidden; position: relative; padding-right: 2px; margin-top: 5px; }
        .tiranga-row { background: rgba(15,15,15,0.7); border: 1px solid #444; border-radius: 6px; padding: 4px; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center; font-size: 9px; }
        .tiranga-period { color: #ffdf73; font-family: monospace; font-size: 9px; font-weight:bold; text-align: left; width: 65px; flex-shrink: 0; }
        .tiranga-nums { display: flex; gap: 3px; align-items: center; justify-content: space-between; flex-grow: 1; padding: 0 4px; }
        .t-num-circle { width: 17px; height: 17px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 8px; font-weight: 900; background: #111; color: #555; border: 1px solid #444; }
        .t-num-circle.c-violet { background: #9b59b6 !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 6px #9b59b6; }
        .t-num-circle.c-green { background: #2ecc71 !important; color: #000 !important; border-color: #fff !important; box-shadow: 0 0 6px #2ecc71; }
        .t-num-circle.c-red { background: #e74c3c !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 6px #e74c3c; }

        .log-list { flex-grow: 1; overflow-y: auto; text-align: left; font-size: 10px; margin-top: 5px; }
        .log-item { background: rgba(15,15,15,0.7); border: 1px solid #444; border-radius: 6px; padding: 6px; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center; }
        .badge-win { color: #00ff88; font-weight: 900; background: rgba(0,255,136,0.15); padding: 3px 6px; border-radius: 4px; border: 1px solid #00ff88; }
        .badge-loss { color: #ff4444; font-weight: 900; background: rgba(255,68,68,0.15); padding: 3px 6px; border-radius: 4px; border: 1px solid #ff4444; }

        .profile-card { background: rgba(15,15,15,0.75); border: 1px solid #d4af37; border-radius: 8px; padding: 10px; margin-top: 8px; text-align: left; font-size: 10px; font-weight: bold; }
        .profile-card p { margin: 6px 0; color: #ddd; }
        .profile-card span { color: #fff; font-weight: 900; }

        .bottom-nav { position: absolute; bottom: 12px; left: 0; right: 0; background: rgba(10,10,10,0.85); backdrop-filter: blur(8px); border-top: 2px solid #d4af37; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; display: grid; grid-template-columns: repeat(5, 1fr); padding: 8px 0 12px 0; z-index: 25; box-shadow: 0 -5px 20px rgba(0,0,0,0.9); }
        .nav-item { font-size: 8px; color: #888; font-weight: bold; cursor: pointer; transition: 0.2s; text-decoration: none; display: flex; flex-direction: column; align-items: center; }
        .nav-item.active { color: #ffdf73; text-shadow: 0 0 8px rgba(255,223,115,0.5); }
        .nav-item div { font-size: 14px; margin-bottom: 3px; }
    </style>
</head>
<body>
    <video autoplay loop muted playsinline class="video-bg">
        <source src="https://www.image2url.com/r2/default/videos/1785310888502-2cf6edf9-e8da-4acd-9499-49cf0bafddf2.mp4" type="video/mp4">
    </video>

    <div id="winToast" class="win-toast">🏆 WINNER 🏆</div>

    <div id="jackpotOverlay" class="jackpot-overlay" onclick="this.style.display='none'">
        <div class="jackpot-text" id="jackpotMsg">🎉 MEGA JACKPOT 🎉<br><span id="jpSubText" style="font-size:22px; color:#00ff88;"></span></div>
    </div>

    <div id="keyWarnModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:9999; align-items:center; justify-content:center; padding:20px; box-sizing:border-box;">
        <div style="background:linear-gradient(145deg, #220000, #3d0000); border:3px solid #ff3300; border-radius:20px; padding:20px; text-align:center; max-width:320px; box-shadow:0 0 35px #ff3300; animation:pulse-warn 1.5s infinite;">
            <div style="font-size:38px; margin-bottom:5px;">⚠️</div>
            <div style="font-size:15px; font-weight:900; color:#ff3300; letter-spacing:1px; margin-bottom:8px;">VIP KEY EXPIRING SOON</div>
            <div style="font-size:12px; color:#fff; font-weight:bold; margin-bottom:15px; line-height:1.4;" id="warnBody">Your VIP key will expire shortly!</div>
            <button onclick="dismissWarnModal()" style="background:linear-gradient(45deg, #ff3300, #ff6600); color:#fff; border:none; padding:10px 20px; font-weight:900; border-radius:8px; cursor:pointer; font-size:12px; width:100%;">OK, UNDERSTOOD</button>
        </div>
    </div>

    <div class="container">
        <div class="top-banner">
            <div class="vip-header">
                <span>👑 TRUST WIN VIP</span>
                <span>🔑 KEY: <span style="color:#00ff88;">ACTIVE</span> (<span id="keyTimer" style="color:#ffdf73;">Syncing...</span>)</span>
            </div>
            <div class="main-title">🍁 TRUST WIN 🍁</div>
            <div class="sub-engine">15-ENGINE WIN-TRACKING MASTER</div>
            <div class="time-row">
                <span id="currentTime">--:--:-- PM</span>
                <span id="currentDate">--/--/----</span>
            </div>
        </div>

        <div class="huge-last-result">
            <div class="huge-last-title">🔥 LIVE WINGO RESULT TRACKER 🔥</div>
            <div class="huge-last-val" id="hugeResultVal">Connecting to Worker...</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="lbl">TOTAL</div><span class="val" id="statTotal">0</span>
            </div>
            <div class="stat-card" style="border-color: #00ff88aa; background: rgba(0,255,136,0.15);">
                <div class="lbl" style="color:#00ff88;">WIN</div><span class="val" id="statWins" style="color: #00ff88;">0</span>
            </div>
            <div class="stat-card" style="border-color: #ff4444aa; background: rgba(255,68,68,0.15);">
                <div class="lbl" style="color:#ff4444;">LOSS</div><span class="val" id="statLosses" style="color: #ff4444;">0</span>
            </div>
            <div class="stat-card" style="border-color: #ffcc00aa; background: rgba(255,204,0,0.15);">
                <div class="lbl" style="color:#ffcc00;">JACKPOT</div><span class="val" id="statJackpots" style="color: #ffcc00;">0</span>
            </div>
        </div>

        <div class="period-box">
            <div>CURRENT PERIOD<br><b id="periodVal" style="color:#ffdf73; font-size:11px;">Syncing...</b></div>
            <div style="text-align: right;">NEXT SIGNAL IN<br><div class="countdown" id="timer">00:60</div></div>
        </div>

        <div id="tab-terminal" class="tab-content active">
            <div class="giant-predictor">
                <div class="wings-banner">👑 CHECK RESULT 👑</div>
                <div class="glowing-pedestal" id="mainPedestal" onclick="revealPrediction()">
                    <div class="leaf-icon">👑</div>
                    <div class="prediction-display color-wait" id="predDisplay">CHECK RESULT</div>
                </div>
            </div>
        </div>

        <div id="tab-stats" class="tab-content">
            <div style="background:rgba(20,20,20,0.6); backdrop-filter:blur(6px); border:1px solid #d4af37; border-radius:10px; padding:10px; overflow-y:auto; flex-grow:1;">
                <div style="font-size:11px; color:#ffdf73; font-weight:900; margin-bottom:8px; text-align:center;">📊 METRICS & 15 ENGINES</div>
                
                <div style="background:rgba(0,0,0,0.7); border-radius:6px; padding:8px; text-align:left; font-size:10px; font-weight:bold; border:1px solid #444;">
                    <p style="display:flex; justify-content:space-between; margin:3px 0;"><span>Total Rounds:</span> <b id="statTotal2" style="color:#fff;">0</b></p>
                    <p style="display:flex; justify-content:space-between; margin:3px 0;"><span>Real Accuracy:</span> <b id="statAccuracy" style="color:#00ff88;">0.0%</b></p>
                </div>

                <div class="engine-status-box">
                    <div class="engine-header">🤖 15 MASTER ENGINES VOTING PANEL</div>
                    <div class="engine-row"><span>1. Sequence Opposite Engine <b style="color:#00ff88; font-size:9px;" id="winCnt1">(0 Wins)</b>:</span> <b id="uiEng1">--</b></div>
                    <div class="engine-row"><span>2. Statistical Engine <b style="color:#00ff88; font-size:9px;" id="winCnt2">(0 Wins)</b>:</span> <b id="uiEng2">--</b></div>
                    <div class="engine-row"><span>3. Psychology Engine <b style="color:#00ff88; font-size:9px;" id="winCnt3">(0 Wins)</b>:</span> <b id="uiEng3">--</b></div>
                    <div class="engine-row"><span>4. Pattern Engine <b style="color:#00ff88; font-size:9px;" id="winCnt4">(0 Wins)</b>:</span> <b id="uiEng4">--</b></div>
                    <div class="engine-row"><span>5. Zig-Zag Engine <b style="color:#00ff88; font-size:9px;" id="winCnt5">(0 Wins)</b>:</span> <b id="uiEng5">--</b></div>
                    <div class="engine-row"><span>6. Loss Grant Engine <b style="color:#00ff88; font-size:9px;" id="winCnt6">(0 Wins)</b>:</span> <b id="uiEng6">--</b></div>
                    <div class="engine-row"><span>7. Math Counting Engine <b style="color:#00ff88; font-size:9px;" id="winCnt7">(0 Wins)</b>:</span> <b id="uiEng7">--</b></div>
                    <div class="engine-row"><span>8. Zigzag Trend Engine <b style="color:#00ff88; font-size:9px;" id="winCnt8">(0 Wins)</b>:</span> <b id="uiEng8">--</b></div>
                    <div class="engine-row"><span>9. Chart Map Engine <b style="color:#00ff88; font-size:9px;" id="winCnt9">(0 Wins)</b>:</span> <b id="uiEng9">--</b></div>
                    <div class="engine-row"><span>10. 2S/2B Rule Engine <b style="color:#00ff88; font-size:9px;" id="winCnt10">(0 Wins)</b>:</span> <b id="uiEng10">--</b></div>
                    <div class="engine-row"><span>11. Breakout Engine <b style="color:#00ff88; font-size:9px;" id="winCnt11">(0 Wins)</b>:</span> <b id="uiEng11">--</b></div>
                    <div class="engine-row"><span>12. Pattern Detect Engine <b style="color:#00ff88; font-size:9px;" id="winCnt12">(0 Wins)</b>:</span> <b id="uiEng12">--</b></div>
                    <div class="engine-row"><span>13. Loss Guard Engine <b style="color:#00ff88; font-size:9px;" id="winCnt13">(0 Wins)</b>:</span> <b id="uiEng13">--</b></div>
                    <div class="engine-row"><span>14. Dual Confirm Engine <b style="color:#00ff88; font-size:9px;" id="winCnt14">(0 Wins)</b>:</span> <b id="uiEng14">--</b></div>
                    <div class="engine-row"><span>15. Dual Lock Engine <b style="color:#00ff88; font-size:9px;" id="winCnt15">(0 Wins)</b>:</span> <b id="uiEng15">--</b></div>
                    <div class="engine-row final-vote"><span>FINAL MAJORITY (15 ENGINES):</span> <b id="uiEngFinal" style="font-size:12px;">--</b></div>
                </div>
            </div>
        </div>

        <div id="tab-pattern" class="tab-content">
            <div style="background:rgba(20,20,20,0.6); backdrop-filter:blur(6px); border:1px solid #d4af37; border-radius:10px; padding:10px; display:flex; flex-direction:column; height:100%;">
                <div style="font-size:10px; color:#ffdf73; font-weight:900; text-align:center; margin-bottom:5px;">📊 BDG CHART TREND</div>
                <div class="chart-scroll-area" id="tirangaPatternList">
                    <div style="text-align:center; color:#777; padding:20px;">Loading Data...</div>
                </div>
            </div>
        </div>

        <div id="tab-log" class="tab-content">
            <div style="background:rgba(20,20,20,0.6); backdrop-filter:blur(6px); border:1px solid #d4af37; border-radius:10px; padding:10px; display:flex; flex-direction:column; height:100%;">
                <div style="font-size:10px; color:#ffdf73; font-weight:900; text-align:center; margin-bottom:5px;">📜 REAL HISTORY LOG</div>
                <div class="log-list" id="logList">
                    <div style="text-align:center; color:#777; padding:20px;">Waiting for real round...</div>
                </div>
            </div>
        </div>

        <div id="tab-profile" class="tab-content">
            <div style="background:rgba(20,20,20,0.6); backdrop-filter:blur(6px); border:1px solid #d4af37; border-radius:10px; padding:10px; text-align:left;">
                <div style="font-size:10px; color:#ffdf73; font-weight:900; text-align:center; margin-bottom:8px;">👑 USER PROFILE</div>
                <div class="profile-card">
                    <p>Active Key: <span style="color:#00ff88;">{{ session.get('active_key', 'N/A') }}</span></p>
                    <p>License Status: <span style="color:#00ff88;">Active VIP</span></p>
                    <p>Time Remaining: <span id="profileKeyTimer" style="color:#ffdf73;">Calculating...</span></p>
                    <p>Server: <span style="color:#ffdf73;">Engine Win-Tracking Server</span></p>
                    <br>
                    <a href="/logout" style="display:block; text-align:center; background:linear-gradient(45deg, #ff4444, #cc0000); color:#fff; text-decoration:none; padding:10px; border-radius:8px; font-weight:900; font-size:13px; box-shadow:0 4px 10px rgba(255,0,0,0.4);">LOGOUT ACCOUNT</a>
                </div>
            </div>
        </div>

        <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('terminal', this)"><div>📈</div>TERMINAL</div>
            <div class="nav-item" onclick="switchTab('pattern', this)"><div>📊</div>PATTERN</div>
            <div class="nav-item" onclick="switchTab('log', this)"><div>📜</div>LOG</div>
            <div class="nav-item" onclick="switchTab('stats', this)"><div>🤖</div>STATS</div>
            <div class="nav-item" onclick="switchTab('profile', this)"><div>👑</div>PROFILE</div>
        </div>
    </div>

    <script>
        const WORKER_URL = "https://wingo-cloudflare-worker.anishanisha143love.workers.dev";
        const KEY_EXPIRE_ISO = "{{ session.get('key_expire_iso', '') }}";
        
        let totalRounds = 0, winsCount = 0, lossesCount = 0, jackpotsCount = 0;
        let historyLogs = [];
        let hasRevealedThisRound = false; 
        let isAnalyzing = false;
        let lastEvaluatedIssue = null;

        let lockedPeriod = null;
        let currentPredType = "WAITING";
        let currentPredNum = 0;

        let lastRoundWasLoss = false, lastMajorityType = null;
        let warnTriggered120 = false, warnTriggered90 = false, warnTriggered60 = false, warnTriggered30 = false;

        // Individual Engine Win Counters
        let engineWins = Array(16).fill(0);
        let lastEnginePreds = Array(16).fill(null);

        const CHART_MAP = {
            0: { size:"BIG", n1:0, n2:5 }, 1: { size:"SMALL", n1:1, n2:6 },
            2: { size:"BIG", n1:2, n2:7 }, 3: { size:"BIG", n1:3, n2:8 },
            4: { size:"SMALL", n1:4, n2:0 }, 5: { size:"BIG", n1:5, n2:0 },
            6: { size:"BIG", n1:6, n2:1 }, 7: { size:"SMALL", n1:7, n2:2 },
            8: { size:"BIG", n1:8, n2:3 }, 9: { size:"SMALL", n1:0, n2:1 }
        };

        let audioUnlocked = false;
        function unlockAudio() {
            if (audioUnlocked) return;
            try {
                const a = new Audio("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3");
                a.volume = 0.01; a.play().then(()=>{audioUnlocked=true;}).catch(e=>{});
            } catch(e) {}
        }
        document.addEventListener('click', unlockAudio, { once: true });
        document.addEventListener('touchstart', unlockAudio, { once: true });

        function playWarningBeep() {
            try { const a = new Audio("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"); a.volume = 1.0; a.play().catch(e=>{}); } catch(e) {}
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

        function updateClock() {
            const now = new Date();
            let hours = now.getHours(), minutes = now.getMinutes(), seconds = now.getSeconds();
            let ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12; hours = hours ? hours : 12;
            document.getElementById('currentTime').innerText = `${hours}:${minutes<10?'0'+minutes:minutes}:${seconds<10?'0'+seconds:seconds} ${ampm}`;
            document.getElementById('currentDate').innerText = `${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}/${now.getFullYear()}`;
        }
        setInterval(updateClock, 1000); updateClock();

        function switchTab(tabName, element) {
            try {
                const actx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = actx.createOscillator(), gn = actx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(587.33, actx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(880, actx.currentTime + 0.15);
                gn.gain.setValueAtTime(0.15, actx.currentTime); gn.gain.exponentialRampToValueAtTime(0.01, actx.currentTime + 0.2);
                osc.connect(gn); gn.connect(actx.destination); osc.start(); osc.stop(actx.currentTime + 0.2);
            } catch(e) {}
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            element.classList.add('active');
        }

        function getColorClass(num, type) {
            if (num === 0 || num === 5) return 'color-violet';
            if (type === 'BIG') return 'color-green';
            if (type === 'SMALL') return 'color-red';
            return 'color-wait';
        }

        function revealPrediction() {
            if (hasRevealedThisRound || isAnalyzing || currentPredType === "WAITING") return;
            
            isAnalyzing = true;
            const pedestal = document.getElementById('mainPedestal');
            const inner = document.getElementById('predDisplay');
            
            pedestal.classList.add('analyzing-effect');
            inner.className = "prediction-display color-wait";
            inner.innerHTML = "⚡ ANALYZING... ⚡";

            try {
                const scanAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3");
                scanAudio.volume = 0.6; scanAudio.play().catch(e=>{});
            } catch(e) {}

            setTimeout(() => {
                isAnalyzing = false;
                hasRevealedThisRound = true;
                pedestal.classList.remove('analyzing-effect');
                
                try {
                    const dtAudio = new Audio("https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3");
                    dtAudio.volume = 1.0; dtAudio.play().catch(e=>{});
                } catch(e) {}

                inner.className = `prediction-display ${getColorClass(currentPredNum, currentPredType)}`;
                inner.innerHTML = `${currentPredType} : ${currentPredNum}`;
            }, 4000);
        }

        function showWinToast() {
            const toast = document.getElementById('winToast');
            toast.classList.add('show');
            document.getElementById('mainPedestal').classList.add('pedestal-win-flash');
            try { 
                const w = new Audio("https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"); 
                w.volume = 1.0; w.play().catch(e=>{}); 
            } catch(e) {}
            setTimeout(() => { 
                toast.classList.remove('show'); 
                document.getElementById('mainPedestal').classList.remove('pedestal-win-flash');
            }, 3500);
        }

        function showJackpotOverlay(targetNum, targetType) {
            const overlay = document.getElementById('jackpotOverlay');
            const sub = document.getElementById('jpSubText');
            sub.innerText = `JACKPOT TARGET: ${targetType} : ${targetNum} (15 Engines Verified)`;
            overlay.style.display = 'flex';
            try { 
                const jp = new Audio("https://assets.mixkit.co/active_storage/sfx/2020/2020-preview.mp3"); 
                jp.volume = 1.0; jp.play().catch(e=>{}); 
            } catch(e) {}
            setTimeout(() => { overlay.style.display = 'none'; }, 5000);
        }

        function getLiveUTCPeriod() {
            const now = new Date();
            const totalMins = now.getUTCHours() * 60 + now.getUTCMinutes();
            const serial = 10000 + totalMins + 1;
            return `${now.getUTCFullYear()}${String(now.getUTCMonth()+1).padStart(2,'0')}${String(now.getUTCDate()).padStart(2,'0')}1000${serial}`;
        }

        async function fetch500Results() {
            let combinedList = [];
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
                if (items.length >= 5) {
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

                        // Evaluate Individual Engine Wins based on last recorded engine predictions
                        for(let j=1; j<=15; j++) {
                            if (lastEnginePreds[j] === actType) {
                                engineWins[j]++;
                            }
                            const wEl = document.getElementById('winCnt' + j);
                            if (wEl) wEl.innerText = `(${engineWins[j]} Wins)`;
                        }

                        if (currentPredType === actType && currentPredNum === actNum && hasRevealedThisRound) {
                            jackpotsCount++; winsCount++; statusRes = "JACKPOT";
                            showJackpotOverlay(currentPredNum, currentPredType);
                            lastRoundWasLoss = false;
                        } else if (currentPredType === actType && hasRevealedThisRound) {
                            winsCount++; statusRes = "WIN";
                            showWinToast();
                            lastRoundWasLoss = false;
                        } else {
                            if (hasRevealedThisRound) lossesCount++; 
                            statusRes = "LOSS";
                            lastRoundWasLoss = true;
                        }

                        if (hasRevealedThisRound) {
                            historyLogs.unshift({ issue: lastEvaluatedIssue, pred: `${currentPredType} : ${currentPredNum}`, act_type: actType, act_num: actNum, status: statusRes });
                            if (historyLogs.length > 50) historyLogs.pop();
                            updateLogUI();
                        }

                        hasRevealedThisRound = false;
                        isAnalyzing = false;
                        document.getElementById('predDisplay').className = 'prediction-display color-wait';
                        document.getElementById('predDisplay').innerHTML = `CHECK RESULT`;
                    }

                    updateBdgChartUI(items);

                    let currentActivePeriod = getLiveUTCPeriod();
                    
                    const pool = items.slice(0, 500);
                    const lastN = parseInt(pool[0].number, 10);
                    const lastT = lastN >= 5 ? "BIG" : "SMALL";
                    const prevT = parseInt(pool[1].number, 10) >= 5 ? "BIG" : "SMALL";

                    let predE1 = (lastT === "BIG") ? "SMALL" : "BIG";
                    if (pool.length > 10) {
                        let matchCount = 0;
                        let nextTrendSum = 0;
                        let currentPattern = `${parseInt(pool[1].number,10)>=5?"B":"S"}-${lastT[0]}`;
                        for(let i=2; i<pool.length-1; i++) {
                            let histPattern = `${parseInt(pool[i+1].number,10)>=5?"B":"S"}-${parseInt(pool[i].number,10)>=5?"B":"S"}`;
                            if(histPattern === currentPattern) {
                                matchCount++;
                                let nxtType = parseInt(pool[i-1].number,10)>=5 ? "BIG" : "SMALL";
                                if(nxtType === "BIG") nextTrendSum++; else nextTrendSum--;
                            }
                        }
                        if(matchCount >= 2) {
                            let expectedHist = (nextTrendSum >= 0) ? "BIG" : "SMALL";
                            predE1 = (expectedHist === "BIG") ? "SMALL" : "BIG";
                        }
                    }

                    let numFreq = Array(10).fill(0);
                    let bigC = 0, smallC = 0;
                    for (let i = 0; i < pool.length - 1; i++) {
                        if (parseInt(pool[i + 1].number, 10) === lastN) {
                            let nxt = parseInt(pool[i].number, 10);
                            numFreq[nxt]++;
                            if (nxt >= 5) bigC++; else smallC++;
                        }
                    }
                    let predE2 = bigC >= smallC ? "BIG" : "SMALL";
                    let bestNumE2 = numFreq.indexOf(Math.max(...numFreq));

                    let streak = 1;
                    for(let i=1; i<pool.length; i++) {
                        let t = parseInt(pool[i].number,10)>=5 ? "BIG" : "SMALL";
                        if(t === lastT) streak++; else break;
                    }
                    let predE3 = (streak >= 3) ? lastT : ((lastT === "BIG") ? "SMALL" : "BIG");

                    let predE4 = lastT; 
                    let t1 = parseInt(pool[1].number,10)>=5?"BIG":"SMALL";
                    let t2 = parseInt(pool[2].number,10)>=5?"BIG":"SMALL";
                    if (lastT === t1 && t1 !== t2) predE4 = (lastT === "BIG") ? "SMALL" : "BIG";

                    let predE5 = lastT;
                    if (lastT !== t1 && t1 !== t2) predE5 = (lastT === "BIG") ? "SMALL" : "BIG";

                    let predE6 = lastT;
                    if (lastRoundWasLoss && lastMajorityType) {
                        predE6 = (lastMajorityType === "BIG") ? "SMALL" : "BIG";
                    }

                    let n0 = parseInt(pool[0].number); let n1 = parseInt(pool[1].number);
                    let n2 = parseInt(pool[2].number); let n3 = parseInt(pool[3].number);
                    let n4 = parseInt(pool[4].number);
                    let mathVal = (n0 + n1 + n2 - n3 - n4) % 10;
                    if (mathVal < 0) mathVal += 10;
                    let predE7 = mathVal >= 5 ? "BIG" : "SMALL";

                    let cons = 1;
                    for(let i=1; i<pool.length; i++) {
                        let t = parseInt(pool[i].number,10)>=5 ? "BIG" : "SMALL";
                        if(t === lastT) cons++; else break;
                    }
                    let predE8 = (cons >= 3) ? lastT : ((lastT === "BIG") ? "SMALL" : "BIG");

                    let chartEntry = CHART_MAP[lastN];
                    let predE9 = chartEntry ? chartEntry.size : lastT;
                    let targetN1 = chartEntry ? chartEntry.n1 : 0;

                    let predE10 = (cons === 2) ? ((lastT === "BIG") ? "SMALL" : "BIG") : lastT;
                    let predE11 = (cons >= 3) ? lastT : ((lastT === "BIG") ? "SMALL" : "BIG");
                    let predE12 = (lastT === prevT) ? ((lastT === "BIG") ? "SMALL" : "BIG") : lastT;

                    let predE13 = lastT;
                    if (lastRoundWasLoss) predE13 = (lastT === "BIG") ? "SMALL" : "BIG";

                    let predE14 = (predE9 === predE8) ? predE9 : lastT;
                    let predE15 = (mathVal >= 5) ? "BIG" : "SMALL";

                    // Save current predictions to check win counts on next evaluation cycle
                    lastEnginePreds = [null, predE1, predE2, predE3, predE4, predE5, predE6, predE7, predE8, predE9, predE10, predE11, predE12, predE13, predE14, predE15];

                    updateUIEngine('uiEng1', predE1);
                    updateUIEngine('uiEng2', predE2);
                    updateUIEngine('uiEng3', predE3);
                    updateUIEngine('uiEng4', predE4);
                    updateUIEngine('uiEng5', predE5);
                    updateUIEngine('uiEng6', predE6);
                    updateUIEngine('uiEng7', predE7);
                    updateUIEngine('uiEng8', predE8);
                    updateUIEngine('uiEng9', predE9);
                    updateUIEngine('uiEng10', predE10);
                    updateUIEngine('uiEng11', predE11);
                    updateUIEngine('uiEng12', predE12);
                    updateUIEngine('uiEng13', predE13);
                    updateUIEngine('uiEng14', predE14);
                    updateUIEngine('uiEng15', predE15);

                    let validVotes = [predE1, predE2, predE3, predE4, predE5, predE6, predE7, predE8, predE9, predE10, predE11, predE12, predE13, predE14, predE15].filter(v => v === "BIG" || v === "SMALL");
                    let voteB = validVotes.filter(v => v === "BIG").length;
                    let voteS = validVotes.filter(v => v === "SMALL").length;

                    let calcPredT = (voteB >= voteS) ? "BIG" : "SMALL";
                    lastMajorityType = calcPredT;
                    
                    let calcPredN = targetN1;
                    if (bestNumE2 >= 5 && calcPredT === "BIG") calcPredN = bestNumE2;
                    if (bestNumE2 < 5 && calcPredT === "SMALL") calcPredN = bestNumE2;
                    let subPool = calcPredT === "BIG" ? [5,6,7,8,9] : [0,1,2,3,4];
                    if (!subPool.includes(calcPredN)) calcPredN = mathVal;

                    if (lockedPeriod !== currentActivePeriod) {
                        lockedPeriod = currentActivePeriod;
                        currentPredType = calcPredT;
                        currentPredNum = calcPredN;
                    }

                    document.getElementById('uiEngFinal').className = calcPredT === "BIG" ? "color-green" : "color-red";
                    document.getElementById('uiEngFinal').innerText = `${calcPredT} (Votes: ${voteB >= voteS ? voteB : voteS}/${validVotes.length})`;

                    lastEvaluatedIssue = actIssue;

                    document.getElementById('statTotal').innerText = totalRounds;
                    document.getElementById('statWins').innerText = winsCount;
                    document.getElementById('statLosses').innerText = lossesCount;
                    document.getElementById('statJackpots').innerText = jackpotsCount;
                    document.getElementById('statTotal2').innerText = totalRounds;
                    let acc = totalRounds > 0 ? ((winsCount / totalRounds) * 100).toFixed(1) : "0.0";
                    document.getElementById('statAccuracy').innerText = acc + "%";
                }
            } catch(e) { console.error("Fetch error"); }
        }

        function updateBdgChartUI(items) {
            const container = document.getElementById('tirangaPatternList');
            let html = '';
            items.slice(0, 40).forEach((item) => {
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
                html += `<div class="tiranga-row"><div class="tiranga-period">${String(item.issueNumber).slice(-4)}</div><div class="tiranga-nums">${circlesHtml}</div></div>`;
            });
            container.innerHTML = html;
        }

        function updateLogUI() {
            const listEl = document.getElementById('logList');
            if (historyLogs.length === 0) return;
            let html = '';
            historyLogs.forEach(log => {
                let badge = log.status === 'WIN' ? '<span class="badge-win">WIN ✅</span>' :
                            log.status === 'JACKPOT' ? '<span class="badge-win" style="color:#ffcc00; border-color:#ffcc00;">JACKPOT 🌟</span>' :
                            '<span class="badge-loss">LOSS ❌</span>';
                let actColor = log.act_type === 'BIG' ? '#00ff88' : '#ff4444';
                html += `
                <div class="log-item">
                    <div>
                        <div style="color:#aaa; font-size:9px;">Period: ${log.issue}</div>
                        <div style="color:#fff; font-weight:900;">Pred: ${log.pred} | Act: <span style="color:${actColor}">${log.act_type} (${log.act_num})</span></div>
                    </div>
                    <div>${badge}</div>
                </div>`;
            });
            listEl.innerHTML = html;
        }

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
                        doc = doc.get()
                    if not doc.exists:
                        doc_ref = db.collection('trustwin_keys').document(key)
                        doc = doc.get()

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
                                    created_dt = created_val.replace(tzinfo=timezone.utc) if created_val.tzinfo is None else created_dt.astimezone(timezone.utc)
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

@app.route('/')
def home():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
