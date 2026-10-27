from flask import Flask, jsonify, render_template_string
import serial
import threading
import re
import time

app = Flask(__name__)

# =====================================
# ARDUINO SETTINGS & STATE
# =====================================
ARDUINO_PORT = "COM7"
BAUD_RATE = 9600
THRESHOLD = 400

gas_value = 0
peak_value = 0
gas_status = "NORMAL"
led_status = "OFF"
fan_status = "OFF"
last_update = "Waiting for Arduino..."
arduino_connected = False


# =====================================
# DASHBOARD HTML TEMPLATE
# =====================================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisGuard | Smart Gas Leak Detection & Safety System</title>
    
    <!-- Modern Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg-base: #080c14;
            --bg-surface: #0f172a;
            --bg-card: rgba(17, 26, 44, 0.75);
            --bg-card-hover: rgba(23, 35, 60, 0.85);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(255, 255, 255, 0.16);
            
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            --safe-color: #10b981;
            --safe-bg: rgba(16, 185, 129, 0.12);
            --safe-glow: rgba(16, 185, 129, 0.35);
            --safe-border: rgba(16, 185, 129, 0.3);
            
            --warn-color: #f59e0b;
            --warn-bg: rgba(245, 158, 11, 0.12);
            
            --danger-color: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.14);
            --danger-glow: rgba(239, 68, 68, 0.5);
            --danger-border: rgba(239, 68, 68, 0.45);
            
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(16, 185, 129, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 85% 20%, rgba(59, 130, 246, 0.04) 0%, transparent 45%),
                linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
            color: var(--text-primary);
            font-family: var(--font-sans);
            min-height: 100vh;
            padding-bottom: 50px;
            overflow-x: hidden;
            transition: background 0.4s ease;
        }

        body.danger-mode {
            background-image: 
                radial-gradient(circle at 50% 20%, rgba(239, 68, 68, 0.18) 0%, transparent 60%),
                radial-gradient(circle at 15% 85%, rgba(239, 68, 68, 0.08) 0%, transparent 45%),
                linear-gradient(rgba(239, 68, 68, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(239, 68, 68, 0.03) 1px, transparent 1px);
        }

        /* TOP NAVIGATION BAR */
        .topbar {
            background: rgba(11, 17, 30, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 14px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand-group {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
            color: #ffffff;
            transition: all 0.4s ease;
        }

        body.danger-mode .brand-icon {
            background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.6);
            animation: pulse-hazard 1.5s infinite;
        }

        .brand-title h1 {
            font-size: 19px;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .brand-badge {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 7px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-secondary);
            letter-spacing: 0.05em;
        }

        .brand-title p {
            font-size: 12px;
            color: var(--text-secondary);
            font-family: var(--font-mono);
            margin-top: 1px;
        }

        .controls-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .btn-ctrl {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 600;
            padding: 8px 14px;
            border-radius: 10px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }

        .btn-ctrl:hover {
            background: rgba(255, 255, 255, 0.12);
            color: var(--text-primary);
            border-color: var(--border-highlight);
        }

        .btn-ctrl.active {
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--safe-color);
            color: var(--safe-color);
        }

        .status-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 14px;
            border-radius: 30px;
            font-size: 12px;
            font-weight: 600;
            font-family: var(--font-mono);
            background: rgba(16, 185, 129, 0.1);
            color: var(--safe-color);
            border: 1px solid var(--safe-border);
            transition: all 0.3s ease;
        }

        .status-chip.disconnected {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger-color);
            border-color: var(--danger-border);
        }

        .dot-ping {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: currentColor;
            box-shadow: 0 0 10px currentColor;
            position: relative;
        }

        .dot-ping::after {
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            border-radius: 50%;
            border: 2px solid currentColor;
            animation: ring-pulse 1.8s infinite cubic-bezier(0.4, 0, 0.6, 1);
            opacity: 0.6;
        }

        @keyframes ring-pulse {
            0% { transform: scale(0.8); opacity: 0.9; }
            100% { transform: scale(2.4); opacity: 0; }
        }

        @keyframes pulse-hazard {
            0%, 100% { transform: scale(1); filter: brightness(1); }
            50% { transform: scale(1.05); filter: brightness(1.25); }
        }

        /* MAIN WRAPPER */
        .dashboard-container {
            max-width: 1320px;
            margin: 28px auto 0;
            padding: 0 24px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        /* EMERGENCY HERO BANNER */
        .hero-banner {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid var(--border-subtle);
            padding: 24px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            overflow: hidden;
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .hero-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            width: 6px;
            background: var(--safe-color);
            transition: background 0.35s ease;
        }

        .hero-banner.normal {
            border-color: var(--safe-border);
            box-shadow: 0 10px 30px -10px var(--safe-glow);
        }

        .hero-banner.normal::before {
            background: var(--safe-color);
        }

        .hero-banner.danger {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.16) 0%, rgba(15, 23, 42, 0.9) 100%);
            border-color: var(--danger-color);
            box-shadow: 0 0 40px rgba(239, 68, 68, 0.4);
            animation: banner-flash 1.6s infinite alternate ease-in-out;
        }

        .hero-banner.danger::before {
            background: var(--danger-color);
            width: 8px;
        }

        @keyframes banner-flash {
            0% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.25); }
            100% { box-shadow: 0 0 50px rgba(239, 68, 68, 0.6); }
        }

        .hero-content {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .hero-status-icon {
            width: 58px;
            height: 58px;
            border-radius: 16px;
            background: var(--safe-bg);
            border: 1px solid var(--safe-border);
            color: var(--safe-color);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: all 0.3s ease;
        }

        .hero-banner.danger .hero-status-icon {
            background: var(--danger-bg);
            border-color: var(--danger-color);
            color: var(--danger-color);
            animation: pulse-hazard 1.2s infinite;
        }

        .hero-texts h2 {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.01em;
            margin-bottom: 4px;
        }

        .hero-texts p {
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
            max-width: 680px;
        }

        .hero-meta {
            text-align: right;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
        }

        .threat-pill {
            display: inline-block;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: 20px;
            background: var(--safe-bg);
            color: var(--safe-color);
            border: 1px solid var(--safe-border);
        }

        .hero-banner.danger .threat-pill {
            background: var(--danger-bg);
            color: var(--danger-color);
            border-color: var(--danger-color);
        }

        .hero-time {
            font-family: var(--font-mono);
            font-size: 12px;
            color: var(--text-muted);
        }

        /* EMERGENCY ACTION CHECKLIST */
        .emergency-action-bar {
            display: none;
            background: rgba(239, 68, 68, 0.12);
            border: 1px dashed rgba(239, 68, 68, 0.5);
            border-radius: 14px;
            padding: 16px 20px;
            margin-top: 14px;
            color: #fca5a5;
            font-size: 13px;
        }

        .emergency-action-bar.visible {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }

        .action-steps {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }

        .step-num {
            background: var(--danger-color);
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
        }

        /* METRICS CARDS GRID (5 Cards) */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }

        .metric-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: 18px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            transition: all 0.25s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: var(--border-highlight);
            background: var(--bg-card-hover);
        }

        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .metric-label {
            font-size: 11px;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .metric-icon-small {
            width: 30px;
            height: 30px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
        }

        .metric-value-wrap {
            display: flex;
            align-items: baseline;
            gap: 8px;
            margin: 4px 0 8px;
        }

        .metric-value {
            font-family: var(--font-mono);
            font-size: 34px;
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.03em;
            color: var(--text-primary);
        }

        .metric-unit {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            font-family: var(--font-sans);
        }

        .metric-footer {
            margin-top: auto;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* HARDWARE ACTUATORS (LED & FAN) */
        .actuator-row {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .led-diode {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #2b1115;
            border: 2px solid #57161d;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
            transition: all 0.3s ease;
        }

        .led-diode.on {
            background: #ef4444;
            border-color: #fca5a5;
            box-shadow: 0 0 15px #ef4444, 0 0 25px rgba(239, 68, 68, 0.7);
            animation: led-strobe 0.8s infinite alternate ease-in-out;
        }

        @keyframes led-strobe {
            0% { filter: brightness(1); }
            100% { filter: brightness(1.35); }
        }

        .fan-spinner {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            transition: all 0.3s ease;
        }

        .fan-spinner.spinning {
            color: var(--accent-cyan);
            animation: fan-rotate 0.6s linear infinite;
        }

        @keyframes fan-rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* TWO-COLUMN ANALYTICS ROW */
        .analytics-row {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        .chart-card, .gauge-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 24px;
            display: flex;
            flex-direction: column;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .section-header h3 {
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chart-legend {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .legend-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .legend-dot.ppm { background: var(--accent-cyan); }
        .legend-dot.threshold { background: var(--danger-color); }

        .canvas-container {
            width: 100%;
            height: 230px;
            position: relative;
        }

        #historyChart {
            width: 100%;
            height: 100%;
            display: block;
        }

        /* RADIAL GAUGE CARD */
        .gauge-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 10px 0;
            position: relative;
        }

        #radialGauge {
            width: 220px;
            height: 140px;
        }

        .gauge-readout {
            position: absolute;
            top: 75px;
            text-align: center;
        }

        .gauge-readout .gauge-number {
            font-family: var(--font-mono);
            font-size: 32px;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1;
        }

        .gauge-readout .gauge-sub {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }

        .gauge-zones {
            display: flex;
            width: 100%;
            justify-content: space-between;
            margin-top: 15px;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            font-size: 12px;
        }

        .gauge-zone-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--text-secondary);
        }

        /* SYSTEM SPECS & EVENT LOG SECTION */
        .bottom-row {
            display: grid;
            grid-template-columns: 1fr 1.3fr;
            gap: 20px;
        }

        .specs-card, .log-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 24px;
        }

        .specs-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 14px;
        }

        .spec-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 14px 16px;
            transition: background 0.2s;
        }

        .spec-item:hover {
            background: rgba(255, 255, 255, 0.06);
        }

        .spec-item span {
            display: block;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 5px;
        }

        .spec-item strong {
            font-size: 14px;
            color: var(--text-primary);
            font-family: var(--font-mono);
            font-weight: 600;
        }

        /* EVENT LOG STREAM */
        .log-container {
            height: 185px;
            overflow-y: auto;
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-family: var(--font-mono);
            font-size: 12px;
        }

        .log-container::-webkit-scrollbar {
            width: 6px;
        }

        .log-container::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }

        .log-entry {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            line-height: 1.4;
            color: var(--text-secondary);
        }

        .log-time {
            color: var(--text-muted);
            flex-shrink: 0;
        }

        .log-badge {
            font-size: 10px;
            font-weight: 700;
            padding: 1px 6px;
            border-radius: 4px;
            text-transform: uppercase;
            flex-shrink: 0;
        }

        .log-badge.info { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
        .log-badge.normal { background: rgba(16, 185, 129, 0.15); color: #34d399; }
        .log-badge.alarm { background: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: 800; }

        .log-msg {
            color: var(--text-primary);
        }

        /* FOOTER */
        .footer {
            margin-top: 36px;
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
        }

        /* RESPONSIVE */
        @media (max-width: 1200px) {
            .metrics-grid { grid-template-columns: repeat(3, 1fr); }
        }
        @media (max-width: 900px) {
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .analytics-row { grid-template-columns: 1fr; }
            .bottom-row { grid-template-columns: 1fr; }
        }
        @media (max-width: 600px) {
            .metrics-grid { grid-template-columns: 1fr; }
            .topbar { flex-direction: column; align-items: flex-start; gap: 12px; }
            .controls-group { width: 100%; justify-content: space-between; }
        }
    </style>
</head>
<body>

    <!-- TOP NAVIGATION BAR -->
    <header class="topbar">
        <div class="brand-group">
            <div class="brand-icon" id="brandIcon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path>
                </svg>
            </div>
            <div class="brand-title">
                <h1>AEGIS GASGUARD <span class="brand-badge">IoT PRO</span></h1>
                <p>Arduino UNO &middot; MQ-2 Gas &middot; Relay Fan &middot; COM7</p>
            </div>
        </div>

        <div class="controls-group">
            <button class="btn-ctrl" id="soundToggleBtn" onclick="toggleSound()">
                <svg id="soundIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <line x1="23" y1="9" x2="17" y2="15"></line>
                    <line x1="17" y1="9" x2="23" y2="15"></line>
                </svg>
                <span id="soundLabel">Siren Muted</span>
            </button>

            <button class="btn-ctrl" id="simToggleBtn" onclick="toggleSimulation()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                </svg>
                <span>Test Alert</span>
            </button>

            <div class="status-chip" id="connChip">
                <span class="dot-ping"></span>
                <span id="connLabel">Arduino Connecting...</span>
            </div>
        </div>
    </header>

    <!-- MAIN DASHBOARD CONTENT -->
    <main class="dashboard-container">

        <!-- HERO ALERT BANNER -->
        <section class="hero-banner normal" id="heroBanner">
            <div class="hero-content">
                <div class="hero-status-icon" id="heroIcon">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        <polyline points="9 12 11 14 15 10"></polyline>
                    </svg>
                </div>
                <div class="hero-texts">
                    <h2 id="heroTitle">ATMOSPHERE NOMINAL — ENVIRONMENT SAFE</h2>
                    <p id="heroMsg">MQ-2 analog hydrocarbon telemetry is within normal baseline parameters. Interlocks D6 (LED) and D7 (Relay Fan) are dormant.</p>
                </div>
            </div>
            <div class="hero-meta">
                <span class="threat-pill" id="threatPill">DEFCON 5 &middot; NORMAL</span>
                <div class="hero-time">Last update: <span id="heroTime">--:--:--</span></div>
            </div>
        </section>

        <!-- EMERGENCY ACTION CHECKLIST (Revealed when Gas Detected) -->
        <div class="emergency-action-bar" id="emergencyActionBar">
            <div class="step-item" style="color: #ffffff; font-weight: 700;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                CRITICAL LEAK PROTOCOL:
            </div>
            <div class="action-steps">
                <div class="step-item"><span class="step-num">1</span> Evacuate area immediately</div>
                <div class="step-item"><span class="step-num">2</span> Do not touch electrical switches</div>
                <div class="step-item"><span class="step-num">3</span> Open windows & ventilate</div>
                <div class="step-item"><span class="step-num">4</span> Relay Cooling Fan active (D7)</div>
                <div class="step-item"><span class="step-num">5</span> Shut off cylinder valve</div>
            </div>
        </div>

        <!-- 5-CARD TELEMETRY GRID -->
        <section class="metrics-grid">

            <!-- CARD 1: GAS LEVEL -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Gas Concentration</span>
                    <div class="metric-icon-small">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                    </div>
                </div>
                <div class="metric-value-wrap">
                    <div class="metric-value" id="gasValueDisplay">0</div>
                    <span class="metric-unit">ADC Raw</span>
                </div>
                <div class="metric-footer">
                    <span>Baseline: 150 - 250</span>
                    <span id="gasDelta" style="font-family: var(--font-mono); font-weight: 600;">--</span>
                </div>
            </div>

            <!-- CARD 2: SAFETY STATUS -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Safety Status</span>
                    <div class="metric-icon-small">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="m9 12 2 2 4-4"></path>
                        </svg>
                    </div>
                </div>
                <div class="metric-value-wrap">
                    <div class="metric-value" id="statusDisplay" style="font-size: 24px; color: var(--safe-color);">NORMAL</div>
                </div>
                <div class="metric-footer">
                    <span>State</span>
                    <span id="statusSub">Clean Air</span>
                </div>
            </div>

            <!-- CARD 3: HARDWARE LED PIN D6 -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Alarm LED (Pin D6)</span>
                    <div class="metric-icon-small">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="6"></circle>
                            <line x1="12" y1="2" x2="12" y2="4"></line>
                            <line x1="12" y1="20" x2="12" y2="22"></line>
                        </svg>
                    </div>
                </div>
                <div class="metric-value-wrap">
                    <div class="actuator-row">
                        <div class="led-diode" id="ledDiode"></div>
                        <div class="metric-value" id="ledDisplay" style="font-size: 24px;">OFF</div>
                    </div>
                </div>
                <div class="metric-footer">
                    <span>Visual Strobe</span>
                    <span id="ledPinStatus">Digital Out</span>
                </div>
            </div>

            <!-- CARD 4: COOLING FAN (RELAY PIN D7) -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Relay Fan (Pin D7)</span>
                    <div class="metric-icon-small">
                        <svg class="fan-spinner" id="fanSpinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="M12 12c-2-2-2-5 0-7 2 2 2 5 0 7z"></path>
                            <path d="M12 12c2 2 5 2 7 0-2-2-5-2-7 0z"></path>
                            <path d="M12 12c2-2 2-5 0-7-2 2-2 5 0 7z"></path>
                            <path d="M12 12c-2 2-5 2-7 0 2-2 5-2 7 0z"></path>
                        </svg>
                    </div>
                </div>
                <div class="metric-value-wrap">
                    <div class="metric-value" id="fanDisplay" style="font-size: 24px;">OFF</div>
                </div>
                <div class="metric-footer">
                    <span>Exhaust Extraction</span>
                    <span id="fanStatusSub">Relay Normal</span>
                </div>
            </div>

            <!-- CARD 5: THRESHOLD & PEAK -->
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-label">Alarm Threshold</span>
                    <div class="metric-icon-small">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                        </svg>
                    </div>
                </div>
                <div class="metric-value-wrap">
                    <div class="metric-value" style="color: #f59e0b;">400</div>
                    <span class="metric-unit">ADC Trigger</span>
                </div>
                <div class="metric-footer">
                    <span>Peak Recorded:</span>
                    <span id="peakDisplay" style="font-family: var(--font-mono); font-weight: 700; color: var(--text-primary);">0</span>
                </div>
            </div>

        </section>

        <!-- ANALYTICS ROW: LIVE CHART + RADIAL GAUGE -->
        <section class="analytics-row">

            <!-- REAL-TIME STREAM CHART -->
            <div class="chart-card">
                <div class="section-header">
                    <h3>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                        Live Hydrocarbon Sensor Telemetry (Rolling 30s)
                    </h3>
                    <div class="chart-legend">
                        <div class="legend-item">
                            <span class="legend-dot ppm"></span>
                            <span>MQ-2 Value</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot threshold"></span>
                            <span>Alarm Threshold (400)</span>
                        </div>
                    </div>
                </div>
                <div class="canvas-container">
                    <canvas id="historyChart"></canvas>
                </div>
            </div>

            <!-- CIRCULAR GAUGE METER -->
            <div class="gauge-card">
                <div class="section-header">
                    <h3>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        Concentration Meter
                    </h3>
                </div>
                <div class="gauge-wrapper">
                    <canvas id="radialGauge"></canvas>
                    <div class="gauge-readout">
                        <div class="gauge-number" id="gaugeValueText">0</div>
                        <div class="gauge-sub" id="gaugeStatusText">0 - 1023 ADC</div>
                    </div>
                </div>
                <div class="gauge-zones">
                    <div class="gauge-zone-pill">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span>
                        <span>0-250 Safe</span>
                    </div>
                    <div class="gauge-zone-pill">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #f59e0b;"></span>
                        <span>250-400 Warn</span>
                    </div>
                    <div class="gauge-zone-pill">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #ef4444;"></span>
                        <span>400+ Danger</span>
                    </div>
                </div>
            </div>

        </section>

        <!-- SYSTEM DIAGNOSTICS & EVENT LOG -->
        <section class="bottom-row">

            <!-- HARDWARE DIAGNOSTICS -->
            <div class="specs-card">
                <div class="section-header">
                    <h3>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
                            <rect x="9" y="9" width="6" height="6"></rect>
                            <line x1="9" y1="1" x2="9" y2="4"></line>
                            <line x1="15" y1="1" x2="15" y2="4"></line>
                            <line x1="9" y1="20" x2="9" y2="23"></line>
                            <line x1="15" y1="20" x2="15" y2="23"></line>
                        </svg>
                        Hardware & Pin Configuration
                    </h3>
                </div>
                <div class="specs-grid">
                    <div class="spec-item">
                        <span>Microcontroller</span>
                        <strong>Arduino UNO (R3)</strong>
                    </div>
                    <div class="spec-item">
                        <span>Serial Port</span>
                        <strong>COM7 @ 9600 8N1</strong>
                    </div>
                    <div class="spec-item">
                        <span>Gas Sensor</span>
                        <strong>Hanwei MQ-2 (A0)</strong>
                    </div>
                    <div class="spec-item">
                        <span>Alarm LED</span>
                        <strong>Pin D6 (Digital Out)</strong>
                    </div>
                    <div class="spec-item">
                        <span>Cooling Exhaust Fan</span>
                        <strong>Relay Pin D7 (Actuator)</strong>
                    </div>
                    <div class="spec-item">
                        <span>Threshold Trigger</span>
                        <strong>400 ADC (Automatic Fan)</strong>
                    </div>
                </div>
            </div>

            <!-- INCIDENT STREAM LOG -->
            <div class="log-card">
                <div class="section-header">
                    <h3>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="4 17 10 11 4 5"></polyline>
                            <line x1="12" y1="19" x2="20" y2="19"></line>
                        </svg>
                        Telemetry Event Stream
                    </h3>
                    <button class="btn-ctrl" style="padding: 4px 10px; font-size: 11px;" onclick="clearLogs()">Clear</button>
                </div>
                <div class="log-container" id="logContainer">
                    <div class="log-entry">
                        <span class="log-time">[SYSTEM]</span>
                        <span class="log-badge info">BOOT</span>
                        <span class="log-msg">Dashboard initialized. Monitoring COM7 serial stream...</span>
                    </div>
                </div>
            </div>

        </section>

        <!-- FOOTER -->
        <footer class="footer">
            <span>AegisGuard IoT v2.5 &middot; Industrial Gas Leak & Extraction Monitor</span>
            <span>&bull;</span>
            <span>Arduino UNO + MQ-2 + Relay Fan</span>
        </footer>

    </main>

    <!-- CLIENT SCRIPT -->
    <script>
        const MAX_POINTS = 30;
        let chartData = Array(MAX_POINTS).fill(0);
        let prevGasValue = null;
        let sessionPeak = 0;
        let isSimulation = false;
        let soundEnabled = false;
        let lastLoggedStatus = null;
        let audioCtx = null;
        let alarmInterval = null;

        function toggleSound() {
            soundEnabled = !soundEnabled;
            const btn = document.getElementById("soundToggleBtn");
            const label = document.getElementById("soundLabel");
            const icon = document.getElementById("soundIcon");

            if (soundEnabled) {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                btn.classList.add("active");
                label.innerText = "Siren Armed";
                icon.innerHTML = `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>`;
                appendLog("AUDIO", "info", "Siren alert armed.");
            } else {
                btn.classList.remove("active");
                label.innerText = "Siren Muted";
                icon.innerHTML = `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>`;
                stopAlarmSound();
                appendLog("AUDIO", "info", "Siren muted.");
            }
        }

        function playAlarmBeep() {
            if (!soundEnabled || !audioCtx) return;
            try {
                if (audioCtx.state === 'suspended') audioCtx.resume();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.25);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.28);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.3);
            } catch (e) {
                console.error(e);
            }
        }

        function startAlarmSound() {
            if (alarmInterval) return;
            playAlarmBeep();
            alarmInterval = setInterval(playAlarmBeep, 500);
        }

        function stopAlarmSound() {
            if (alarmInterval) {
                clearInterval(alarmInterval);
                alarmInterval = null;
            }
        }

        function toggleSimulation() {
            isSimulation = !isSimulation;
            const btn = document.getElementById("simToggleBtn");
            if (isSimulation) {
                btn.classList.add("active");
                btn.style.color = "#ef4444";
                btn.style.borderColor = "#ef4444";
                appendLog("SIM", "alarm", "TEST ALERT: Injected 600 ADC reading. LED ON, FAN ON.");
            } else {
                btn.classList.remove("active");
                btn.style.color = "";
                btn.style.borderColor = "";
                appendLog("SIM", "normal", "TEST ALERT: Reverted to live hardware stream.");
            }
            updateDashboard();
        }

        function appendLog(category, type, message) {
            const container = document.getElementById("logContainer");
            const now = new Date().toTimeString().split(' ')[0];
            const entry = document.createElement("div");
            entry.className = "log-entry";
            entry.innerHTML = `<span class="log-time">[${now}]</span> <span class="log-badge ${type}">${category}</span> <span class="log-msg">${message}</span>`;
            container.appendChild(entry);
            container.scrollTop = container.scrollHeight;
        }

        function clearLogs() {
            document.getElementById("logContainer").innerHTML = "";
            appendLog("SYSTEM", "info", "Event stream cleared.");
        }

        function drawChart() {
            const canvas = document.getElementById("historyChart");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const dpr = window.devicePixelRatio || 1;
            const width = canvas.parentElement.clientWidth;
            const height = canvas.parentElement.clientHeight;

            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);
            ctx.clearRect(0, 0, width, height);

            const padLeft = 45, padRight = 15, padTop = 15, padBottom = 25;
            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;
            const maxScale = 800;

            ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
            ctx.lineWidth = 1;
            for (let i = 0; i <= 4; i++) {
                const yVal = (maxScale / 4) * i;
                const yPos = padTop + plotH - (yVal / maxScale) * plotH;
                ctx.beginPath();
                ctx.moveTo(padLeft, yPos);
                ctx.lineTo(width - padRight, yPos);
                ctx.stroke();

                ctx.fillStyle = "#64748b";
                ctx.font = "10px JetBrains Mono, monospace";
                ctx.textAlign = "right";
                ctx.fillText(Math.round(yVal), padLeft - 8, yPos + 3);
            }

            const threshY = padTop + plotH - (400 / maxScale) * plotH;
            ctx.strokeStyle = "rgba(239, 68, 68, 0.65)";
            ctx.setLineDash([5, 5]);
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(padLeft, threshY);
            ctx.lineTo(width - padRight, threshY);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = "#ef4444";
            ctx.font = "10px JetBrains Mono, monospace";
            ctx.textAlign = "left";
            ctx.fillText("THRESHOLD: 400", padLeft + 6, threshY - 6);

            if (chartData.length > 1) {
                const stepX = plotW / (MAX_POINTS - 1);
                const grad = ctx.createLinearGradient(0, padTop, 0, padTop + plotH);
                grad.addColorStop(0, "rgba(6, 182, 212, 0.35)");
                grad.addColorStop(1, "rgba(6, 182, 212, 0.0)");

                ctx.beginPath();
                for (let i = 0; i < chartData.length; i++) {
                    const x = padLeft + i * stepX;
                    const val = Math.min(chartData[i], maxScale);
                    const y = padTop + plotH - (val / maxScale) * plotH;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                const lastX = padLeft + (chartData.length - 1) * stepX;
                ctx.lineTo(lastX, padTop + plotH);
                ctx.lineTo(padLeft, padTop + plotH);
                ctx.closePath();
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.beginPath();
                for (let i = 0; i < chartData.length; i++) {
                    const x = padLeft + i * stepX;
                    const val = Math.min(chartData[i], maxScale);
                    const y = padTop + plotH - (val / maxScale) * plotH;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.strokeStyle = "#06b6d4";
                ctx.lineWidth = 2.5;
                ctx.stroke();

                const latestVal = chartData[chartData.length - 1];
                const curY = padTop + plotH - (Math.min(latestVal, maxScale) / maxScale) * plotH;
                ctx.beginPath();
                ctx.arc(lastX, curY, 5, 0, Math.PI * 2);
                ctx.fillStyle = latestVal >= 400 ? "#ef4444" : "#10b981";
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        }

        function drawGauge(val) {
            const canvas = document.getElementById("radialGauge");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const dpr = window.devicePixelRatio || 1;
            const w = 220, h = 140;

            canvas.width = w * dpr;
            canvas.height = h * dpr;
            ctx.scale(dpr, dpr);
            ctx.clearRect(0, 0, w, h);

            const cx = w / 2, cy = 115, radius = 80;
            const startAngle = Math.PI * 0.85;
            const endAngle = Math.PI * 2.15;
            const totalAngle = endAngle - startAngle;

            ctx.beginPath();
            ctx.arc(cx, cy, radius, startAngle, endAngle);
            ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
            ctx.lineWidth = 14;
            ctx.lineCap = "round";
            ctx.stroke();

            const pct = Math.min(Math.max(val / 1023, 0), 1);
            const currentAngle = startAngle + totalAngle * pct;

            ctx.beginPath();
            ctx.arc(cx, cy, radius, startAngle, currentAngle);
            ctx.strokeStyle = val >= 400 ? "#ef4444" : (val >= 250 ? "#f59e0b" : "#10b981");
            ctx.lineWidth = 14;
            ctx.lineCap = "round";
            ctx.stroke();

            const threshPct = 400 / 1023;
            const threshAngle = startAngle + totalAngle * threshPct;
            ctx.beginPath();
            ctx.moveTo(cx + (radius - 12) * Math.cos(threshAngle), cy + (radius - 12) * Math.sin(threshAngle));
            ctx.lineTo(cx + (radius + 12) * Math.cos(threshAngle), cy + (radius + 12) * Math.sin(threshAngle));
            ctx.strokeStyle = "#ef4444";
            ctx.lineWidth = 3;
            ctx.stroke();
        }

        function updateDashboard() {
            fetch("/data")
            .then(res => res.json())
            .then(data => {
                let currentGas = data.gas_value;
                let currentStatus = data.status;
                let currentLed = data.led;
                let currentFan = data.fan;
                let isConnected = data.connected;

                if (isSimulation) {
                    currentGas = 600;
                    currentStatus = "GAS DETECTED";
                    currentLed = "ON";
                    currentFan = "ON";
                    isConnected = true;
                }

                if (currentGas > sessionPeak) {
                    sessionPeak = currentGas;
                    document.getElementById("peakDisplay").innerText = sessionPeak;
                }

                chartData.push(currentGas);
                chartData.shift();
                drawChart();
                drawGauge(currentGas);

                document.getElementById("gasValueDisplay").innerText = currentGas;
                document.getElementById("gaugeValueText").innerText = currentGas;

                if (prevGasValue !== null) {
                    const diff = currentGas - prevGasValue;
                    const deltaEl = document.getElementById("gasDelta");
                    if (diff > 0) deltaEl.innerHTML = `<span style="color:#ef4444;">▲ +${diff}</span>`;
                    else if (diff < 0) deltaEl.innerHTML = `<span style="color:#10b981;">▼ ${diff}</span>`;
                    else deltaEl.innerHTML = `<span style="color:#64748b;">= Steady</span>`;
                }
                prevGasValue = currentGas;

                const connChip = document.getElementById("connChip");
                const connLabel = document.getElementById("connLabel");
                if (isConnected) {
                    connChip.className = "status-chip";
                    connLabel.innerText = "Arduino COM7 &bull; 9600 BAUD";
                } else {
                    connChip.className = "status-chip disconnected";
                    connLabel.innerText = "Arduino Disconnected";
                }

                document.getElementById("heroTime").innerText = data.last_update || new Date().toLocaleTimeString();

                const heroBanner = document.getElementById("heroBanner");
                const heroIcon = document.getElementById("heroIcon");
                const heroTitle = document.getElementById("heroTitle");
                const heroMsg = document.getElementById("heroMsg");
                const threatPill = document.getElementById("threatPill");
                const statusDisplay = document.getElementById("statusDisplay");
                const statusSub = document.getElementById("statusSub");
                const ledDisplay = document.getElementById("ledDisplay");
                const ledDiode = document.getElementById("ledDiode");
                const fanDisplay = document.getElementById("fanDisplay");
                const fanSpinner = document.getElementById("fanSpinner");
                const fanStatusSub = document.getElementById("fanStatusSub");
                const emergencyBar = document.getElementById("emergencyActionBar");

                const isLeak = (currentStatus === "GAS DETECTED") || (currentGas >= 400);

                // LED state
                if (currentLed === "ON") {
                    ledDisplay.innerText = "ACTIVE";
                    ledDisplay.style.color = "var(--danger-color)";
                    ledDiode.className = "led-diode on";
                } else {
                    ledDisplay.innerText = "OFF";
                    ledDisplay.style.color = "var(--text-primary)";
                    ledDiode.className = "led-diode";
                }

                // FAN state
                if (currentFan === "ON") {
                    fanDisplay.innerText = "VENTING";
                    fanDisplay.style.color = "var(--accent-cyan)";
                    fanSpinner.className = "fan-spinner spinning";
                    fanStatusSub.innerText = "Active Extraction";
                } else {
                    fanDisplay.innerText = "OFF";
                    fanDisplay.style.color = "var(--text-primary)";
                    fanSpinner.className = "fan-spinner";
                    fanStatusSub.innerText = "Relay Dormant";
                }

                if (isLeak) {
                    document.body.classList.add("danger-mode");
                    heroBanner.className = "hero-banner danger";
                    heroIcon.innerHTML = `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
                    heroTitle.innerText = "🚨 CRITICAL: COMBUSTIBLE GAS DETECTED!";
                    heroMsg.innerText = "Concentration breached 400 ADC. Hardware Pin D6 (LED) and Pin D7 (Relay Exhaust Fan) are ACTIVE.";
                    threatPill.innerText = "DEFCON 1 &middot; HAZARD";
                    threatPill.style.background = "rgba(239, 68, 68, 0.2)";
                    threatPill.style.color = "#ef4444";

                    statusDisplay.innerText = "HAZARD";
                    statusDisplay.style.color = "var(--danger-color)";
                    statusSub.innerText = "Leak Warning";

                    emergencyBar.classList.add("visible");
                    startAlarmSound();

                    if (lastLoggedStatus !== "HAZARD") {
                        appendLog("ALARM", "alarm", `Hazard triggered: ${currentGas} ADC! LED: ON, Relay Fan: ON.`);
                        lastLoggedStatus = "HAZARD";
                    }
                } else {
                    document.body.classList.remove("danger-mode");
                    heroBanner.className = "hero-banner normal";
                    heroIcon.innerHTML = `<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>`;
                    heroTitle.innerText = "ATMOSPHERE NOMINAL — ENVIRONMENT SAFE";
                    heroMsg.innerText = "MQ-2 analog hydrocarbon telemetry is within normal baseline parameters. Interlocks D6 and D7 are dormant.";
                    threatPill.innerText = "DEFCON 5 &middot; NORMAL";
                    threatPill.style.background = "";
                    threatPill.style.color = "";

                    statusDisplay.innerText = "NORMAL";
                    statusDisplay.style.color = "var(--safe-color)";
                    statusSub.innerText = "Clean Baseline";

                    emergencyBar.classList.remove("visible");
                    stopAlarmSound();

                    if (lastLoggedStatus === "HAZARD") {
                        appendLog("NORMAL", "normal", `Gas cleared. Sensor returned to safe baseline: ${currentGas} ADC.`);
                        lastLoggedStatus = "NORMAL";
                    }
                }
            })
            .catch(err => {
                console.error("Dashboard poll failed:", err);
            });
        }

        window.addEventListener("resize", () => {
            drawChart();
            drawGauge(prevGasValue || 0);
        });

        setInterval(updateDashboard, 1000);
        updateDashboard();
    </script>
</body>
</html>
"""


# =====================================
# READ ARDUINO SERIAL STREAM
# =====================================
def read_arduino():
    global gas_value, peak_value, gas_status, led_status, fan_status, last_update, arduino_connected

    while True:
        try:
            arduino = serial.Serial(
                ARDUINO_PORT,
                BAUD_RATE,
                timeout=1
            )
            arduino_connected = True
            print(f"[*] Arduino connected on {ARDUINO_PORT}")

            while True:
                line = arduino.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(line)

                    # Extract gas sensor numerical reading
                    match = re.search(r"Gas Sensor Value:\s*(\d+)", line)
                    if match:
                        gas_value = int(match.group(1))
                        peak_value = max(peak_value, gas_value)

                        if "GAS DETECTED" in line or gas_value >= THRESHOLD:
                            gas_status = "GAS DETECTED"
                        else:
                            gas_status = "NORMAL"

                        last_update = time.strftime("%H:%M:%S")

                    # Parse LED state
                    if "LED: ON" in line:
                        led_status = "ON"
                    elif "LED: OFF" in line:
                        led_status = "OFF"

                    # Parse Fan / Relay state
                    if "FAN: ON" in line:
                        fan_status = "ON"
                    elif "FAN: OFF" in line:
                        fan_status = "OFF"

        except Exception as e:
            arduino_connected = False
            print(f"[!] Arduino serial error ({ARDUINO_PORT}): {e}. Retrying in 2 seconds...")
            time.sleep(2)


# =====================================
# ROUTES
# =====================================
@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/data")
def data():
    return jsonify({
        "gas_value": gas_value,
        "peak_value": peak_value,
        "status": gas_status,
        "led": led_status,
        "fan": fan_status,
        "last_update": last_update,
        "connected": arduino_connected,
        "threshold": THRESHOLD,
        "port": ARDUINO_PORT
    })


# =====================================
# START
# =====================================
if __name__ == "__main__":
    thread = threading.Thread(
        target=read_arduino,
        daemon=True
    )
    thread.start()

    print("")
    print("======================================================")
    print("       AEGIS GASGUARD - SMART IOT DASHBOARD")
    print("======================================================")
    print("")
    print("  Local Dashboard : http://127.0.0.1:5000")
    print(f"  Target Serial   : {ARDUINO_PORT} @ {BAUD_RATE} baud")
    print(f"  Alarm Threshold : {THRESHOLD} ADC")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )