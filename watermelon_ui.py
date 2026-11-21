"""
watermelon_ui.py
----------------
Upgraded Watermelon UI + Magic UI + Cult UI + Godly Glassmorphic Wallpaper Frontend
and HTTP Server for JalSetu Nagpur.
Pairs cleanly with `jalsetu_backend.py`.
"""

import http.cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import sys
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import jalsetu_backend as backend


def build_react_page(title: str, page_mode: str, bootstrap_json: str) -> str:
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__PAGE_TITLE__</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.7/babel.min.js"></script>
  <style>
    :root, [data-theme="aurora"] {
      --bg-base: #DCEEFB;
      --bg-grad-1: rgba(14, 165, 233, 0.34);
      --bg-grad-2: rgba(16, 185, 129, 0.26);
      --bg-grad-3: rgba(244, 63, 94, 0.20);
      --bg-grad-4: rgba(99, 102, 241, 0.22);
      --dot-color: rgba(2, 132, 199, 0.16);
      --contour-stroke: rgba(2, 132, 199, 0.11);

      --wm-surface: rgba(255, 255, 255, 0.76);
      --wm-surface-strong: rgba(255, 255, 255, 0.88);
      --wm-surface-soft: rgba(241, 248, 255, 0.72);
      --wm-nav-bg: rgba(255, 255, 255, 0.72);
      --wm-border: rgba(255, 255, 255, 0.75);
      --wm-border-subtle: rgba(148, 184, 218, 0.36);
      --wm-text: #0B1324;
      --wm-muted: #475569;

      --wm-aqua: #0284C7;
      --wm-aqua-bright: #0EA5E9;
      --wm-aqua-soft: rgba(224, 242, 254, 0.88);
      --wm-melon: #F43F5E;
      --wm-melon-soft: rgba(255, 228, 230, 0.90);
      --wm-mint: #059669;
      --wm-mint-soft: rgba(209, 250, 229, 0.90);
      --wm-amber: #D97706;
      --wm-amber-soft: rgba(254, 243, 199, 0.92);

      --spotlight-color: rgba(14, 165, 233, 0.16);
      --wm-shadow: 0 16px 40px -14px rgba(15, 35, 68, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.85);
      --wm-shadow-hover: 0 24px 48px -12px rgba(2, 132, 199, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.95);
    }

    [data-theme="sunset"] {
      --bg-base: #FDE8EC;
      --bg-grad-1: rgba(244, 63, 94, 0.30);
      --bg-grad-2: rgba(251, 146, 60, 0.28);
      --bg-grad-3: rgba(20, 184, 166, 0.25);
      --bg-grad-4: rgba(236, 72, 153, 0.20);
      --dot-color: rgba(244, 63, 94, 0.15);
      --contour-stroke: rgba(244, 63, 94, 0.10);

      --wm-surface: rgba(255, 252, 250, 0.78);
      --wm-surface-strong: rgba(255, 255, 255, 0.90);
      --wm-surface-soft: rgba(255, 245, 242, 0.75);
      --wm-nav-bg: rgba(255, 250, 248, 0.74);
      --wm-border: rgba(255, 255, 255, 0.82);
      --wm-border-subtle: rgba(244, 162, 178, 0.38);
      --wm-text: #18101C;
      --wm-muted: #574B5E;

      --spotlight-color: rgba(244, 63, 94, 0.15);
      --wm-shadow: 0 16px 40px -14px rgba(88, 24, 48, 0.13), inset 0 1px 0 rgba(255, 255, 255, 0.90);
      --wm-shadow-hover: 0 24px 48px -12px rgba(244, 63, 94, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.96);
    }

    [data-theme="abyssal"] {
      --bg-base: #06101E;
      --bg-grad-1: rgba(14, 165, 233, 0.28);
      --bg-grad-2: rgba(16, 185, 129, 0.22);
      --bg-grad-3: rgba(244, 63, 94, 0.22);
      --bg-grad-4: rgba(99, 102, 241, 0.26);
      --dot-color: rgba(56, 189, 248, 0.16);
      --contour-stroke: rgba(56, 189, 248, 0.10);

      --wm-surface: rgba(13, 25, 45, 0.72);
      --wm-surface-strong: rgba(17, 33, 58, 0.86);
      --wm-surface-soft: rgba(22, 41, 70, 0.68);
      --wm-nav-bg: rgba(9, 19, 36, 0.76);
      --wm-border: rgba(125, 211, 252, 0.20);
      --wm-border-subtle: rgba(56, 189, 248, 0.18);
      --wm-text: #F1F5F9;
      --wm-muted: #94A3B8;

      --wm-aqua: #38BDF8;
      --wm-aqua-bright: #0EA5E9;
      --wm-aqua-soft: rgba(14, 165, 233, 0.20);
      --wm-melon: #FB7185;
      --wm-melon-soft: rgba(244, 63, 94, 0.22);
      --wm-mint: #34D399;
      --wm-mint-soft: rgba(16, 185, 129, 0.20);
      --wm-amber: #FBBF24;
      --wm-amber-soft: rgba(245, 158, 11, 0.22);

      --spotlight-color: rgba(56, 189, 248, 0.20);
      --wm-shadow: 0 20px 44px -14px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.10);
      --wm-shadow-hover: 0 26px 52px -12px rgba(14, 165, 233, 0.30), inset 0 1px 0 rgba(255, 255, 255, 0.18);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    body {
      background-color: var(--bg-base);
      color: var(--wm-text);
      min-height: 100vh;
      overflow-x: hidden;
      transition: background-color 0.45s ease, color 0.35s ease;
    }

    /* -------------------------------------------------------------------
       GODLY DESIGN LAYERED AURORA + TOPOGRAPHIC WALLPAPER
    ------------------------------------------------------------------- */
    .godly-wallpaper {
      position: fixed;
      inset: 0;
      z-index: -1;
      overflow: hidden;
      pointer-events: none;
      background:
        radial-gradient(1200px circle at 12% 8%, var(--bg-grad-1), transparent 58%),
        radial-gradient(1000px circle at 88% 14%, var(--bg-grad-3), transparent 55%),
        radial-gradient(1100px circle at 76% 85%, var(--bg-grad-2), transparent 60%),
        radial-gradient(900px circle at 18% 82%, var(--bg-grad-4), transparent 55%),
        var(--bg-base);
    }

    .godly-dot-grid {
      position: absolute;
      inset: 0;
      background-image: radial-gradient(var(--dot-color) 1.35px, transparent 1.35px);
      background-size: 24px 24px;
      mask-image: radial-gradient(ellipse 85% 80% at 50% 35%, #000 55%, transparent 100%);
      -webkit-mask-image: radial-gradient(ellipse 85% 80% at 50% 35%, #000 55%, transparent 100%);
    }

    .aurora-orb {
      position: absolute;
      border-radius: 999px;
      filter: blur(72px);
      opacity: 0.72;
      animation: auroraDrift 18s ease-in-out infinite alternate;
    }
    .aurora-orb.one {
      width: 460px; height: 460px; top: -110px; left: -80px;
      background: var(--bg-grad-1);
    }
    .aurora-orb.two {
      width: 420px; height: 420px; top: 18%; right: -90px;
      background: var(--bg-grad-3);
      animation-delay: -5s;
    }
    .aurora-orb.three {
      width: 500px; height: 500px; bottom: -140px; left: 32%;
      background: var(--bg-grad-2);
      animation-delay: -10s;
    }

    @keyframes auroraDrift {
      0% { transform: translate3d(0, 0, 0) scale(1); }
      50% { transform: translate3d(38px, -26px, 0) scale(1.07); }
      100% { transform: translate3d(-24px, 32px, 0) scale(0.96); }
    }

    /* -------------------------------------------------------------------
       MAGIC UI SHIMMER, BORDER BEAM & SHINY TEXT ANIMATIONS
    ------------------------------------------------------------------- */
    @keyframes shimmerSweep {
      0% { transform: translateX(-140%) skewX(-22deg); }
      60%, 100% { transform: translateX(260%) skewX(-22deg); }
    }

    @keyframes shinyTextGlint {
      0% { background-position: -200% center; }
      100% { background-position: 200% center; }
    }

    @keyframes borderBeamSpin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    @keyframes pulseBeacon {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.55); opacity: 0.45; }
    }

    .magic-shiny-badge {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      background: var(--wm-surface-strong);
      border: 1px solid var(--wm-border-subtle);
      box-shadow: 0 6px 18px -6px rgba(2, 132, 199, 0.25);
    }

    .magic-shiny-text {
      background: linear-gradient(110deg, var(--wm-aqua) 20%, #38BDF8 45%, #F43F5E 55%, var(--wm-aqua) 80%);
      background-size: 220% auto;
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      animation: shinyTextGlint 4.2s linear infinite;
    }

    /* -------------------------------------------------------------------
       GLASSMORPHIC CARDS, NAVBAR & CONTROLS
    ------------------------------------------------------------------- */
    .wm-nav {
      position: sticky;
      top: 0;
      z-index: 45;
      background: var(--wm-nav-bg);
      backdrop-filter: blur(18px) saturate(150%);
      -webkit-backdrop-filter: blur(18px) saturate(150%);
      border-bottom: 1px solid var(--wm-border-subtle);
      padding: 12px 26px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .wm-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 800;
      font-size: 17px;
      color: var(--wm-text);
      letter-spacing: -0.02em;
    }

    .wm-logo-drop {
      width: 38px;
      height: 38px;
      border-radius: 13px;
      background: linear-gradient(135deg, #0284C7 0%, #10B981 55%, #F43F5E 100%);
      display: grid;
      place-items: center;
      color: #fff;
      font-size: 18px;
      box-shadow: 0 10px 22px -6px rgba(2, 132, 199, 0.55);
    }

    .wm-container {
      max-width: 1300px;
      margin: 0 auto;
      padding: 24px 20px 56px;
    }

    .wm-card {
      position: relative;
      overflow: hidden;
      background: var(--wm-surface);
      backdrop-filter: blur(18px) saturate(145%);
      -webkit-backdrop-filter: blur(18px) saturate(145%);
      border: 1px solid var(--wm-border);
      outline: 1px solid var(--wm-border-subtle);
      border-radius: 22px;
      padding: 20px;
      box-shadow: var(--wm-shadow);
      transition: background 0.3s ease, border-color 0.3s ease;
    }

    .wm-card-spotlight {
      position: absolute;
      inset: 0;
      pointer-events: none;
      border-radius: inherit;
      opacity: 0;
      transition: opacity 0.25s ease;
      background: radial-gradient(360px circle at var(--mx, 50%) var(--my, 50%), var(--spotlight-color), transparent 75%);
    }
    .wm-card:hover .wm-card-spotlight {
      opacity: 1;
    }

    /* Magic UI Border Beam Wrapper */
    .border-beam-shell {
      position: relative;
      border-radius: 24px;
      padding: 2px;
      overflow: hidden;
      box-shadow: var(--wm-shadow);
    }
    .border-beam-spinner {
      position: absolute;
      inset: -120%;
      background: conic-gradient(from 0deg, transparent 0deg 260deg, #0EA5E9 300deg, #10B981 330deg, #F43F5E 360deg);
      animation: borderBeamSpin 6.5s linear infinite;
      pointer-events: none;
    }
    .border-beam-inner {
      position: relative;
      z-index: 1;
      border-radius: 22px;
      background: var(--wm-surface-strong);
      backdrop-filter: blur(20px) saturate(150%);
      -webkit-backdrop-filter: blur(20px) saturate(150%);
      padding: 22px;
      height: 100%;
    }

    .wm-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 11.5px;
      font-weight: 800;
      letter-spacing: 0.01em;
    }
    .wm-pill.aqua { background: var(--wm-aqua-soft); color: var(--wm-aqua); }
    .wm-pill.mint { background: var(--wm-mint-soft); color: var(--wm-mint); }
    .wm-pill.melon { background: var(--wm-melon-soft); color: var(--wm-melon); }
    .wm-pill.amber { background: var(--wm-amber-soft); color: var(--wm-amber); }

    .live-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: currentColor;
      display: inline-block;
      animation: pulseBeacon 1.8s ease-in-out infinite;
    }

    /* Watermelon + Magic UI Buttons */
    .wm-btn {
      position: relative;
      overflow: hidden;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 16px;
      border-radius: 14px;
      border: 1px solid var(--wm-border-subtle);
      background: var(--wm-surface-strong);
      color: var(--wm-text);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      box-shadow: 0 4px 12px -4px rgba(15, 23, 42, 0.08);
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .wm-btn:hover {
      border-color: var(--wm-aqua-bright);
      box-shadow: 0 8px 20px -6px rgba(2, 132, 199, 0.22);
    }
    .wm-btn.primary {
      background: linear-gradient(135deg, #0284C7 0%, #0EA5E9 55%, #06B6D4 100%);
      color: #fff;
      border: none;
      box-shadow: 0 12px 24px -8px rgba(2, 132, 199, 0.58);
    }
    .wm-btn.mint {
      background: linear-gradient(135deg, #059669 0%, #10B981 100%);
      color: #fff;
      border: none;
      box-shadow: 0 12px 24px -8px rgba(16, 185, 129, 0.50);
    }
    .wm-btn.melon {
      background: linear-gradient(135deg, #E11D48 0%, #F43F5E 100%);
      color: #fff;
      border: none;
      box-shadow: 0 12px 24px -8px rgba(244, 63, 94, 0.50);
    }
    .wm-btn.amber {
      background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
      color: #fff;
      border: none;
      box-shadow: 0 12px 24px -8px rgba(245, 158, 11, 0.45);
    }

    .shimmer-beam {
      position: absolute;
      top: 0;
      left: 0;
      width: 45%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.42), transparent);
      animation: shimmerSweep 3.4s ease-in-out infinite;
      pointer-events: none;
    }

    .wm-input, .wm-select, .wm-textarea {
      width: 100%;
      background: var(--wm-surface-soft);
      border: 1.5px solid var(--wm-border-subtle);
      color: var(--wm-text);
      padding: 10px 13px;
      border-radius: 13px;
      font-size: 13.5px;
      font-weight: 600;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
    }
    .wm-input:focus, .wm-select:focus, .wm-textarea:focus {
      border-color: var(--wm-aqua-bright);
      background: var(--wm-surface-strong);
      box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.16);
    }
    .wm-label {
      display: block;
      font-size: 11.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--wm-muted);
      margin-bottom: 6px;
    }

    .wm-grid-hero { display: grid; grid-template-columns: 1.18fr 0.82fr; gap: 22px; align-items: stretch; }
    .wm-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
    .wm-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
    .wm-grid-main { display: grid; grid-template-columns: 400px 1fr; gap: 22px; align-items: start; }
    @media (max-width: 1024px) {
      .wm-grid-hero, .wm-grid-main { grid-template-columns: 1fr; }
      .wm-grid-4 { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 640px) {
      .wm-grid-3, .wm-grid-4 { grid-template-columns: 1fr; }
    }

    .wm-map {
      height: 320px;
      border-radius: 18px;
      border: 1px solid var(--wm-border-subtle);
      overflow: hidden;
      background: #E8F1F8;
    }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th {
      text-align: left;
      padding: 10px 8px;
      color: var(--wm-muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--wm-border-subtle);
    }
    td {
      padding: 11px 8px;
      border-bottom: 1px solid var(--wm-border-subtle);
    }
    .mono { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body data-theme="aurora">
  <!-- Godly Design Layered Animated Wallpaper -->
  <div class="godly-wallpaper" aria-hidden="true">
    <div class="aurora-orb one"></div>
    <div class="aurora-orb two"></div>
    <div class="aurora-orb three"></div>
    <div class="godly-dot-grid"></div>
    <svg width="100%" height="100%" viewBox="0 0 1440 900" preserveAspectRatio="none" style="position:absolute;inset:0;">
      <path d="M-80 180 C 320 90, 640 290, 1080 170 C 1280 115, 1400 160, 1520 140" fill="none" stroke="var(--contour-stroke)" stroke-width="2" />
      <path d="M-80 440 C 280 540, 740 340, 1140 460 C 1320 515, 1420 470, 1520 450" fill="none" stroke="var(--contour-stroke)" stroke-width="2" />
      <path d="M-80 730 C 360 630, 780 820, 1200 700 C 1360 655, 1440 690, 1520 675" fill="none" stroke="var(--contour-stroke)" stroke-width="2" />
    </svg>
  </div>

  <div id="root" style="padding:28px;font-family:'Plus Jakarta Sans',sans-serif;color:#475569;">
    Loading JalSetu Nagpur Watermelon UI...
  </div>

  <script>
    window.__PAGE_MODE__ = "__PAGE_MODE__";
    window.__BOOTSTRAP__ = __BOOTSTRAP_JSON__;

    function showFatalBanner(title, detail) {
      var el = document.getElementById('root');
      if (el) {
        el.innerHTML =
          '<div style="max-width:680px;margin:40px auto;background:#FFE4E6;border:1px solid #FECDD3;color:#BE123C;padding:20px;border-radius:16px;font-family:sans-serif;">' +
          '<h3 style="margin-bottom:8px;">' + title + '</h3>' +
          '<pre style="white-space:pre-wrap;font-size:12.5px;line-height:1.5;">' + detail + '</pre>' +
          '</div>';
      }
    }

    window.addEventListener('error', function (e) {
      var el = document.getElementById('root');
      if (el && el.innerText.indexOf('Loading') !== -1) {
        showFatalBanner('JalSetu UI Initialization Error', String(e.message || e.error || 'Unknown error'));
      }
    });

    if (!window.React || !window.ReactDOM || !window.Babel) {
      showFatalBanner(
        'Frontend CDN Scripts Unavailable',
        'React, ReactDOM, or Babel failed to load from cdnjs.cloudflare.com. Check your internet connection and refresh.'
      );
    }
  </script>

  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const { createRoot } = ReactDOM;

    // -----------------------------------------------------------------------
    // ERROR BOUNDARY
    // -----------------------------------------------------------------------
    class UIErrorBoundary extends React.Component {
      constructor(props) {
        super(props);
        this.state = { error: null };
      }
      static getDerivedStateFromError(error) {
        return { error };
      }
      render() {
        if (this.state.error) {
          return (
            <div style={{ maxWidth: '680px', margin: '48px auto', background: '#FFE4E6', border: '1px solid #FECDD3', color: '#BE123C', padding: '22px', borderRadius: '18px' }}>
              <h3 style={{ marginBottom: '8px', fontWeight: 800 }}>Watermelon UI Runtime Notice</h3>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12.5px' }}>{String(this.state.error)}</pre>
            </div>
          );
        }
        return this.props.children;
      }
    }

    // -----------------------------------------------------------------------
    // HOOKE'S-LAW SPRING ENGINE
    // -----------------------------------------------------------------------
    function makeSpringVal(v) {
      return {
        __sv: true,
        _v: v,
        get() { return this._v; },
        to(fn) { return makeSpringVal(fn(this._v)); },
      };
    }

    function useSpring(spec) {
      const { from = {}, to, delay = 0, config = {}, ...direct } = spec;
      const targets = to || direct;
      const tension = config.tension || 270;
      const friction = config.friction || 24;

      const stateRef = useRef(null);
      if (!stateRef.current) {
        const init = {};
        const vel = {};
        Object.keys(targets).forEach((k) => {
          init[k] = from[k] !== undefined ? from[k] : targets[k];
          vel[k] = 0;
        });
        stateRef.current = { cur: init, vel, targets };
      }
      stateRef.current.targets = targets;

      const [, setTick] = useState(0);
      const targetSig = JSON.stringify(targets);

      useEffect(() => {
        let rafId = null;
        let lastTime = performance.now();
        const timer = setTimeout(() => {
          const step = (now) => {
            const dt = Math.min(0.032, (now - lastTime) / 1000);
            lastTime = now;
            let moving = false;
            const { cur, vel, targets: curTargets } = stateRef.current;

            Object.keys(curTargets).forEach((k) => {
              const tgt = curTargets[k];
              if (typeof tgt !== 'number') {
                cur[k] = tgt;
                return;
              }
              const c = typeof cur[k] === 'number' ? cur[k] : tgt;
              const v = vel[k] || 0;
              const force = -tension * (c - tgt);
              const damp = -friction * v;
              const nextV = v + (force + damp) * dt;
              const nextC = c + nextV * dt;

              if (Math.abs(tgt - nextC) < 0.01 && Math.abs(nextV) < 0.01) {
                cur[k] = tgt;
                vel[k] = 0;
              } else {
                cur[k] = nextC;
                vel[k] = nextV;
                moving = true;
              }
            });

            setTick((t) => t + 1);
            if (moving) rafId = requestAnimationFrame(step);
          };
          rafId = requestAnimationFrame(step);
        }, delay);

        return () => {
          clearTimeout(timer);
          if (rafId) cancelAnimationFrame(rafId);
        };
      }, [targetSig]);

      const out = {};
      Object.keys(targets).forEach((k) => {
        out[k] = makeSpringVal(stateRef.current.cur[k]);
      });
      return out;
    }

    function useTransition(item, spec) {
      const s = useSpring({
        from: spec.from || { opacity: 0, y: 12 },
        to: spec.enter || { opacity: 1, y: 0 },
        config: spec.config,
      });
      return (renderFn) =>
        renderFn(
          {
            opacity: s.opacity,
            transform: s.y ? s.y.to((v) => `translate3d(0, ${v}px, 0)`) : undefined,
          },
          item
        );
    }

    function wrapAnimated(Tag) {
      return function AnimatedTag({ style, children, ...rest }) {
        const cleanStyle = style ? { ...style } : undefined;
        if (cleanStyle) {
          Object.keys(cleanStyle).forEach((k) => {
            if (cleanStyle[k] && cleanStyle[k].__sv) cleanStyle[k] = cleanStyle[k].get();
          });
        }
        const cleanChildren = children && children.__sv ? children.get() : children;
        return <Tag style={cleanStyle} {...rest}>{cleanChildren}</Tag>;
      };
    }

    const animated = {
      div: wrapAnimated('div'),
      button: wrapAnimated('button'),
      span: wrapAnimated('span'),
    };

    const MODE = window.__PAGE_MODE__;
    const BOOT = window.__BOOTSTRAP__;

    // -----------------------------------------------------------------------
    // GODLY WALLPAPER SWITCHER (Persisted in localStorage)
    // -----------------------------------------------------------------------
    function WallpaperSwitcher() {
      const [theme, setTheme] = useState(() => {
        try { return localStorage.getItem('jalsetu_godly_theme') || 'aurora'; } catch (e) { return 'aurora'; }
      });

      useEffect(() => {
        document.body.setAttribute('data-theme', theme);
        try { localStorage.setItem('jalsetu_godly_theme', theme); } catch (e) {}
      }, [theme]);

      const themes = [
        { id: 'aurora', label: 'Oceanic Aurora', dot: 'linear-gradient(135deg, #0EA5E9, #10B981)' },
        { id: 'sunset', label: 'Watermelon', dot: 'linear-gradient(135deg, #F43F5E, #F59E0B)' },
        { id: 'abyssal', label: 'Abyssal Glass', dot: 'linear-gradient(135deg, #0F172A, #38BDF8)' },
      ];

      return (
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px',
          borderRadius: '999px', background: 'var(--wm-surface-soft)',
          border: '1px solid var(--wm-border-subtle)'
        }}>
          {themes.map((t) => {
            const active = theme === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setTheme(t.id)}
                title={`Wallpaper: ${t.label}`}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: '6px',
                  padding: '5px 10px', borderRadius: '999px', border: 'none',
                  background: active ? 'var(--wm-surface-strong)' : 'transparent',
                  color: active ? 'var(--wm-text)' : 'var(--wm-muted)',
                  fontSize: '11.5px', fontWeight: 700, cursor: 'pointer',
                  boxShadow: active ? '0 3px 10px rgba(15,23,42,0.10)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: t.dot, display: 'inline-block' }} />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>
      );
    }

    // -----------------------------------------------------------------------
    // MAGIC UI + CULT UI + WATERMELON UI COMPONENTS
    // -----------------------------------------------------------------------

    // 1. MagicCard: Cursor-tracking spotlight glow + Watermelon Spring physics
    function MagicSpringCard({ children, style = {}, delay = 0, hoverLift = false, onClick }) {
      const cardRef = useRef(null);
      const [hovered, setHovered] = useState(false);
      const [pressed, setPressed] = useState(false);

      const enter = useSpring({
        from: { opacity: 0, y: 18 },
        to: { opacity: 1, y: 0 },
        delay,
        config: { tension: 260, friction: 24 },
      });

      const interact = useSpring({
        scale: pressed ? 0.985 : (hoverLift && hovered ? 1.016 : 1),
        y: hoverLift && hovered ? -4 : 0,
        config: { tension: 350, friction: 22 },
      });

      const handleMouseMove = (e) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        cardRef.current.style.setProperty('--mx', `${e.clientX - rect.left}px`);
        cardRef.current.style.setProperty('--my', `${e.clientY - rect.top}px`);
      };

      const ey = enter.y.get();
      const iy = interact.y.get();
      const sc = interact.scale.get();
      const isSettled = Math.abs(ey) < 0.02 && Math.abs(iy) < 0.02 && Math.abs(sc - 1) < 0.001;

      return (
        <animated.div
          ref={cardRef}
          className="wm-card"
          onClick={onClick}
          onMouseMove={handleMouseMove}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => { setHovered(false); setPressed(false); }}
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          style={{
            ...style,
            opacity: enter.opacity,
            transform: isSettled ? 'none' : `translate3d(0, ${ey + iy}px, 0) scale(${sc})`,
            boxShadow: hoverLift && hovered ? 'var(--wm-shadow-hover)' : 'var(--wm-shadow)',
            cursor: onClick ? 'pointer' : style.cursor,
          }}
        >
          <div className="wm-card-spotlight" />
          <div style={{ position: 'relative', zIndex: 1 }}>{children}</div>
        </animated.div>
      );
    }

    // 2. Magic UI BorderBeam Card
    function BorderBeamCard({ children, style = {} }) {
      return (
        <div className="border-beam-shell" style={style}>
          <div className="border-beam-spinner" />
          <div className="border-beam-inner">{children}</div>
        </div>
      );
    }

    // 3. Watermelon + Magic UI Magnetic Shimmer Button
    function ShimmerSpringButton({ children, variant = '', onClick, style = {}, type = 'button', shimmer = false }) {
      const btnRef = useRef(null);
      const [pressed, setPressed] = useState(false);
      const [mag, setMag] = useState({ x: 0, y: 0 });

      const spring = useSpring({
        scale: pressed ? 0.95 : 1,
        mx: mag.x,
        my: mag.y,
        config: { tension: 420, friction: 20 },
      });

      const onMove = (e) => {
        if (!btnRef.current) return;
        const r = btnRef.current.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) * 0.14;
        const dy = (e.clientY - (r.top + r.height / 2)) * 0.18;
        setMag({ x: dx, y: dy });
      };

      const onLeave = () => {
        setPressed(false);
        setMag({ x: 0, y: 0 });
      };

      const sc = spring.scale.get();
      const mx = spring.mx.get();
      const my = spring.my.get();

      return (
        <animated.button
          ref={btnRef}
          type={type}
          className={`wm-btn ${variant}`}
          onClick={onClick}
          onMouseMove={onMove}
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          onMouseLeave={onLeave}
          style={{
            ...style,
            transform: `translate3d(${mx.toFixed(2)}px, ${my.toFixed(2)}px, 0) scale(${sc.toFixed(4)})`,
          }}
        >
          {(shimmer || variant === 'primary' || variant === 'mint' || variant === 'melon') && (
            <span className="shimmer-beam" />
          )}
          <span style={{ position: 'relative', zIndex: 1, display: 'inline-flex', alignItems: 'center', gap: '7px' }}>
            {children}
          </span>
        </animated.button>
      );
    }

    // 4. Watermelon UI ContinuousTabs (Spring gliding pill indicator)
    function ContinuousTabs({ items, activeId, onChange }) {
      const containerRef = useRef(null);
      const itemRefs = useRef({});
      const [pill, setPill] = useState({ left: 4, width: 100 });

      useEffect(() => {
        const el = itemRefs.current[activeId];
        const wrap = containerRef.current;
        if (el && wrap) {
          setPill({ left: el.offsetLeft, width: el.offsetWidth });
        }
      }, [activeId, items.length]);

      const pillSpring = useSpring({
        left: pill.left,
        width: pill.width,
        config: { tension: 340, friction: 26 },
      });

      return (
        <div
          ref={containerRef}
          style={{
            position: 'relative',
            display: 'inline-flex',
            flexWrap: 'wrap',
            gap: '4px',
            padding: '5px',
            borderRadius: '16px',
            background: 'var(--wm-surface)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--wm-border-subtle)',
            boxShadow: 'var(--wm-shadow)',
          }}
        >
          <animated.div
            style={{
              position: 'absolute',
              top: '5px',
              bottom: '5px',
              left: pillSpring.left.to((v) => `${v}px`),
              width: pillSpring.width.to((v) => `${v}px`),
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #0284C7, #0EA5E9)',
              boxShadow: '0 8px 18px -5px rgba(2, 132, 199, 0.52)',
              zIndex: 0,
            }}
          />
          {items.map((it) => {
            const isActive = it.id === activeId;
            return (
              <button
                key={it.id}
                ref={(node) => { itemRefs.current[it.id] = node; }}
                type="button"
                onClick={() => onChange(it.id)}
                style={{
                  position: 'relative',
                  zIndex: 1,
                  padding: '9px 14px',
                  borderRadius: '12px',
                  border: 'none',
                  background: 'transparent',
                  color: isActive ? '#FFFFFF' : 'var(--wm-text)',
                  fontSize: '12.5px',
                  fontWeight: 800,
                  cursor: 'pointer',
                  transition: 'color 0.2s ease',
                }}
              >
                {it.label}
              </button>
            );
          })}
        </div>
      );
    }

    // 5. Cult UI / Watermelon UI Dynamic Island Floating Toast
    function DynamicIslandToast({ message }) {
      const spring = useSpring({
        y: message ? 0 : 70,
        opacity: message ? 1 : 0,
        scale: message ? 1 : 0.88,
        config: { tension: 360, friction: 24 },
      });

      if (!message && spring.opacity.get() < 0.02) return null;

      return (
        <animated.div
          style={{
            position: 'fixed',
            bottom: '24px',
            left: '50%',
            zIndex: 70,
            opacity: spring.opacity,
            transform: `translate3d(-50%, ${spring.y.get()}px, 0) scale(${spring.scale.get()})`,
            background: 'rgba(11, 19, 36, 0.92)',
            backdropFilter: 'blur(16px)',
            color: '#FFFFFF',
            padding: '12px 22px',
            borderRadius: '999px',
            border: '1px solid rgba(56, 189, 248, 0.35)',
            boxShadow: '0 20px 40px -10px rgba(2, 132, 199, 0.45)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '13px',
            fontWeight: 700,
            pointerEvents: 'none',
          }}
        >
          <span style={{
            width: '22px', height: '22px', borderRadius: '50%',
            background: 'linear-gradient(135deg, #10B981, #0EA5E9)',
            display: 'grid', placeItems: 'center', fontSize: '12px'
          }}>✓</span>
          <span>{message}</span>
        </animated.div>
      );
    }

    function AnimatedNumber({ value, suffix = '' }) {
      const num = Number(value) || 0;
      const spring = useSpring({
        val: num,
        from: { val: 0 },
        config: { tension: 120, friction: 20 },
      });
      return (
        <animated.span className="mono">
          {spring.val.to((v) => `${Math.round(v).toLocaleString('en-IN')}${suffix}`)}
        </animated.span>
      );
    }

    function StatusBadge({ status }) {
      const s = String(status || '').toUpperCase();
      if (['RED', 'OPEN', 'FLAGGED', 'BOREWELL_DRY'].includes(s)) {
        return <span className="wm-pill melon"><span className="live-dot" /> {s.replace('_', ' ')}</span>;
      }
      if (['YELLOW', 'DISPATCHED', 'UNLOADED', 'PENDING_DISPATCH', 'LOW_PRESSURE'].includes(s)) {
        return <span className="wm-pill amber"><span className="live-dot" /> {s.replace('_', ' ')}</span>;
      }
      return <span className="wm-pill mint"><span className="live-dot" /> {s || 'HEALTHY'}</span>;
    }

    function NagpurMap({ center = [21.125, 79.025], zoom = 11, renderLayers, deps = [] }) {
      const divRef = useRef(null);
      const mapRef = useRef(null);
      const layerRef = useRef(null);

      useEffect(() => {
        if (!divRef.current) return;
        if (typeof L === 'undefined') {
          divRef.current.innerHTML =
            '<div style="height:100%;display:grid;place-items:center;padding:16px;text-align:center;color:var(--wm-muted);font-size:13px;">Interactive map tiles unavailable offline — telemetry and dispatch lists remain active below.</div>';
          return;
        }
        if (!mapRef.current) {
          const m = L.map(divRef.current).setView(center, zoom);
          const tiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap © CARTO',
          });
          tiles.on('tileerror', () => {
            if (divRef.current) {
              divRef.current.style.backgroundImage = 'radial-gradient(#94A3B8 1.2px, transparent 1.2px)';
              divRef.current.style.backgroundSize = '18px 18px';
            }
          });
          tiles.addTo(m);
          mapRef.current = m;
          layerRef.current = L.layerGroup().addTo(m);
          setTimeout(() => {
            if (mapRef.current) mapRef.current.invalidateSize();
          }, 180);
        }
        if (renderLayers && mapRef.current && layerRef.current) {
          layerRef.current.clearLayers();
          renderLayers(mapRef.current, layerRef.current);
        }
      }, deps);

      return <div ref={divRef} className="wm-map" />;
    }

    // -----------------------------------------------------------------------
    // VIEW 0: PUBLIC OVERVIEW + PORTAL SIGN-IN (/login)
    // -----------------------------------------------------------------------
    function LandingLoginApp() {
      const [role, setRole] = useState(BOOT.preselect_role || 'citizen');
      const [name, setName] = useState(BOOT.role_defaults[BOOT.preselect_role || 'citizen'].default_name);
      const [password, setPassword] = useState(BOOT.role_defaults[BOOT.preselect_role || 'citizen'].default_pass);
      const [err, setErr] = useState('');
      const [summary, setSummary] = useState(null);
      const loginBoxRef = useRef(null);

      useEffect(() => {
        fetch('/api/public-summary').then((r) => r.json()).then(setSummary).catch(() => {});
      }, []);

      const chooseRole = (r, scrollToLogin = false) => {
        setRole(r);
        setName(BOOT.role_defaults[r].default_name);
        setPassword(BOOT.role_defaults[r].default_pass);
        setErr('');
        if (scrollToLogin && loginBoxRef.current) {
          loginBoxRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      };

      const handleAuth = async (endpoint) => {
        setErr('');
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role, name: name.trim(), password }),
        });
        const data = await res.json();
        if (!res.ok) {
          setErr(data.error || 'Sign-in failed');
          return;
        }
        window.location.href = data.redirect;
      };

      const roleDescriptions = {
        citizen: 'Check daily colony water status & pump runway, log 1-tap household availability, track live incoming tankers on map, report leaks, and calculate 14-taluka rainwater harvesting.',
        verifier: 'Log weekly/fortnightly reference well depths with live 48h Open-Meteo rainfall anti-cheat validation, inspect 6-hourly calibrated hydrographs, and raise verified 55 LPCD tanker indents.',
        utility: 'Monitor Nagpur scarcity & live tanker routes, auto-dispatch nearest depot tankers with stock tracking, and resolve resident leak & valve fault tickets.',
      };

      const kpis = [
        { label: 'Monitored Nagpur Locations', val: summary ? summary.total_locations : 91, sub: '87 CGWB stations + pilot colonies', tone: 'aqua', icon: '📍' },
        { label: 'Active Scarcity Zones', val: summary ? summary.stressed_zones : 3, sub: 'RED & YELLOW alert colonies', tone: 'melon', icon: '⚠️' },
        { label: 'Dry Borewell Households', val: summary ? summary.dry_households : 96, sub: 'Live resident check-in reports', tone: 'amber', icon: '🏠' },
        { label: 'Tankers Ready at Depots', val: summary ? summary.trucks_ready : 12, sub: 'Across 3 Nagpur filling zones', tone: 'mint', icon: '🚛' },
        { label: 'Active / Completed Deliveries', val: summary ? summary.total_orders : 1, sub: 'Verified end-to-end trips', tone: 'aqua', icon: '💧' },
        { label: 'Live 48h Nagpur Rainfall', val: summary ? summary.rain_48h_mm : 0, suffix: ' mm', sub: 'Open-Meteo live precipitation', tone: 'mint', icon: '🌧️' },
      ];

      const quickActions = [
        { title: 'Daily Water Check-In', desc: 'Report normal supply, low pressure, or dry borewell in 1 tap.', role: 'citizen', icon: '💧', accent: '#0284C7', tag: '1-Tap Telemetry' },
        { title: 'Track Live Tanker', desc: 'See incoming tanker route from depot & confirm delivery.', role: 'citizen', icon: '🗺️', accent: '#059669', tag: 'Live GPS Route' },
        { title: 'Report Leak / Pump Fault', desc: 'Log leaking valves or pump breakdowns directly to utility desk.', role: 'citizen', icon: '🔧', accent: '#E11D48', tag: 'Rapid Triage' },
        { title: '14-Taluka RWH Calculator', desc: 'Estimate roof runoff, first-flush & recharge in EN / हिं / म.', role: 'citizen', icon: '🌦️', accent: '#D97706', tag: 'Multilingual' },
      ];

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">💧</div>
              <div>
                <div>JalSetu Nagpur</div>
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--wm-muted)' }}>Community Groundwater, Tanker & Recharge Intelligence</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
              <WallpaperSwitcher />
              <ShimmerSpringButton onClick={() => chooseRole('citizen', true)}>Citizen</ShimmerSpringButton>
              <ShimmerSpringButton onClick={() => chooseRole('verifier', true)}>Verifier</ShimmerSpringButton>
              <ShimmerSpringButton variant="primary" onClick={() => chooseRole('utility', true)}>Utility Ops</ShimmerSpringButton>
            </div>
          </nav>

          <div className="wm-container">
            <div className="wm-grid-hero" style={{ marginBottom: '26px' }}>
              <BorderBeamCard>
                <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%' }}>
                  <div>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                      <span className="magic-shiny-badge">
                        <span className="live-dot" style={{ color: '#0EA5E9' }} />
                        <span className="magic-shiny-text">Nagpur District · 91 Live Locations</span>
                      </span>
                      <span className="wm-pill mint">CGWB Calibration + Live 48h Rain</span>
                    </div>
                    <h1 style={{ fontSize: '33px', fontWeight: 800, lineHeight: 1.16, letterSpacing: '-0.03em', marginBottom: '12px' }}>
                      Real-Time Water Scarcity, Tanker Tracking & Rainwater Recharge
                    </h1>
                    <p style={{ fontSize: '14.5px', lineHeight: 1.62, color: 'var(--wm-muted)', marginBottom: '20px' }}>
                      Connecting Nagpur residents, field verifiers, and tanker dispatchers on one live workflow—calibrating local borewells against CGWB telemetry, verifying scarcity with 48-hour rainfall, and tracking every tanker drop.
                    </p>
                  </div>

                  <div style={{ background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', borderRadius: '18px', padding: '14px' }}>
                    <svg viewBox="0 0 540 135" style={{ width: '100%', height: '125px', display: 'block' }}>
                      <defs>
                        <linearGradient id="flowLineGrad" x1="0" y1="0" x2="1" y2="0">
                          <stop offset="0%" stopColor="#0284C7" />
                          <stop offset="50%" stopColor="#10B981" />
                          <stop offset="100%" stopColor="#F43F5E" />
                        </linearGradient>
                      </defs>
                      <path d="M 65 88 C 165 25, 295 118, 465 52" fill="none" stroke="url(#flowLineGrad)" strokeWidth="4.5" strokeDasharray="8 6" strokeLinecap="round" />
                      <circle cx="65" cy="88" r="20" fill="#0284C7" />
                      <text x="65" y="94" textAnchor="middle" fill="#fff" fontSize="15">🚛</text>
                      <text x="65" y="124" textAnchor="middle" fill="var(--wm-text)" fontSize="10.5" fontWeight="800">3 Nagpur Depots</text>

                      <circle cx="265" cy="72" r="20" fill="#10B981" />
                      <text x="265" y="78" textAnchor="middle" fill="#fff" fontSize="15">📡</text>
                      <text x="265" y="108" textAnchor="middle" fill="var(--wm-text)" fontSize="10.5" fontWeight="800">CGWB + Rain Verify</text>

                      <circle cx="465" cy="52" r="20" fill="#F43F5E" />
                      <text x="465" y="58" textAnchor="middle" fill="#fff" fontSize="15">🏘️</text>
                      <text x="465" y="88" textAnchor="middle" fill="var(--wm-text)" fontSize="10.5" fontWeight="800">Colony Delivery</text>
                    </svg>
                  </div>
                </div>
              </BorderBeamCard>

              <div ref={loginBoxRef}>
                <MagicSpringCard delay={80} style={{ height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Sign In to Your Portal</h2>
                    <span className="wm-pill aqua">Role-Based Access</span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '14px' }}>
                    {[
                      { id: 'citizen', label: 'Citizen' },
                      { id: 'verifier', label: 'Field Verifier' },
                      { id: 'utility', label: 'Utility Ops' },
                    ].map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => chooseRole(t.id)}
                        style={{
                          padding: '10px 8px',
                          borderRadius: '13px',
                          border: role === t.id ? '2px solid #0EA5E9' : '1px solid var(--wm-border-subtle)',
                          background: role === t.id ? 'var(--wm-aqua-soft)' : 'var(--wm-surface-soft)',
                          color: role === t.id ? 'var(--wm-aqua)' : 'var(--wm-muted)',
                          fontWeight: 800,
                          fontSize: '12.5px',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                        }}
                      >
                        {t.label}
                      </button>
                    ))}
                  </div>

                  <div style={{ background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', borderRadius: '13px', padding: '11px 13px', fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5, marginBottom: '14px' }}>
                    {roleDescriptions[role]}
                  </div>

                  <label className="wm-label">Full Name / Username</label>
                  <input className="wm-input" style={{ marginBottom: '10px' }} value={name} onChange={(e) => setName(e.target.value)} placeholder="Enter your name" />

                  <label className="wm-label">Password</label>
                  <input
                    className="wm-input"
                    type="password"
                    style={{ marginBottom: '12px' }}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAuth('/api/login')}
                    placeholder="Enter password"
                  />

                  {err && (
                    <div style={{ background: 'var(--wm-melon-soft)', color: 'var(--wm-melon)', padding: '8px 12px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, marginBottom: '10px' }}>
                      {err}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <ShimmerSpringButton variant="primary" style={{ flex: 1 }} onClick={() => handleAuth('/api/login')}>
                      Enter {BOOT.role_defaults[role].title} →
                    </ShimmerSpringButton>
                    <ShimmerSpringButton onClick={() => handleAuth('/api/register')}>
                      Register
                    </ShimmerSpringButton>
                  </div>
                </MagicSpringCard>
              </div>
            </div>

            <div className="wm-grid-3" style={{ marginBottom: '26px' }}>
              {kpis.map((k, idx) => (
                <MagicSpringCard key={k.label} delay={idx * 45} hoverLift style={{ padding: '16px 18px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{
                      width: '48px', height: '48px', borderRadius: '15px', flexShrink: 0,
                      background: `var(--wm-${k.tone}-soft)`, display: 'grid', placeItems: 'center', fontSize: '22px',
                      border: '1px solid var(--wm-border-subtle)'
                    }}>
                      {k.icon}
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--wm-muted)' }}>{k.label}</div>
                      <div style={{ fontSize: '25px', fontWeight: 800, color: 'var(--wm-text)', lineHeight: 1.15 }}>
                        <AnimatedNumber value={k.val} suffix={k.suffix || ''} />
                      </div>
                      <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)', marginTop: '2px' }}>{k.sub}</div>
                    </div>
                  </div>
                </MagicSpringCard>
              ))}
            </div>

            <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Citizen Quick Actions</h2>
              <span style={{ fontSize: '12px', color: 'var(--wm-muted)', fontWeight: 700 }}>Hover & click any Bento tile to launch</span>
            </div>
            <div className="wm-grid-4">
              {quickActions.map((qa, idx) => (
                <MagicSpringCard
                  key={qa.title}
                  delay={120 + idx * 50}
                  hoverLift
                  onClick={() => chooseRole(qa.role, true)}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '158px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <div style={{
                          width: '42px', height: '42px', borderRadius: '13px',
                          background: 'var(--wm-aqua-soft)', display: 'grid', placeItems: 'center', fontSize: '20px'
                        }}>
                          {qa.icon}
                        </div>
                        <span className="wm-pill aqua" style={{ fontSize: '10.5px' }}>{qa.tag}</span>
                      </div>
                      <div style={{ fontSize: '15px', fontWeight: 800, marginBottom: '6px' }}>{qa.title}</div>
                      <p style={{ fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5 }}>{qa.desc}</p>
                    </div>
                    <div style={{ marginTop: '14px', fontSize: '12px', fontWeight: 800, color: qa.accent }}>
                      Open Action →
                    </div>
                  </div>
                </MagicSpringCard>
              ))}
            </div>
          </div>
        </div>
      );
    }

    // -----------------------------------------------------------------------
    // VIEW 1: CITIZEN PORTAL (/citizen)
    // -----------------------------------------------------------------------
    const RWH_RULES = {
      en: [
        'Sweep terrace & clear drain outlets before monsoon showers',
        'Divert first rain & dry-spell flush before recharge pit entry',
        'Keep terrace free of detergents & chemical cleaners',
        'Inspect filter mesh, sand/gravel bed & recharge pit lid',
      ],
      hi: [
        'मानसून से पहले छत और नालियों की सफाई करें',
        'पहली बारिश और सूखे अंतराल का फर्स्ट-फ्लश बाहर निकालें',
        'छत को डिटर्जेंट और रसायनों से मुक्त रखें',
        'फिल्टर जाली, रेत/बजरी परत और पिट ढक्कन की जांच करें',
      ],
      mr: [
        'पावसाळ्यापूर्वी छत आणि पाण्याचे निचरे स्वच्छ करा',
        'पहिल्या पावसाचा व कोरड्या काळानंतरचा फर्स्ट-फ्लश बाहेर सोडा',
        'छत डिटर्जंट आणि रसायनांपासून मुक्त ठेवा',
        'फिल्टर जाळी, वाळू/खडीचा थर आणि पिट झाकण तपासा',
      ],
    };

    function CitizenApp() {
      const [tehsil, setTehsil] = useState('ALL');
      const [query, setQuery] = useState('');
      const [layoutId, setLayoutId] = useState('wanadongri');
      const [data, setData] = useState(null);
      const [tab, setTab] = useState('checkin');
      const [unit, setUnit] = useState('B-304');
      const [toast, setToast] = useState('');

      const [issueType, setIssueType] = useState('Leaking pipeline');
      const [severity, setSeverity] = useState('Moderate');
      const [desc, setDesc] = useState('');

      const [rwhLang, setRwhLang] = useState('en');
      const [rwhTaluka, setRwhTaluka] = useState('hingna');
      const [rwhArea, setRwhArea] = useState(1200);
      const [rwhUnit, setRwhUnit] = useState('sqft');
      const [rwhSurface, setRwhSurface] = useState('concrete');
      const [rwhOut, setRwhOut] = useState(null);

      const tehsils = Array.from(new Set(BOOT.layouts.map((x) => x.tehsil))).sort();
      const filteredLayouts = BOOT.layouts.filter((l) => {
        if (tehsil !== 'ALL' && l.tehsil !== tehsil) return false;
        if (query && !l.name.toLowerCase().includes(query.toLowerCase())) return false;
        return true;
      });

      useEffect(() => {
        if (filteredLayouts.length > 0 && !filteredLayouts.some((l) => l.id === layoutId)) {
          setLayoutId(filteredLayouts[0].id);
        }
      }, [tehsil, query]);

      const showToast = (msg) => {
        setToast(msg);
        setTimeout(() => setToast(''), 3200);
      };

      const loadColony = async (id = layoutId) => {
        const res = await fetch(`/api/colony?id=${encodeURIComponent(id)}`);
        const d = await res.json();
        setData(d);
      };

      useEffect(() => { loadColony(layoutId); }, [layoutId]);

      useEffect(() => {
        fetch('/api/rwh-calc', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ taluka_id: rwhTaluka, area: Number(rwhArea) || 0, unit: rwhUnit, surface_id: rwhSurface }),
        }).then((r) => r.json()).then(setRwhOut);
      }, [rwhTaluka, rwhArea, rwhUnit, rwhSurface]);

      const tabTransition = useTransition(tab, {
        from: { opacity: 0, y: 12 },
        enter: { opacity: 1, y: 0 },
        config: { tension: 310, friction: 26 },
      });

      const sendCheckin = async (status) => {
        await fetch('/api/checkin', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ layout_id: layoutId, unit, status }),
        });
        showToast('Daily water check-in recorded!');
        loadColony(layoutId);
      };

      const submitTicket = async () => {
        if (!desc.trim()) return showToast('Please describe the leak location first.');
        const res = await fetch('/api/ticket', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ layout_id: layoutId, issue_type: issueType, severity, description: desc }),
        });
        const d = await res.json();
        setDesc('');
        showToast(`Ticket #${d.ticket_id} sent to Utility Desk!`);
        loadColony(layoutId);
      };

      const confirmTanker = async (orderId) => {
        await fetch('/api/tanker-status', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ order_id: orderId, status: 'CONFIRMED' }),
        });
        showToast('Thank you! Tanker delivery confirmed.');
        loadColony(layoutId);
      };

      const toggleRwh = async (key, checked) => {
        await fetch('/api/rwh-check', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ layout_id: layoutId, key, checked }),
        });
        loadColony(layoutId);
      };

      const ev = data?.evaluation;
      const counts = data?.crowd?.counts || {};
      const recentLogs = data?.crowd?.recent_logs || [];
      const totalHomes = Math.max(data?.layout?.total_households || 1, (counts.NORMAL || 0) + (counts.LOW_PRESSURE || 0) + (counts.BOREWELL_DRY || 0));

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">💧</div>
              <div>
                <div>Citizen Water Portal</div>
                <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Welcome, {BOOT.user_name}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              <WallpaperSwitcher />
              {ev && <span className="wm-pill aqua">48h Rain: {ev.raw_stage1.rain_48h_mm} mm</span>}
              <a className="wm-btn" href="/login?role=verifier">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          <DynamicIslandToast message={toast} />

          <div className="wm-container">
            <div className="wm-grid-main">
              <div>
                <MagicSpringCard style={{ marginBottom: '18px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '12px' }}>Select Your Colony / Ward</h3>
                  <label className="wm-label">Filter by Tehsil</label>
                  <select className="wm-select" style={{ marginBottom: '10px' }} value={tehsil} onChange={(e) => setTehsil(e.target.value)}>
                    <option value="ALL">All Nagpur District (91 Locations)</option>
                    {tehsils.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>

                  <label className="wm-label">Search Location</label>
                  <input className="wm-input" style={{ marginBottom: '10px' }} placeholder="Hingna, Wanadongri, Wadi..." value={query} onChange={(e) => setQuery(e.target.value)} />

                  <label className="wm-label">Colony / Station</label>
                  <select className="wm-select" value={layoutId} onChange={(e) => setLayoutId(e.target.value)}>
                    {filteredLayouts.map((l) => (
                      <option key={l.id} value={l.id}>{l.category === 'Featured Pilot' ? '★ ' : ''}{l.name}</option>
                    ))}
                  </select>
                </MagicSpringCard>

                {ev && (
                  <BorderBeamCard>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ fontSize: '11.5px', fontWeight: 800, color: 'var(--wm-muted)' }}>COLONY SUPPLY HEALTH</span>
                      <StatusBadge status={ev.scarcity_status} />
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: 800, marginBottom: '6px' }}>{data.layout.name}</div>
                    <p style={{ fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5, marginBottom: '14px' }}>{ev.diagnosis}</p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div style={{ background: 'var(--wm-surface-soft)', padding: '11px', borderRadius: '13px', border: '1px solid var(--wm-border-subtle)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>PUMP RUNWAY</div>
                        <div className="mono" style={{ fontSize: '19px', fontWeight: 800, color: ev.groundwater_summary.pump_runway.days !== null && ev.groundwater_summary.pump_runway.days <= 20 ? 'var(--wm-melon)' : 'var(--wm-aqua)' }}>
                          {ev.groundwater_summary.pump_runway.days !== null ? `${ev.groundwater_summary.pump_runway.days} days` : 'Stable'}
                        </div>
                      </div>
                      <div style={{ background: 'var(--wm-surface-soft)', padding: '11px', borderRadius: '13px', border: '1px solid var(--wm-border-subtle)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>DRY HOMES</div>
                        <div className="mono" style={{ fontSize: '19px', fontWeight: 800 }}>
                          {ev.signals.signal_3_community_shortage.dry_percentage}%
                        </div>
                      </div>
                    </div>
                  </BorderBeamCard>
                )}
              </div>

              <div>
                <div style={{ marginBottom: '16px' }}>
                  <ContinuousTabs
                    activeId={tab}
                    onChange={setTab}
                    items={[
                      { id: 'checkin', label: '1. Daily Check-In' },
                      { id: 'tanker', label: `2. Tanker Tracker (${data?.tanker_orders?.length || 0})` },
                      { id: 'leak', label: `3. Report Leak (${data?.tickets?.length || 0})` },
                      { id: 'rwh', label: '4. RWH Calculator' },
                    ]}
                  />
                </div>

                {tabTransition((style, activeTab) => (
                  <animated.div style={style}>
                    {activeTab === 'checkin' && (
                      <MagicSpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '6px' }}>How is your tap / borewell water supply today?</h2>
                        <p style={{ fontSize: '13px', color: 'var(--wm-muted)', marginBottom: '16px' }}>
                          Your 1-tap check-in updates colony scarcity signals in real time for verifiers and tanker dispatchers.
                        </p>

                        <div style={{ maxWidth: '280px', marginBottom: '14px' }}>
                          <label className="wm-label">Your Flat / Plot / House No.</label>
                          <input className="wm-input" value={unit} onChange={(e) => setUnit(e.target.value)} />
                        </div>

                        <div className="wm-grid-3" style={{ marginBottom: '18px' }}>
                          <ShimmerSpringButton variant="mint" style={{ padding: '14px' }} onClick={() => sendCheckin('NORMAL')}>
                            🟢 Normal Supply
                          </ShimmerSpringButton>
                          <ShimmerSpringButton variant="amber" style={{ padding: '14px' }} onClick={() => sendCheckin('LOW_PRESSURE')}>
                            🟡 Low Pressure
                          </ShimmerSpringButton>
                          <ShimmerSpringButton variant="melon" style={{ padding: '14px' }} onClick={() => sendCheckin('BOREWELL_DRY')}>
                            🔴 Borewell Dry
                          </ShimmerSpringButton>
                        </div>

                        <div style={{ background: 'var(--wm-surface-soft)', padding: '14px', borderRadius: '15px', border: '1px solid var(--wm-border-subtle)', marginBottom: '16px' }}>
                          <div style={{ fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>Live Colony Household Breakdown</div>
                          <div style={{ height: '12px', borderRadius: '999px', overflow: 'hidden', display: 'flex', background: 'rgba(148,163,184,0.25)', marginBottom: '8px' }}>
                            <div style={{ width: `${((counts.NORMAL || 0) / totalHomes) * 100}%`, background: '#10B981', transition: 'width 0.4s ease' }} />
                            <div style={{ width: `${((counts.LOW_PRESSURE || 0) / totalHomes) * 100}%`, background: '#F59E0B', transition: 'width 0.4s ease' }} />
                            <div style={{ width: `${((counts.BOREWELL_DRY || 0) / totalHomes) * 100}%`, background: '#F43F5E', transition: 'width 0.4s ease' }} />
                          </div>
                          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '12px', fontWeight: 600, color: 'var(--wm-muted)' }}>
                            <span>🟢 Normal: <b>{counts.NORMAL || 0}</b></span>
                            <span>🟡 Low Pressure: <b>{counts.LOW_PRESSURE || 0}</b></span>
                            <span>🔴 Dry Borewell: <b>{counts.BOREWELL_DRY || 0}</b></span>
                          </div>
                        </div>

                        {recentLogs.length > 0 && (
                          <div>
                            <div style={{ fontSize: '13px', fontWeight: 800, marginBottom: '8px' }}>Recent Resident Check-Ins</div>
                            <div style={{ display: 'grid', gap: '8px' }}>
                              {recentLogs.slice(0, 5).map((log, idx) => (
                                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '9px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', fontSize: '12.5px' }}>
                                  <span><b>{log.unit}</b> · {log.by} <span style={{ color: 'var(--wm-muted)' }}>({log.time})</span></span>
                                  <StatusBadge status={log.status} />
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </MagicSpringCard>
                    )}

                    {activeTab === 'tanker' && data && (
                      <MagicSpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '12px' }}>Live Incoming Tanker Map & Delivery Proof</h2>
                        <NagpurMap
                          center={[data.layout.lat, data.layout.lon]}
                          zoom={12}
                          deps={[data]}
                          renderLayers={(map, group) => {
                            L.circleMarker([data.layout.lat, data.layout.lon], { radius: 9, color: '#0284C7', fillColor: '#0EA5E9', fillOpacity: 0.9 })
                              .bindPopup(`<b>${data.layout.name}</b><br>Your Colony`).addTo(group);

                            BOOT.depots.forEach((d) => {
                              L.marker([d.lat, d.lon]).bindPopup(`<b>${d.name}</b>`).addTo(group);
                            });

                            (data.tanker_orders || []).forEach((o) => {
                              const dep = BOOT.depots.find((d) => d.id === o.depot_id);
                              if (dep && (o.status === 'DISPATCHED' || o.status === 'UNLOADED')) {
                                const line = L.polyline([[dep.lat, dep.lon], [data.layout.lat, data.layout.lon]], { color: '#10B981', weight: 4, dashArray: '8,8' }).addTo(group);
                                L.circleMarker([(dep.lat + data.layout.lat) / 2, (dep.lon + data.layout.lon) / 2], { radius: 7, color: '#F43F5E', fillColor: '#F43F5E', fillOpacity: 1 })
                                  .bindPopup(`<b>🚛 ${o.vehicle_no}</b><br>${o.volume_l.toLocaleString()} L`).addTo(group);
                                map.fitBounds(line.getBounds(), { padding: [45, 45] });
                              }
                            });
                          }}
                        />

                        <div style={{ marginTop: '14px', display: 'grid', gap: '10px' }}>
                          {(data.tanker_orders || []).length === 0 && (
                            <div style={{ fontSize: '13px', color: 'var(--wm-muted)' }}>No active tanker orders for this colony right now.</div>
                          )}
                          {(data.tanker_orders || []).map((o) => (
                            <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', padding: '12px 14px', borderRadius: '14px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)' }}>
                              <div>
                                <div style={{ fontWeight: 800, fontSize: '14px' }}>{o.id} · {o.volume_l.toLocaleString()} L ({o.vehicle_no || 'Awaiting Truck'})</div>
                                <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>From {o.depot_name || 'Pending Depot'} · {o.distance_km || '--'} km</div>
                              </div>
                              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                <StatusBadge status={o.status} />
                                {(o.status === 'DISPATCHED' || o.status === 'UNLOADED') && (
                                  <ShimmerSpringButton variant="mint" onClick={() => confirmTanker(o.id)}>✓ Confirm Water Received</ShimmerSpringButton>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </MagicSpringCard>
                    )}

                    {activeTab === 'leak' && (
                      <MagicSpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '12px' }}>Report Pipeline Leak / Pump Breakdown</h2>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '10px' }}>
                          <div>
                            <label className="wm-label">Issue Type</label>
                            <select className="wm-select" value={issueType} onChange={(e) => setIssueType(e.target.value)}>
                              <option>Leaking pipeline</option>
                              <option>Overflowing storage tank</option>
                              <option>Public tap wastage</option>
                              <option>Submersible pump fault</option>
                              <option>Broken RWH unit</option>
                            </select>
                          </div>
                          <div>
                            <label className="wm-label">Severity</label>
                            <select className="wm-select" value={severity} onChange={(e) => setSeverity(e.target.value)}>
                              <option>Minor</option>
                              <option>Moderate</option>
                              <option>Severe</option>
                            </select>
                          </div>
                        </div>
                        <label className="wm-label">Landmark & Issue Details</label>
                        <textarea className="wm-textarea" rows="2" style={{ marginBottom: '12px' }} placeholder="e.g. Gate 2 feeder valve leaking heavily..." value={desc} onChange={(e) => setDesc(e.target.value)} />
                        <ShimmerSpringButton variant="primary" onClick={submitTicket}>Submit Ticket to Utility Desk</ShimmerSpringButton>

                        <h3 style={{ fontSize: '14px', fontWeight: 800, marginTop: '20px', marginBottom: '10px' }}>Colony Tickets</h3>
                        <div style={{ display: 'grid', gap: '8px' }}>
                          {(data?.tickets || []).length === 0 && (
                            <div style={{ fontSize: '13px', color: 'var(--wm-muted)' }}>No leak or pump tickets logged in this colony yet.</div>
                          )}
                          {(data?.tickets || []).map((t) => (
                            <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '11px 14px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)' }}>
                              <div>
                                <div style={{ fontWeight: 700, fontSize: '13px' }}>#{t.id} · {t.issue_type} ({t.severity})</div>
                                <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>{t.description} · {t.created_at}</div>
                              </div>
                              <StatusBadge status={t.status} />
                            </div>
                          ))}
                        </div>
                      </MagicSpringCard>
                    )}

                    {activeTab === 'rwh' && (
                      <MagicSpringCard>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '14px' }}>
                          <h2 style={{ fontSize: '17px', fontWeight: 800 }}>Nagpur District Rainwater Harvesting Calculator</h2>
                          <select className="wm-select" style={{ width: 'auto' }} value={rwhLang} onChange={(e) => setRwhLang(e.target.value)}>
                            <option value="en">English</option>
                            <option value="hi">हिंदी</option>
                            <option value="mr">मराठी</option>
                          </select>
                        </div>

                        <div className="wm-grid-3" style={{ marginBottom: '14px' }}>
                          <div>
                            <label className="wm-label">Nagpur Taluka (14)</label>
                            <select className="wm-select" value={rwhTaluka} onChange={(e) => setRwhTaluka(e.target.value)}>
                              {BOOT.talukas.map((t) => <option key={t.id} value={t.id}>{t.name} ({t.rainfall_mm} mm)</option>)}
                            </select>
                          </div>
                          <div>
                            <label className="wm-label">Roof Area</label>
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <input className="wm-input" type="number" value={rwhArea} onChange={(e) => setRwhArea(e.target.value)} />
                              <select className="wm-select" style={{ width: '95px' }} value={rwhUnit} onChange={(e) => setRwhUnit(e.target.value)}>
                                <option value="sqft">Sq.Ft</option>
                                <option value="sqm">Sq.M</option>
                              </select>
                            </div>
                          </div>
                          <div>
                            <label className="wm-label">Roof Surface</label>
                            <select className="wm-select" value={rwhSurface} onChange={(e) => setRwhSurface(e.target.value)}>
                              <option value="concrete">Concrete / RCC (0.85)</option>
                              <option value="metal">Metal / GI Sheet (0.90)</option>
                              <option value="tiled">Tiled / Sloped (0.75)</option>
                            </select>
                          </div>
                        </div>

                        {rwhOut && (
                          <div className="wm-grid-3" style={{ marginBottom: '16px' }}>
                            <div style={{ background: 'var(--wm-aqua-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--wm-aqua)' }}>GROSS CAPTURED</div>
                              <div className="mono" style={{ fontSize: '20px', fontWeight: 800 }}>{rwhOut.gross_l.toLocaleString('en-IN')} L</div>
                            </div>
                            <div style={{ background: 'var(--wm-amber-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--wm-amber)' }}>FIRST-FLUSH DIVERTED</div>
                              <div className="mono" style={{ fontSize: '20px', fontWeight: 800 }}>{rwhOut.first_flush_l.toLocaleString('en-IN')} L</div>
                            </div>
                            <div style={{ background: 'var(--wm-mint-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--wm-mint)' }}>NET EFFECTIVE HARVEST</div>
                              <div className="mono" style={{ fontSize: '20px', fontWeight: 800, color: 'var(--wm-mint)' }}>{rwhOut.net_l.toLocaleString('en-IN')} L</div>
                            </div>
                          </div>
                        )}

                        <div style={{ fontSize: '13px', fontWeight: 800, marginBottom: '8px' }}>Monsoon Readiness Checklist</div>
                        {(RWH_RULES[rwhLang] || RWH_RULES.en).map((rule, idx) => {
                          const key = `r_${idx}`;
                          const checked = !!(data?.rwh_checks || {})[key];
                          return (
                            <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '9px 12px', borderRadius: '11px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', marginBottom: '6px', cursor: 'pointer', fontSize: '13px' }}>
                              <input type="checkbox" checked={checked} onChange={(e) => toggleRwh(key, e.target.checked)} />
                              <span>{rule}</span>
                            </label>
                          );
                        })}
                      </MagicSpringCard>
                    )}
                  </animated.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    }

    // -----------------------------------------------------------------------
    // VIEW 2: FIELD VERIFIER PORTAL (/verifier)
    // -----------------------------------------------------------------------
    function VerifierApp() {
      const [query, setQuery] = useState('');
      const [layoutId, setLayoutId] = useState('wanadongri');
      const [data, setData] = useState(null);
      const [vDepth, setVDepth] = useState(18.6);
      const [vLast, setVLast] = useState(16.8);
      const [vDays, setVDays] = useState(7);
      const [indentVol, setIndentVol] = useState(10000);
      const [toast, setToast] = useState('');

      const list = BOOT.layouts.filter((l) => !query || l.name.toLowerCase().includes(query.toLowerCase()) || l.tehsil.toLowerCase().includes(query.toLowerCase()));

      useEffect(() => {
        if (list.length > 0 && !list.some((l) => l.id === layoutId)) {
          setLayoutId(list[0].id);
        }
      }, [query]);

      const showToast = (msg) => {
        setToast(msg);
        setTimeout(() => setToast(''), 3200);
      };

      const loadColony = async (id = layoutId) => {
        const res = await fetch(`/api/colony?id=${encodeURIComponent(id)}`);
        const d = await res.json();
        setData(d);
        setVDepth(d.verifier_record.verifier_depth_m);
        setVLast(d.verifier_record.last_recorded_depth_m);
        setVDays(d.verifier_record.days_since_last || 7);
      };

      useEffect(() => { loadColony(layoutId); }, [layoutId]);

      const saveReading = async () => {
        await fetch('/api/verifier-update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            layout_id: layoutId,
            verifier_depth_m: Number(vDepth),
            last_recorded_depth_m: Number(vLast),
            days_since_last: Number(vDays),
          }),
        });
        showToast('Well depth verified & calibrated!');
        loadColony(layoutId);
      };

      const raiseIndent = async () => {
        const res = await fetch('/api/tanker-indent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ layout_id: layoutId, volume_l: Number(indentVol) }),
        });
        const d = await res.json();
        showToast(`Verified Tanker Indent ${d.order.id} sent to Utility!`);
      };

      const ev = data?.evaluation;
      const series = ev?.raw_stage1?.calibrated_series || [];

      const renderHydrograph = () => {
        if (series.length < 2) return null;
        const w = 600, h = 195, padL = 46, padR = 18, padT = 18, padB = 26;
        const all = series.map((p) => p.gov_depth_m).concat(series.map((p) => p.calibrated_layout_depth_m));
        const minD = Math.floor(Math.min(...all) - 0.5);
        const maxD = Math.ceil(Math.max(...all) + 0.5);
        const midD = ((minD + maxD) / 2).toFixed(1);
        const xS = (i) => padL + (i / (series.length - 1)) * (w - padL - padR);
        const yS = (d) => padT + ((d - minD) / Math.max(maxD - minD, 0.5)) * (h - padT - padB);
        const pGov = series.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xS(i).toFixed(1)} ${yS(p.gov_depth_m).toFixed(1)}`).join(' ');
        const pCal = series.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xS(i).toFixed(1)} ${yS(p.calibrated_layout_depth_m).toFixed(1)}`).join(' ');

        return (
          <svg viewBox="0 0 600 195" style={{ width: '100%', height: '195px', background: 'var(--wm-surface-soft)', borderRadius: '14px', border: '1px solid var(--wm-border-subtle)' }}>
            <line x1={padL} y1={padT} x2={w - padR} y2={padT} stroke="var(--wm-border-subtle)" strokeDasharray="4 4" />
            <line x1={padL} y1={(padT + h - padB) / 2} x2={w - padR} y2={(padT + h - padB) / 2} stroke="var(--wm-border-subtle)" strokeDasharray="4 4" />
            <line x1={padL} y1={h - padB} x2={w - padR} y2={h - padB} stroke="var(--wm-border-subtle)" />
            <text x="8" y={padT + 4} fill="var(--wm-muted)" fontSize="10" fontWeight="700">{minD}m</text>
            <text x="8" y={(padT + h - padB) / 2 + 4} fill="var(--wm-muted)" fontSize="10" fontWeight="700">{midD}m</text>
            <text x="8" y={h - padB} fill="var(--wm-muted)" fontSize="10" fontWeight="700">{maxD}m</text>
            <text x={padL} y={h - 8} fill="var(--wm-muted)" fontSize="10" fontWeight="600">7 Days Ago</text>
            <text x={w - padR - 32} y={h - 8} fill="var(--wm-muted)" fontSize="10" fontWeight="600">Now</text>
            <path d={pGov} fill="none" stroke="#0EA5E9" strokeWidth="2.5" strokeLinecap="round" />
            <path d={pCal} fill="none" stroke="#F43F5E" strokeWidth="3" strokeLinecap="round" />
          </svg>
        );
      };

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">📡</div>
              <div>
                <div>Field Verifier Portal</div>
                <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Verifier: {BOOT.user_name}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              <WallpaperSwitcher />
              {ev && <span className="wm-pill mint">48h Rain: {ev.raw_stage1.rain_48h_mm} mm</span>}
              <a className="wm-btn" href="/login?role=utility">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          <DynamicIslandToast message={toast} />

          <div className="wm-container">
            <div className="wm-grid-main">
              <div>
                <MagicSpringCard style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>1. Assigned Colony / Ward</h3>
                  <input className="wm-input" style={{ marginBottom: '8px' }} placeholder="Search 91 locations..." value={query} onChange={(e) => setQuery(e.target.value)} />
                  <select className="wm-select" value={layoutId} onChange={(e) => setLayoutId(e.target.value)}>
                    {list.map((l) => <option key={l.id} value={l.id}>{l.category === 'Featured Pilot' ? '★ ' : ''}{l.name}</option>)}
                  </select>
                </MagicSpringCard>

                <MagicSpringCard delay={60} style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>2. Reference Well Depth Entry</h3>
                  <label className="wm-label">Today's Measured Depth (m bgl)</label>
                  <input className="wm-input" type="number" step="0.1" style={{ marginBottom: '8px' }} value={vDepth} onChange={(e) => setVDepth(e.target.value)} />
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '10px' }}>
                    <div>
                      <label className="wm-label">Previous Depth (m)</label>
                      <input className="wm-input" type="number" step="0.1" value={vLast} onChange={(e) => setVLast(e.target.value)} />
                    </div>
                    <div>
                      <label className="wm-label">Elapsed Days</label>
                      <select className="wm-select" value={vDays} onChange={(e) => setVDays(e.target.value)}>
                        <option value="7">7 days</option>
                        <option value="14">14 days</option>
                        <option value="30">30 days</option>
                      </select>
                    </div>
                  </div>
                  {ev?.groundwater_summary?.verifier_validation && (
                    <div style={{
                      padding: '9px 11px', borderRadius: '11px', fontSize: '12px', fontWeight: 700, marginBottom: '10px',
                      background: ev.groundwater_summary.verifier_validation.status === 'VERIFIED' ? 'var(--wm-mint-soft)' : 'var(--wm-melon-soft)',
                      color: ev.groundwater_summary.verifier_validation.status === 'VERIFIED' ? 'var(--wm-mint)' : 'var(--wm-melon)',
                    }}>
                      {ev.groundwater_summary.verifier_validation.status}: {ev.groundwater_summary.verifier_validation.reason}
                    </div>
                  )}
                  <ShimmerSpringButton variant="primary" style={{ width: '100%' }} onClick={saveReading}>Verify & Update Calibration</ShimmerSpringButton>
                </MagicSpringCard>

                <MagicSpringCard delay={110}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '6px' }}>3. Verified Tanker Indent (55 LPCD)</h3>
                  {data && (
                    <div style={{ fontSize: '12px', color: 'var(--wm-aqua)', background: 'var(--wm-aqua-soft)', padding: '9px 11px', borderRadius: '11px', marginBottom: '10px', fontWeight: 700 }}>
                      Recommended: {data.recommended_tanker.litres_per_day.toLocaleString()} L/day ({data.recommended_tanker.trips_10k} trips) for {data.recommended_tanker.affected_homes} homes.
                    </div>
                  )}
                  <select className="wm-select" style={{ marginBottom: '10px' }} value={indentVol} onChange={(e) => setIndentVol(e.target.value)}>
                    <option value="10000">10,000 L (1 Tanker Trip)</option>
                    <option value="20000">20,000 L (2 Tanker Trips)</option>
                    <option value="30000">30,000 L (3 Tanker Trips)</option>
                  </select>
                  <ShimmerSpringButton variant="mint" style={{ width: '100%' }} onClick={raiseIndent}>Send Verified Indent to Utility</ShimmerSpringButton>
                </MagicSpringCard>
              </div>

              <div>
                {ev && (
                  <>
                    <BorderBeamCard style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <h2 style={{ fontSize: '18px', fontWeight: 800 }}>{data.layout.name}</h2>
                        <StatusBadge status={ev.scarcity_status} />
                      </div>
                      <p style={{ fontSize: '13px', color: 'var(--wm-muted)', marginBottom: '14px' }}>{ev.diagnosis}</p>

                      <div className="wm-grid-3">
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border-subtle)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>LIVE CALIBRATED DEPTH</div>
                          <div className="mono" style={{ fontSize: '21px', fontWeight: 800 }}>{ev.groundwater_summary.live_calibrated_depth_m} m</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Offset {ev.raw_stage1.local_offset_m >= 0 ? '+' : ''}{ev.raw_stage1.local_offset_m}m vs CGWB</div>
                        </div>
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border-subtle)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>DEPLETION VELOCITY</div>
                          <div className="mono" style={{ fontSize: '21px', fontWeight: 800 }}>{ev.raw_stage1.depletion_velocity_m_per_week} m/wk</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Deficit: {ev.signals.signal_1_aquifer_stress.deficit_m} m</div>
                        </div>
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border-subtle)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>PUMP RUNWAY</div>
                          <div className="mono" style={{ fontSize: '21px', fontWeight: 800 }}>{ev.groundwater_summary.pump_runway.days !== null ? `${ev.groundwater_summary.pump_runway.days} d` : 'Stable'}</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>{ev.groundwater_summary.pump_runway.label}</div>
                        </div>
                      </div>
                    </BorderBeamCard>

                    <MagicSpringCard delay={80} style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                        <h3 style={{ fontSize: '15px', fontWeight: 800 }}>7-Day 6-Hourly Calibrated Hydrograph</h3>
                        <span className="wm-pill aqua">CGWB: {ev.groundwater_summary.matched_gov_station} ({ev.groundwater_summary.station_distance_km} km)</span>
                      </div>
                      {renderHydrograph()}
                      <div style={{ display: 'flex', justifyContent: 'center', gap: '18px', fontSize: '11.5px', color: 'var(--wm-muted)', marginTop: '8px', fontWeight: 700 }}>
                        <span style={{ color: '#0284C7' }}>━━ Raw CGWB 6-Hourly Sensor</span>
                        <span style={{ color: '#F43F5E' }}>━━ Offset-Calibrated Colony Depth</span>
                      </div>
                    </MagicSpringCard>

                    <MagicSpringCard delay={120}>
                      <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>3-Signal Scarcity & Fault Breakdown</h3>
                      {[
                        { title: 'Signal 1: Aquifer Stress (>2.5m Deficit or ≤1.5m Col)', active: ev.signals.signal_1_aquifer_stress.active },
                        { title: 'Signal 2: Rapid Depletion (>0.5m/week)', active: ev.signals.signal_2_rapid_depletion.active },
                        { title: 'Signal 3: Resident Shortage (≥30% Dry Homes)', active: ev.signals.signal_3_community_shortage.active },
                      ].map((s) => (
                        <div key={s.title} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', marginBottom: '8px', fontSize: '13px' }}>
                          <span style={{ fontWeight: 700 }}>{s.active ? '⚠️' : '✓'} {s.title}</span>
                          <StatusBadge status={s.active ? 'RED' : 'GREEN'} />
                        </div>
                      ))}
                    </MagicSpringCard>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }

    // -----------------------------------------------------------------------
    // VIEW 3: UTILITY & TANKER PORTAL (/utility)
    // -----------------------------------------------------------------------
    function UtilityApp() {
      const [ov, setOv] = useState(null);
      const [destId, setDestId] = useState('wanadongri');
      const [depotId, setDepotId] = useState('AUTO');
      const [vol, setVol] = useState(10000);
      const [toast, setToast] = useState('');

      const showToast = (msg) => {
        setToast(msg);
        setTimeout(() => setToast(''), 3200);
      };

      const refresh = async () => {
        const res = await fetch('/api/utility-overview');
        const d = await res.json();
        setOv(d);
      };

      useEffect(() => { refresh(); }, []);

      const dispatchNow = async () => {
        const res = await fetch('/api/tanker-dispatch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ layout_id: destId, depot_id: depotId, volume_l: Number(vol) }),
        });
        const d = await res.json();
        if (!res.ok) return showToast(d.error || 'Dispatch failed');
        showToast(`Dispatched ${d.order.vehicle_no} from ${d.order.depot_name}`);
        refresh();
      };

      const dispatchExisting = async (orderId) => {
        const res = await fetch('/api/tanker-dispatch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ order_id: orderId, depot_id: 'AUTO' }),
        });
        const d = await res.json();
        if (!res.ok) return showToast(d.error || 'Dispatch failed');
        showToast(`Order ${orderId} dispatched!`);
        refresh();
      };

      const markUnloaded = async (orderId) => {
        await fetch('/api/tanker-status', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ order_id: orderId, status: 'UNLOADED' }),
        });
        showToast(`Order ${orderId} marked unloaded.`);
        refresh();
      };

      const refillDepot = async (id) => {
        await fetch('/api/depot-refill', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ depot_id: id }),
        });
        showToast('Depot stock & fleet refilled.');
        refresh();
      };

      const resolveTicket = async (id) => {
        await fetch('/api/ticket-resolve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ticket_id: id }),
        });
        showToast(`Ticket #${id} resolved.`);
        refresh();
      };

      const selectedColony = ov?.priority_colonies?.find((c) => c.layout.id === destId);
      const isGreenZone = selectedColony?.evaluation?.scarcity_status === 'GREEN';

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">🚛</div>
              <div>
                <div>Utility & Tanker Operations</div>
                <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Operator: {BOOT.user_name}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              <WallpaperSwitcher />
              <a className="wm-btn" href="/login?role=citizen">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          <DynamicIslandToast message={toast} />

          {ov && (
            <div className="wm-container">
              <div className="wm-grid-main">
                <div>
                  <MagicSpringCard style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>1. Tanker Dispatch Console</h3>
                    <label className="wm-label">Destination Colony</label>
                    <select className="wm-select" style={{ marginBottom: '8px' }} value={destId} onChange={(e) => setDestId(e.target.value)}>
                      {ov.priority_colonies.map((c) => (
                        <option key={c.layout.id} value={c.layout.id}>
                          {c.layout.name} [{c.evaluation.scarcity_status} · Runway {c.evaluation.groundwater_summary.pump_runway.days ?? 'Stable'}d]
                        </option>
                      ))}
                    </select>

                    {isGreenZone && (
                      <div style={{ background: 'var(--wm-amber-soft)', color: 'var(--wm-amber)', padding: '8px 11px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>
                        ⚠️ Note: Aquifer status is GREEN here. Check Surface Leak Tickets before sending emergency tankers.
                      </div>
                    )}

                    <label className="wm-label">Source Depot</label>
                    <select className="wm-select" style={{ marginBottom: '8px' }} value={depotId} onChange={(e) => setDepotId(e.target.value)}>
                      <option value="AUTO">Auto-Select Nearest Depot with Stock</option>
                      {ov.depots.map((d) => <option key={d.id} value={d.id}>{d.name} ({d.current_stock_l.toLocaleString()} L)</option>)}
                    </select>

                    <label className="wm-label">Tanker Volume</label>
                    <select className="wm-select" style={{ marginBottom: '12px' }} value={vol} onChange={(e) => setVol(e.target.value)}>
                      <option value="5000">5,000 L Tanker</option>
                      <option value="10000">10,000 L Tanker</option>
                      <option value="15000">15,000 L Tanker</option>
                    </select>

                    <ShimmerSpringButton variant="primary" style={{ width: '100%' }} onClick={dispatchNow}>Assign & Dispatch Tanker</ShimmerSpringButton>
                  </MagicSpringCard>

                  <MagicSpringCard delay={60} style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>2. Tanker Depots & Fleet Stock</h3>
                    {ov.depots.map((d) => (
                      <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13px' }}>{d.name}</div>
                          <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)' }}>Stock: {d.current_stock_l.toLocaleString()} / {d.max_capacity_l.toLocaleString()} L · Trucks: {d.trucks_ready}/{d.trucks_total}</div>
                        </div>
                        <ShimmerSpringButton onClick={() => refillDepot(d.id)}>+ Refill</ShimmerSpringButton>
                      </div>
                    ))}
                  </MagicSpringCard>

                  <MagicSpringCard delay={110}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>3. Surface Leak & Valve Maintenance Queue</h3>
                    {ov.tickets.map((t) => (
                      <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '12.5px' }}>#{t.id} · {t.issue_type} @ {t.layout_name}</div>
                          <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)' }}>{t.description}</div>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <StatusBadge status={t.status} />
                          {t.status !== 'RESOLVED' && <ShimmerSpringButton variant="mint" onClick={() => resolveTicket(t.id)}>Resolve</ShimmerSpringButton>}
                        </div>
                      </div>
                    ))}
                  </MagicSpringCard>
                </div>

                <div>
                  <BorderBeamCard style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <h3 style={{ fontSize: '16px', fontWeight: 800 }}>4. Nagpur Scarcity & Live Tanker Route Map</h3>
                      <span className="wm-pill aqua"><span className="live-dot" /> Live Fleet & Colony Stress</span>
                    </div>
                    <NagpurMap
                      deps={[ov]}
                      renderLayers={(map, group) => {
                        ov.priority_colonies.forEach((c) => {
                          const st = c.evaluation.scarcity_status;
                          const col = st === 'RED' ? '#F43F5E' : (st === 'YELLOW' ? '#F59E0B' : '#10B981');
                          L.circleMarker([c.layout.lat, c.layout.lon], { radius: 9, color: col, fillColor: col, fillOpacity: 0.85 })
                            .bindPopup(`<b>${c.layout.name}</b><br>Status: ${st}<br>Depth: ${c.evaluation.groundwater_summary.live_calibrated_depth_m} m`).addTo(group);
                        });
                        ov.depots.forEach((d) => {
                          L.marker([d.lat, d.lon]).bindPopup(`<b>🚛 ${d.name}</b><br>Stock: ${d.current_stock_l.toLocaleString()} L`).addTo(group);
                        });
                        ov.tanker_orders.forEach((o) => {
                          if (o.status === 'DISPATCHED' || o.status === 'UNLOADED') {
                            const dep = ov.depots.find((d) => d.id === o.depot_id);
                            const dest = ov.priority_colonies.find((c) => c.layout.id === o.layout_id);
                            if (dep && dest) {
                              L.polyline([[dep.lat, dep.lon], [dest.layout.lat, dest.layout.lon]], { color: '#0284C7', weight: 4, dashArray: '8,8' }).addTo(group);
                            }
                          }
                        });
                      }}
                    />
                  </BorderBeamCard>

                  <MagicSpringCard delay={70} style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>5. Verified Tanker Indents & Active Deliveries</h3>
                    {ov.tanker_orders.map((o) => (
                      <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', padding: '11px 13px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border-subtle)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13.5px' }}>{o.id} · {o.layout_name} ({o.volume_l.toLocaleString()} L)</div>
                          <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>Verified by {o.verified_by} · {o.vehicle_no || 'Pending Truck'} ({o.depot_name || 'Unassigned'})</div>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <StatusBadge status={o.status} />
                          {o.status === 'PENDING_DISPATCH' && <ShimmerSpringButton variant="primary" onClick={() => dispatchExisting(o.id)}>Dispatch</ShimmerSpringButton>}
                          {o.status === 'DISPATCHED' && <ShimmerSpringButton variant="mint" onClick={() => markUnloaded(o.id)}>Mark Unloaded</ShimmerSpringButton>}
                        </div>
                      </div>
                    ))}
                  </MagicSpringCard>

                  <MagicSpringCard delay={120}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>6. Priority Scarcity Triage Table</h3>
                    <table>
                      <thead>
                        <tr>
                          <th>Colony</th>
                          <th>Calibrated Depth</th>
                          <th>Pump Runway</th>
                          <th>Dry %</th>
                          <th>48h Rain</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ov.priority_colonies.map((c) => {
                          const e = c.evaluation;
                          return (
                            <tr key={c.layout.id}>
                              <td style={{ fontWeight: 700 }}>{c.layout.name}</td>
                              <td className="mono">{e.groundwater_summary.live_calibrated_depth_m} m</td>
                              <td className="mono">{e.groundwater_summary.pump_runway.days ?? 'Stable'} d</td>
                              <td className="mono">{e.signals.signal_3_community_shortage.dry_percentage}%</td>
                              <td className="mono">{e.raw_stage1.rain_48h_mm} mm</td>
                              <td><StatusBadge status={e.scarcity_status} /></td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </MagicSpringCard>
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }

    const root = createRoot(document.getElementById('root'));
    let activeView = <LandingLoginApp />;
    if (MODE === 'citizen') activeView = <CitizenApp />;
    else if (MODE === 'verifier') activeView = <VerifierApp />;
    else if (MODE === 'utility') activeView = <UtilityApp />;

    root.render(<UIErrorBoundary>{activeView}</UIErrorBoundary>);
  </script>
</body>
</html>"""
    return (
        html
        .replace("__PAGE_TITLE__", title)
        .replace("__PAGE_MODE__", page_mode)
        .replace("__BOOTSTRAP_JSON__", bootstrap_json)
    )


class WatermelonRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def _get_session(self) -> dict | None:
        raw_cookie = self.headers.get("Cookie", "")
        if not raw_cookie:
            return None
        c = http.cookies.SimpleCookie()
        c.load(raw_cookie)
        morsel = c.get("nagpur_session")
        if not morsel:
            return None
        return backend.SESSIONS.get(morsel.value)

    def _send_html(self, html: str, cookie_header: str | None = None):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_json(self, code: int, payload, cookie_header: str | None = None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _redirect(self, location: str, cookie_header: str | None = None):
        self.send_response(302)
        self.send_header("Location", location)
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)
        sess = self._get_session()

        if url.path in ("/", "/login"):
            pre_role = (qs.get("role") or ["citizen"])[0]
            if pre_role not in backend.ROLE_META:
                pre_role = "citizen"
            boot = json.dumps({"preselect_role": pre_role, "role_defaults": backend.ROLE_META})
            self._send_html(build_react_page("JalSetu Nagpur — Watermelon UI Network", "login", boot))
            return

        if url.path == "/logout":
            raw_cookie = self.headers.get("Cookie", "")
            c = http.cookies.SimpleCookie()
            c.load(raw_cookie)
            if "nagpur_session" in c:
                backend.SESSIONS.pop(c["nagpur_session"].value, None)
            self._redirect("/login", "nagpur_session=; Path=/; Max-Age=0")
            return

        if url.path == "/citizen":
            if not sess or sess["role"] != "citizen":
                self._redirect("/login?role=citizen")
                return
            boot = json.dumps({
                "user_name": sess["name"],
                "layouts": backend.ALL_LAYOUTS,
                "talukas": backend.NAGPUR_TALUKAS,
                "depots": backend.STATE["depots"],
            })
            self._send_html(build_react_page("Citizen Portal — JalSetu Nagpur", "citizen", boot))
            return

        if url.path == "/verifier":
            if not sess or sess["role"] != "verifier":
                self._redirect("/login?role=verifier")
                return
            boot = json.dumps({
                "user_name": sess["name"],
                "layouts": backend.ALL_LAYOUTS,
            })
            self._send_html(build_react_page("Field Verifier Portal — JalSetu Nagpur", "verifier", boot))
            return

        if url.path == "/utility":
            if not sess or sess["role"] != "utility":
                self._redirect("/login?role=utility")
                return
            boot = json.dumps({"user_name": sess["name"]})
            self._send_html(build_react_page("Utility & Tanker Operations — JalSetu Nagpur", "utility", boot))
            return

        if url.path == "/api/public-summary":
            code, payload = backend.api_public_summary()
            self._send_json(code, payload)
            return

        if url.path == "/api/colony":
            col_id = (qs.get("id") or ["wanadongri"])[0]
            code, payload = backend.api_colony_detail(col_id)
            self._send_json(code, payload)
            return

        if url.path == "/api/utility-overview":
            code, payload = backend.api_utility_overview()
            self._send_json(code, payload)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if url.path in ("/api/login", "/api/register"):
            code, payload, cookie = backend.api_auth(url.path == "/api/register", data)
            self._send_json(code, payload, cookie)
            return

        sess = self._get_session()

        if url.path == "/api/checkin":
            code, payload = backend.api_checkin(data, sess)
            self._send_json(code, payload)
            return

        if url.path == "/api/ticket":
            code, payload = backend.api_create_ticket(data, sess)
            self._send_json(code, payload)
            return

        if url.path == "/api/ticket-resolve":
            code, payload = backend.api_resolve_ticket(data)
            self._send_json(code, payload)
            return

        if url.path == "/api/rwh-check":
            code, payload = backend.api_rwh_check(data)
            self._send_json(code, payload)
            return

        if url.path == "/api/rwh-calc":
            out = backend.calculate_rwh(
                taluka_id=data.get("taluka_id", "hingna"),
                area=float(data.get("area", 0)),
                unit=data.get("unit", "sqft"),
                surface_id=data.get("surface_id", "concrete"),
            )
            self._send_json(200, out)
            return

        if url.path == "/api/verifier-update":
            code, payload = backend.api_verifier_update(data, sess)
            self._send_json(code, payload)
            return

        if url.path == "/api/tanker-indent":
            code, payload = backend.api_tanker_indent(data, sess)
            self._send_json(code, payload)
            return

        if url.path == "/api/tanker-dispatch":
            code, payload = backend.api_tanker_dispatch(data, sess)
            self._send_json(code, payload)
            return

        if url.path == "/api/tanker-status":
            code, payload = backend.api_tanker_status(data)
            self._send_json(code, payload)
            return

        if url.path == "/api/depot-refill":
            code, payload = backend.api_depot_refill(data)
            self._send_json(code, payload)
            return

        self.send_response(404)
        self.end_headers()


def run_server():
    server = ThreadingHTTPServer(("127.0.0.1", backend.PORT), WatermelonRequestHandler)
    print("\n=======================================================")
    print(f" JalSetu Nagpur — Watermelon UI + Magic/Cult Glass ({len(backend.ALL_LAYOUTS)} locations)")
    print(f" Backend: jalsetu_backend.py | Frontend: watermelon_ui.py")
    print(f" Open Portal: http://127.0.0.1:{backend.PORT}/login")
    print(" Press Ctrl+C to stop.")
    print("=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    run_server()
