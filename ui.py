"""
watermelon_ui.py
----------------
Watermelon UI + React Spring Frontend & HTTP Server for JalSetu.
Imports all backend logic, hydrology calibration, and tanker dispatch APIs from `jalsetu_backend.py`.
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
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.7/babel.min.js"></script>
  <style>
    :root {
      /* Watermelon UI Fresh Daylight Palette */
      --wm-bg: #F3F8FC;
      --wm-surface: #FFFFFF;
      --wm-surface-soft: #F8FBFF;
      --wm-border: #E2ECF5;
      --wm-text: #0F172A;
      --wm-muted: #52647A;
      --wm-aqua: #0284C7;
      --wm-aqua-bright: #0EA5E9;
      --wm-aqua-soft: #E0F2FE;
      --wm-melon: #F43F5E;
      --wm-melon-soft: #FFE4E6;
      --wm-mint: #10B981;
      --wm-mint-soft: #D1FAE5;
      --wm-amber: #F59E0B;
      --wm-amber-soft: #FEF3C7;
      --wm-shadow: 0 12px 32px -12px rgba(15, 23, 42, 0.08);
      --wm-shadow-hover: 0 18px 38px -12px rgba(2, 132, 199, 0.16);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
    body {
      background:
        radial-gradient(circle at 8% 0%, rgba(14, 165, 233, 0.10), transparent 36%),
        radial-gradient(circle at 92% 6%, rgba(244, 63, 94, 0.07), transparent 32%),
        var(--wm-bg);
      color: var(--wm-text);
      min-height: 100vh;
    }
    .wm-nav {
      position: sticky; top: 0; z-index: 40;
      background: rgba(255, 255, 255, 0.88);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--wm-border);
      padding: 13px 26px;
      display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
    }
    .wm-brand {
      display: flex; align-items: center; gap: 11px;
      font-weight: 800; font-size: 17px; color: var(--wm-text); letter-spacing: -0.02em;
    }
    .wm-logo-drop {
      width: 36px; height: 36px; border-radius: 12px;
      background: linear-gradient(135deg, #0284C7 0%, #38BDF8 55%, #10B981 100%);
      display: grid; place-items: center; color: #fff; font-size: 18px;
      box-shadow: 0 8px 18px -6px rgba(2, 132, 199, 0.55);
    }
    .wm-container { max-width: 1280px; margin: 0 auto; padding: 24px 20px 48px; }
    .wm-card {
      background: var(--wm-surface);
      border: 1px solid var(--wm-border);
      border-radius: 20px;
      padding: 20px;
      box-shadow: var(--wm-shadow);
    }
    .wm-pill {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 700;
    }
    .wm-pill.aqua { background: var(--wm-aqua-soft); color: #0369A1; }
    .wm-pill.mint { background: var(--wm-mint-soft); color: #047857; }
    .wm-pill.melon { background: var(--wm-melon-soft); color: #BE123C; }
    .wm-pill.amber { background: var(--wm-amber-soft); color: #B45309; }
    .wm-btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      padding: 10px 16px; border-radius: 13px; border: 1px solid var(--wm-border);
      background: #fff; color: var(--wm-text); font-size: 13px; font-weight: 700;
      cursor: pointer; text-decoration: none; transition: border-color 0.15s, background 0.15s;
    }
    .wm-btn:hover { border-color: #BAE6FD; background: #F8FBFF; }
    .wm-btn.primary {
      background: linear-gradient(135deg, #0284C7, #0EA5E9);
      color: #fff; border: none;
      box-shadow: 0 10px 20px -8px rgba(2, 132, 199, 0.55);
    }
    .wm-btn.mint {
      background: linear-gradient(135deg, #059669, #10B981);
      color: #fff; border: none;
      box-shadow: 0 10px 20px -8px rgba(16, 185, 129, 0.45);
    }
    .wm-btn.melon {
      background: linear-gradient(135deg, #E11D48, #F43F5E);
      color: #fff; border: none;
      box-shadow: 0 10px 20px -8px rgba(244, 63, 94, 0.45);
    }
    .wm-input, .wm-select, .wm-textarea {
      width: 100%; background: var(--wm-surface-soft);
      border: 1.5px solid var(--wm-border); color: var(--wm-text);
      padding: 10px 13px; border-radius: 12px; font-size: 13.5px; font-weight: 500;
      outline: none; transition: border-color 0.15s, box-shadow 0.15s;
    }
    .wm-input:focus, .wm-select:focus, .wm-textarea:focus {
      border-color: var(--wm-aqua-bright); background: #fff;
      box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.12);
    }
    .wm-label { display: block; font-size: 12px; font-weight: 700; color: var(--wm-muted); margin-bottom: 6px; }
    .wm-grid-hero { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 22px; align-items: stretch; }
    .wm-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
    .wm-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .wm-grid-main { display: grid; grid-template-columns: 390px 1fr; gap: 22px; align-items: start; }
    @media (max-width: 1024px) {
      .wm-grid-hero, .wm-grid-main { grid-template-columns: 1fr; }
      .wm-grid-4 { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 640px) {
      .wm-grid-3, .wm-grid-4 { grid-template-columns: 1fr; }
    }
    .wm-map { height: 310px; border-radius: 16px; border: 1px solid var(--wm-border); overflow: hidden; background: #E8F1F8; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { text-align: left; padding: 10px 8px; color: var(--wm-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid var(--wm-border); }
    td { padding: 11px 8px; border-bottom: 1px solid #EEF4FA; }
  </style>
</head>
<body>
  <div id="root" style="padding:28px;font-family:'Plus Jakarta Sans',sans-serif;color:#52647A;">
    Loading JalSetu...
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
    // ERROR BOUNDARY (Prevents blank white screen on any runtime edge-case)
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
    // HOOKE'S-LAW SPRING ENGINE (Zero external spring dependency)
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
      const tension = config.tension || 260;
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
        from: spec.from || { opacity: 0, y: 10 },
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
    // WATERMELON UI PRIMITIVES
    // -----------------------------------------------------------------------
    function SpringCard({ children, style = {}, delay = 0, hoverLift = false, onClick }) {
      const [hovered, setHovered] = useState(false);
      const [pressed, setPressed] = useState(false);

      const enter = useSpring({
        from: { opacity: 0, y: 16 },
        to: { opacity: 1, y: 0 },
        delay,
        config: { tension: 260, friction: 24 },
      });

      const interact = useSpring({
        scale: pressed ? 0.985 : (hoverLift && hovered ? 1.015 : 1),
        y: hoverLift && hovered ? -3 : 0,
        boxShadow: hoverLift && hovered
          ? '0 18px 38px -12px rgba(2, 132, 199, 0.18)'
          : '0 12px 32px -12px rgba(15, 23, 42, 0.08)',
        config: { tension: 340, friction: 22 },
      });

      const ey = enter.y.get();
      const iy = interact.y.get();
      const sc = interact.scale.get();
      const isSettled = Math.abs(ey) < 0.02 && Math.abs(iy) < 0.02 && Math.abs(sc - 1) < 0.001;

      return (
        <animated.div
          className="wm-card"
          onClick={onClick}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => { setHovered(false); setPressed(false); }}
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          style={{
            ...style,
            opacity: enter.opacity,
            transform: isSettled ? 'none' : `translate3d(0, ${ey + iy}px, 0) scale(${sc})`,
            boxShadow: interact.boxShadow,
            cursor: onClick ? 'pointer' : style.cursor,
          }}
        >
          {children}
        </animated.div>
      );
    }

    function SpringButton({ children, variant = '', onClick, style = {}, type = 'button' }) {
      const [pressed, setPressed] = useState(false);
      const spring = useSpring({
        scale: pressed ? 0.96 : 1,
        config: { tension: 420, friction: 20 },
      });
      return (
        <animated.button
          type={type}
          className={`wm-btn ${variant}`}
          onClick={onClick}
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          onMouseLeave={() => setPressed(false)}
          style={{ ...style, transform: spring.scale.to((s) => `scale(${s})`) }}
        >
          {children}
        </animated.button>
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
        <animated.span>
          {spring.val.to((v) => `${Math.round(v).toLocaleString('en-IN')}${suffix}`)}
        </animated.span>
      );
    }

    function StatusBadge({ status }) {
      const s = String(status || '').toUpperCase();
      if (['RED', 'OPEN', 'FLAGGED', 'BOREWELL_DRY'].includes(s)) {
        return <span className="wm-pill melon">● {s.replace('_', ' ')}</span>;
      }
      if (['YELLOW', 'DISPATCHED', 'UNLOADED', 'PENDING_DISPATCH', 'LOW_PRESSURE'].includes(s)) {
        return <span className="wm-pill amber">● {s.replace('_', ' ')}</span>;
      }
      return <span className="wm-pill mint">● {s || 'HEALTHY'}</span>;
    }

    function NagpurMap({ center = [21.125, 79.025], zoom = 11, renderLayers, deps = [] }) {
      const divRef = useRef(null);
      const mapRef = useRef(null);
      const layerRef = useRef(null);

      useEffect(() => {
        if (!divRef.current) return;
        if (typeof L === 'undefined') {
          divRef.current.innerHTML =
            '<div style="height:100%;display:grid;place-items:center;padding:16px;text-align:center;color:#52647A;font-size:13px;">Interactive map tiles unavailable offline — telemetry and dispatch lists remain active below.</div>';
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
              divRef.current.style.backgroundImage = 'radial-gradient(#CBD5E1 1.2px, transparent 1.2px)';
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
        { title: 'Daily Water Check-In', desc: 'Report normal supply, low pressure, or dry borewell in 1 tap.', role: 'citizen', icon: '💧', accent: '#0284C7' },
        { title: 'Track Live Tanker', desc: 'See incoming tanker route from depot & confirm delivery.', role: 'citizen', icon: '🗺️', accent: '#10B981' },
        { title: 'Report Leak / Pump Fault', desc: 'Log leaking valves or pump breakdowns directly to utility desk.', role: 'citizen', icon: '🔧', accent: '#F43F5E' },
        { title: '14-Taluka RWH Calculator', desc: 'Estimate roof runoff, first-flush & recharge in EN / हिं / म.', role: 'citizen', icon: '🌦️', accent: '#F59E0B' },
      ];

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">💧</div>
              <div>
                <div>JalSetu</div>
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--wm-muted)' }}>Community Groundwater, Tanker & Recharge Intelligence</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <SpringButton onClick={() => chooseRole('citizen', true)}>Citizen Login</SpringButton>
              <SpringButton onClick={() => chooseRole('verifier', true)}>Field Verifier</SpringButton>
              <SpringButton variant="primary" onClick={() => chooseRole('utility', true)}>Utility & Tanker Ops</SpringButton>
            </div>
          </nav>

          <div className="wm-container">
            <div className="wm-grid-hero" style={{ marginBottom: '26px' }}>
              <SpringCard style={{ background: 'linear-gradient(145deg, #FFFFFF 0%, #F0F9FF 100%)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '14px' }}>
                    <span className="wm-pill aqua">Nagpur District · 91 Locations</span>
                    <span className="wm-pill mint">Zero-Hardware Calibration + Live 48h Rain</span>
                  </div>
                  <h1 style={{ fontSize: '32px', fontWeight: 800, lineHeight: 1.18, letterSpacing: '-0.03em', marginBottom: '12px', color: '#0F172A' }}>
                    Real-Time Water Scarcity, Tanker Tracking & Rainwater Recharge
                  </h1>
                  <p style={{ fontSize: '14.5px', lineHeight: 1.6, color: 'var(--wm-muted)', marginBottom: '20px' }}>
                    Connecting residents, field verifiers, and tanker dispatchers on one live workflow—calibrating local borewells against CGWB telemetry, verifying scarcity with 48-hour rainfall, and tracking every tanker drop.
                  </p>
                </div>

                <div style={{ background: '#fff', border: '1px solid var(--wm-border)', borderRadius: '16px', padding: '14px' }}>
                  <svg viewBox="0 0 540 135" style={{ width: '100%', height: '125px', display: 'block' }}>
                    <defs>
                      <linearGradient id="skyGrad" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#E0F2FE" />
                        <stop offset="50%" stopColor="#F0FDF4" />
                        <stop offset="100%" stopColor="#FFE4E6" />
                      </linearGradient>
                    </defs>
                    <rect x="0" y="0" width="540" height="135" rx="12" fill="url(#skyGrad)" />
                    <path d="M 55 95 C 160 35, 290 115, 465 55" fill="none" stroke="#0284C7" strokeWidth="4" strokeDasharray="8 6" strokeLinecap="round" />
                    <circle cx="55" cy="95" r="18" fill="#0284C7" />
                    <text x="55" y="100" textAnchor="middle" fill="#fff" fontSize="14">🚛</text>
                    <text x="55" y="125" textAnchor="middle" fill="#0F172A" fontSize="10" fontWeight="700">Tanker Depot</text>
                    <circle cx="260" cy="76" r="18" fill="#10B981" />
                    <text x="260" y="81" textAnchor="middle" fill="#fff" fontSize="14">📡</text>
                    <text x="260" y="108" textAnchor="middle" fill="#0F172A" fontSize="10" fontWeight="700">CGWB + Rain Check</text>
                    <circle cx="465" cy="55" r="18" fill="#F43F5E" />
                    <text x="465" y="60" textAnchor="middle" fill="#fff" fontSize="14">🏘️</text>
                    <text x="465" y="87" textAnchor="middle" fill="#0F172A" fontSize="10" fontWeight="700">Colony Delivery</text>
                  </svg>
                </div>
              </SpringCard>

              <div ref={loginBoxRef}>
                <SpringCard delay={80} style={{ height: '100%' }}>
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
                          borderRadius: '12px',
                          border: role === t.id ? '2px solid #0284C7' : '1px solid var(--wm-border)',
                          background: role === t.id ? '#E0F2FE' : '#F8FBFF',
                          color: role === t.id ? '#0369A1' : 'var(--wm-muted)',
                          fontWeight: 800,
                          fontSize: '12.5px',
                          cursor: 'pointer',
                        }}
                      >
                        {t.label}
                      </button>
                    ))}
                  </div>

                  <div style={{ background: '#F8FBFF', border: '1px solid var(--wm-border)', borderRadius: '12px', padding: '10px 12px', fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5, marginBottom: '14px' }}>
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
                    <div style={{ background: 'var(--wm-melon-soft)', color: '#BE123C', padding: '8px 12px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, marginBottom: '10px' }}>
                      {err}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <SpringButton variant="primary" style={{ flex: 1 }} onClick={() => handleAuth('/api/login')}>
                      Enter {BOOT.role_defaults[role].title} →
                    </SpringButton>
                    <SpringButton onClick={() => handleAuth('/api/register')}>
                      Register
                    </SpringButton>
                  </div>
                </SpringCard>
              </div>
            </div>

            <div className="wm-grid-3" style={{ marginBottom: '26px' }}>
              {kpis.map((k, idx) => (
                <SpringCard key={k.label} delay={idx * 45} hoverLift style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '16px 18px' }}>
                  <div style={{
                    width: '46px', height: '46px', borderRadius: '14px', flexShrink: 0,
                    background: `var(--wm-${k.tone}-soft)`, display: 'grid', placeItems: 'center', fontSize: '21px'
                  }}>
                    {k.icon}
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--wm-muted)' }}>{k.label}</div>
                    <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--wm-text)', lineHeight: 1.15 }}>
                      <AnimatedNumber value={k.val} suffix={k.suffix || ''} />
                    </div>
                    <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)', marginTop: '2px' }}>{k.sub}</div>
                  </div>
                </SpringCard>
              ))}
            </div>

            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Citizen Quick Actions</h2>
              <span style={{ fontSize: '12px', color: 'var(--wm-muted)', fontWeight: 600 }}>Click any action to jump into Citizen Portal</span>
            </div>
            <div className="wm-grid-4">
              {quickActions.map((qa, idx) => (
                <SpringCard
                  key={qa.title}
                  delay={120 + idx * 50}
                  hoverLift
                  onClick={() => chooseRole(qa.role, true)}
                  style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
                >
                  <div>
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '12px', marginBottom: '12px',
                      background: '#F0F9FF', display: 'grid', placeItems: 'center', fontSize: '20px'
                    }}>
                      {qa.icon}
                    </div>
                    <div style={{ fontSize: '15px', fontWeight: 800, marginBottom: '6px' }}>{qa.title}</div>
                    <p style={{ fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5 }}>{qa.desc}</p>
                  </div>
                  <div style={{ marginTop: '14px', fontSize: '12px', fontWeight: 800, color: qa.accent }}>
                    Open Action →
                  </div>
                </SpringCard>
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
        from: { opacity: 0, y: 10 },
        enter: { opacity: 1, y: 0 },
        leave: { opacity: 0, y: -8 },
        config: { tension: 300, friction: 26 },
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
              {ev && <span className="wm-pill aqua">48h Rain: {ev.raw_stage1.rain_48h_mm} mm</span>}
              <a className="wm-btn" href="/login?role=verifier">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          {toast && (
            <div style={{ position: 'fixed', bottom: '22px', right: '22px', zIndex: 60, background: '#0F172A', color: '#fff', padding: '12px 18px', borderRadius: '14px', fontSize: '13px', fontWeight: 700, boxShadow: '0 14px 30px rgba(15,23,42,0.25)' }}>
              ✓ {toast}
            </div>
          )}

          <div className="wm-container">
            <div className="wm-grid-main">
              <div>
                <SpringCard style={{ marginBottom: '18px' }}>
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
                </SpringCard>

                {ev && (
                  <SpringCard delay={70}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--wm-muted)' }}>COLONY SUPPLY HEALTH</span>
                      <StatusBadge status={ev.scarcity_status} />
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: 800, marginBottom: '6px' }}>{data.layout.name}</div>
                    <p style={{ fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5, marginBottom: '14px' }}>{ev.diagnosis}</p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div style={{ background: 'var(--wm-surface-soft)', padding: '11px', borderRadius: '12px', border: '1px solid var(--wm-border)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>PUMP RUNWAY</div>
                        <div style={{ fontSize: '19px', fontWeight: 800, color: ev.groundwater_summary.pump_runway.days !== null && ev.groundwater_summary.pump_runway.days <= 20 ? '#E11D48' : '#0284C7' }}>
                          {ev.groundwater_summary.pump_runway.days !== null ? `${ev.groundwater_summary.pump_runway.days} days` : 'Stable'}
                        </div>
                      </div>
                      <div style={{ background: 'var(--wm-surface-soft)', padding: '11px', borderRadius: '12px', border: '1px solid var(--wm-border)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>DRY HOMES</div>
                        <div style={{ fontSize: '19px', fontWeight: 800 }}>
                          {ev.signals.signal_3_community_shortage.dry_percentage}%
                        </div>
                      </div>
                    </div>
                  </SpringCard>
                )}
              </div>

              <div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                  {[
                    { id: 'checkin', label: '1. Daily Water Check-In' },
                    { id: 'tanker', label: `2. Live Tanker Tracker (${data?.tanker_orders?.length || 0})` },
                    { id: 'leak', label: `3. Report Leak (${data?.tickets?.length || 0})` },
                    { id: 'rwh', label: '4. Rainwater Harvesting (14 Talukas)' },
                  ].map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setTab(t.id)}
                      style={{
                        padding: '10px 15px',
                        borderRadius: '999px',
                        border: tab === t.id ? 'none' : '1px solid var(--wm-border)',
                        background: tab === t.id ? 'linear-gradient(135deg, #0284C7, #0EA5E9)' : '#fff',
                        color: tab === t.id ? '#fff' : 'var(--wm-text)',
                        fontSize: '13px',
                        fontWeight: 700,
                        cursor: 'pointer',
                        boxShadow: tab === t.id ? '0 8px 18px -6px rgba(2,132,199,0.5)' : 'none',
                      }}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {tabTransition((style, activeTab) => (
                  <animated.div style={style}>
                    {activeTab === 'checkin' && (
                      <SpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '6px' }}>How is your tap / borewell water supply today?</h2>
                        <p style={{ fontSize: '13px', color: 'var(--wm-muted)', marginBottom: '16px' }}>
                          Your 1-tap check-in updates colony scarcity signals in real time for verifiers and tanker dispatchers.
                        </p>

                        <div style={{ maxWidth: '280px', marginBottom: '14px' }}>
                          <label className="wm-label">Your Flat / Plot / House No.</label>
                          <input className="wm-input" value={unit} onChange={(e) => setUnit(e.target.value)} />
                        </div>

                        <div className="wm-grid-3" style={{ marginBottom: '18px' }}>
                          <SpringButton variant="mint" style={{ padding: '14px' }} onClick={() => sendCheckin('NORMAL')}>
                            🟢 Normal Supply
                          </SpringButton>
                          <SpringButton style={{ padding: '14px', borderColor: '#F59E0B', color: '#B45309', background: '#FFFBEB' }} onClick={() => sendCheckin('LOW_PRESSURE')}>
                            🟡 Low Pressure
                          </SpringButton>
                          <SpringButton variant="melon" style={{ padding: '14px' }} onClick={() => sendCheckin('BOREWELL_DRY')}>
                            🔴 Borewell Dry
                          </SpringButton>
                        </div>

                        <div style={{ background: 'var(--wm-surface-soft)', padding: '14px', borderRadius: '14px', border: '1px solid var(--wm-border)', marginBottom: '16px' }}>
                          <div style={{ fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>Live Colony Household Breakdown</div>
                          <div style={{ height: '12px', borderRadius: '999px', overflow: 'hidden', display: 'flex', background: '#E2E8F0', marginBottom: '8px' }}>
                            <div style={{ width: `${((counts.NORMAL || 0) / totalHomes) * 100}%`, background: '#10B981' }} />
                            <div style={{ width: `${((counts.LOW_PRESSURE || 0) / totalHomes) * 100}%`, background: '#F59E0B' }} />
                            <div style={{ width: `${((counts.BOREWELL_DRY || 0) / totalHomes) * 100}%`, background: '#F43F5E' }} />
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
                                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '9px 12px', borderRadius: '11px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', fontSize: '12.5px' }}>
                                  <span><b>{log.unit}</b> · {log.by} <span style={{ color: 'var(--wm-muted)' }}>({log.time})</span></span>
                                  <StatusBadge status={log.status} />
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </SpringCard>
                    )}

                    {activeTab === 'tanker' && data && (
                      <SpringCard>
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
                            <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', padding: '12px 14px', borderRadius: '14px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)' }}>
                              <div>
                                <div style={{ fontWeight: 800, fontSize: '14px' }}>{o.id} · {o.volume_l.toLocaleString()} L ({o.vehicle_no || 'Awaiting Truck'})</div>
                                <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>From {o.depot_name || 'Pending Depot'} · {o.distance_km || '--'} km</div>
                              </div>
                              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                <StatusBadge status={o.status} />
                                {(o.status === 'DISPATCHED' || o.status === 'UNLOADED') && (
                                  <SpringButton variant="mint" onClick={() => confirmTanker(o.id)}>✓ Confirm Water Received</SpringButton>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </SpringCard>
                    )}

                    {activeTab === 'leak' && (
                      <SpringCard>
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
                        <SpringButton variant="primary" onClick={submitTicket}>Submit Ticket to Utility Desk</SpringButton>

                        <h3 style={{ fontSize: '14px', fontWeight: 800, marginTop: '20px', marginBottom: '10px' }}>Colony Tickets</h3>
                        <div style={{ display: 'grid', gap: '8px' }}>
                          {(data?.tickets || []).length === 0 && (
                            <div style={{ fontSize: '13px', color: 'var(--wm-muted)' }}>No leak or pump tickets logged in this colony yet.</div>
                          )}
                          {(data?.tickets || []).map((t) => (
                            <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '11px 14px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)' }}>
                              <div>
                                <div style={{ fontWeight: 700, fontSize: '13px' }}>#{t.id} · {t.issue_type} ({t.severity})</div>
                                <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>{t.description} · {t.created_at}</div>
                              </div>
                              <StatusBadge status={t.status} />
                            </div>
                          ))}
                        </div>
                      </SpringCard>
                    )}

                    {activeTab === 'rwh' && (
                      <SpringCard>
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
                              <div style={{ fontSize: '11px', fontWeight: 700, color: '#0369A1' }}>GROSS CAPTURED</div>
                              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A' }}>{rwhOut.gross_l.toLocaleString('en-IN')} L</div>
                            </div>
                            <div style={{ background: 'var(--wm-amber-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: '#B45309' }}>FIRST-FLUSH DIVERTED</div>
                              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A' }}>{rwhOut.first_flush_l.toLocaleString('en-IN')} L</div>
                            </div>
                            <div style={{ background: 'var(--wm-mint-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: '#047857' }}>NET EFFECTIVE HARVEST</div>
                              <div style={{ fontSize: '20px', fontWeight: 800, color: '#047857' }}>{rwhOut.net_l.toLocaleString('en-IN')} L</div>
                            </div>
                          </div>
                        )}

                        <div style={{ fontSize: '13px', fontWeight: 800, marginBottom: '8px' }}>Monsoon Readiness Checklist</div>
                        {(RWH_RULES[rwhLang] || RWH_RULES.en).map((rule, idx) => {
                          const key = `r_${idx}`;
                          const checked = !!(data?.rwh_checks || {})[key];
                          return (
                            <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 10px', borderRadius: '10px', background: 'var(--wm-surface-soft)', marginBottom: '6px', cursor: 'pointer', fontSize: '13px' }}>
                              <input type="checkbox" checked={checked} onChange={(e) => toggleRwh(key, e.target.checked)} />
                              <span>{rule}</span>
                            </label>
                          );
                        })}
                      </SpringCard>
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
          <svg viewBox="0 0 600 195" style={{ width: '100%', height: '195px', background: 'var(--wm-surface-soft)', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
            <line x1={padL} y1={padT} x2={w - padR} y2={padT} stroke="#E2ECF5" strokeDasharray="4 4" />
            <line x1={padL} y1={(padT + h - padB) / 2} x2={w - padR} y2={(padT + h - padB) / 2} stroke="#E2ECF5" strokeDasharray="4 4" />
            <line x1={padL} y1={h - padB} x2={w - padR} y2={h - padB} stroke="#E2ECF5" />
            <text x="8" y={padT + 4} fill="#52647A" fontSize="10" fontWeight="700">{minD}m</text>
            <text x="8" y={(padT + h - padB) / 2 + 4} fill="#52647A" fontSize="10" fontWeight="700">{midD}m</text>
            <text x="8" y={h - padB} fill="#52647A" fontSize="10" fontWeight="700">{maxD}m</text>
            <text x={padL} y={h - 8} fill="#52647A" fontSize="10" fontWeight="600">7 Days Ago</text>
            <text x={w - padR - 32} y={h - 8} fill="#52647A" fontSize="10" fontWeight="600">Now</text>
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
              {ev && <span className="wm-pill mint">48h Rain: {ev.raw_stage1.rain_48h_mm} mm</span>}
              <a className="wm-btn" href="/login?role=utility">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          {toast && (
            <div style={{ position: 'fixed', bottom: '22px', right: '22px', zIndex: 60, background: '#0F172A', color: '#fff', padding: '12px 18px', borderRadius: '14px', fontSize: '13px', fontWeight: 700 }}>
              ✓ {toast}
            </div>
          )}

          <div className="wm-container">
            <div className="wm-grid-main">
              <div>
                <SpringCard style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>1. Assigned Colony / Ward</h3>
                  <input className="wm-input" style={{ marginBottom: '8px' }} placeholder="Search 91 locations..." value={query} onChange={(e) => setQuery(e.target.value)} />
                  <select className="wm-select" value={layoutId} onChange={(e) => setLayoutId(e.target.value)}>
                    {list.map((l) => <option key={l.id} value={l.id}>{l.category === 'Featured Pilot' ? '★ ' : ''}{l.name}</option>)}
                  </select>
                </SpringCard>

                <SpringCard delay={60} style={{ marginBottom: '16px' }}>
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
                      padding: '9px 11px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, marginBottom: '10px',
                      background: ev.groundwater_summary.verifier_validation.status === 'VERIFIED' ? 'var(--wm-mint-soft)' : 'var(--wm-melon-soft)',
                      color: ev.groundwater_summary.verifier_validation.status === 'VERIFIED' ? '#047857' : '#BE123C',
                    }}>
                      {ev.groundwater_summary.verifier_validation.status}: {ev.groundwater_summary.verifier_validation.reason}
                    </div>
                  )}
                  <SpringButton variant="primary" style={{ width: '100%' }} onClick={saveReading}>Verify & Update Calibration</SpringButton>
                </SpringCard>

                <SpringCard delay={110}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '6px' }}>3. Verified Tanker Indent (55 LPCD)</h3>
                  {data && (
                    <div style={{ fontSize: '12px', color: '#0369A1', background: 'var(--wm-aqua-soft)', padding: '9px 11px', borderRadius: '10px', marginBottom: '10px', fontWeight: 600 }}>
                      Recommended: {data.recommended_tanker.litres_per_day.toLocaleString()} L/day ({data.recommended_tanker.trips_10k} trips) for {data.recommended_tanker.affected_homes} homes.
                    </div>
                  )}
                  <select className="wm-select" style={{ marginBottom: '10px' }} value={indentVol} onChange={(e) => setIndentVol(e.target.value)}>
                    <option value="10000">10,000 L (1 Tanker Trip)</option>
                    <option value="20000">20,000 L (2 Tanker Trips)</option>
                    <option value="30000">30,000 L (3 Tanker Trips)</option>
                  </select>
                  <SpringButton variant="mint" style={{ width: '100%' }} onClick={raiseIndent}>Send Verified Indent to Utility</SpringButton>
                </SpringCard>
              </div>

              <div>
                {ev && (
                  <>
                    <SpringCard style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <h2 style={{ fontSize: '18px', fontWeight: 800 }}>{data.layout.name}</h2>
                        <StatusBadge status={ev.scarcity_status} />
                      </div>
                      <p style={{ fontSize: '13px', color: 'var(--wm-muted)', marginBottom: '14px' }}>{ev.diagnosis}</p>

                      <div className="wm-grid-3">
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>LIVE CALIBRATED DEPTH</div>
                          <div style={{ fontSize: '21px', fontWeight: 800 }}>{ev.groundwater_summary.live_calibrated_depth_m} m</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Offset {ev.raw_stage1.local_offset_m >= 0 ? '+' : ''}{ev.raw_stage1.local_offset_m}m vs CGWB</div>
                        </div>
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>DEPLETION VELOCITY</div>
                          <div style={{ fontSize: '21px', fontWeight: 800 }}>{ev.raw_stage1.depletion_velocity_m_per_week} m/wk</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Deficit: {ev.signals.signal_1_aquifer_stress.deficit_m} m</div>
                        </div>
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>PUMP RUNWAY</div>
                          <div style={{ fontSize: '21px', fontWeight: 800 }}>{ev.groundwater_summary.pump_runway.days !== null ? `${ev.groundwater_summary.pump_runway.days} d` : 'Stable'}</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>{ev.groundwater_summary.pump_runway.label}</div>
                        </div>
                      </div>
                    </SpringCard>

                    <SpringCard delay={80} style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                        <h3 style={{ fontSize: '15px', fontWeight: 800 }}>7-Day 6-Hourly Calibrated Hydrograph</h3>
                        <span className="wm-pill aqua">CGWB: {ev.groundwater_summary.matched_gov_station} ({ev.groundwater_summary.station_distance_km} km)</span>
                      </div>
                      {renderHydrograph()}
                      <div style={{ display: 'flex', justifyContent: 'center', gap: '18px', fontSize: '11.5px', color: 'var(--wm-muted)', marginTop: '8px', fontWeight: 700 }}>
                        <span style={{ color: '#0284C7' }}>━━ Raw CGWB 6-Hourly Sensor</span>
                        <span style={{ color: '#F43F5E' }}>━━ Offset-Calibrated Colony Depth</span>
                      </div>
                    </SpringCard>

                    <SpringCard delay={120}>
                      <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>3-Signal Scarcity & Fault Breakdown</h3>
                      {[
                        { title: 'Signal 1: Aquifer Stress (>2.5m Deficit or ≤1.5m Col)', active: ev.signals.signal_1_aquifer_stress.active, val: `Deficit: ${ev.signals.signal_1_aquifer_stress.deficit_m} m` },
                        { title: 'Signal 2: Rapid Depletion (>0.5m/week)', active: ev.signals.signal_2_rapid_depletion.active, val: `Rate: ${ev.signals.signal_2_rapid_depletion.velocity_m_per_week} m/wk` },
                        { title: 'Signal 3: Resident Shortage (≥30% Dry Homes)', active: ev.signals.signal_3_community_shortage.active, val: `Dry: ${ev.signals.signal_3_community_shortage.dry_percentage}%` },
                      ].map((s) => (
                        <div key={s.title} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px', fontSize: '13px' }}>
                          <span style={{ fontWeight: 700 }}>{s.active ? '⚠️' : '✓'} {s.title}</span>
                          <StatusBadge status={s.active ? 'RED' : 'GREEN'} />
                        </div>
                      ))}
                    </SpringCard>
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
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <a className="wm-btn" href="/login?role=citizen">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          {toast && (
            <div style={{ position: 'fixed', bottom: '22px', right: '22px', zIndex: 60, background: '#0F172A', color: '#fff', padding: '12px 18px', borderRadius: '14px', fontSize: '13px', fontWeight: 700 }}>
              ✓ {toast}
            </div>
          )}

          {ov && (
            <div className="wm-container">
              <div className="wm-grid-main">
                <div>
                  <SpringCard style={{ marginBottom: '16px' }}>
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
                      <div style={{ background: 'var(--wm-amber-soft)', color: '#B45309', padding: '8px 11px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>
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

                    <SpringButton variant="primary" style={{ width: '100%' }} onClick={dispatchNow}>Assign & Dispatch Tanker</SpringButton>
                  </SpringCard>

                  <SpringCard delay={60} style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>2. Tanker Depots & Fleet Stock</h3>
                    {ov.depots.map((d) => (
                      <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13px' }}>{d.name}</div>
                          <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)' }}>Stock: {d.current_stock_l.toLocaleString()} / {d.max_capacity_l.toLocaleString()} L · Trucks: {d.trucks_ready}/{d.trucks_total}</div>
                        </div>
                        <SpringButton onClick={() => refillDepot(d.id)}>+ Refill</SpringButton>
                      </div>
                    ))}
                  </SpringCard>

                  <SpringCard delay={110}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>3. Surface Leak & Valve Maintenance Queue</h3>
                    {ov.tickets.map((t) => (
                      <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '12.5px' }}>#{t.id} · {t.issue_type} @ {t.layout_name}</div>
                          <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)' }}>{t.description}</div>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <StatusBadge status={t.status} />
                          {t.status !== 'RESOLVED' && <SpringButton variant="mint" onClick={() => resolveTicket(t.id)}>Resolve</SpringButton>}
                        </div>
                      </div>
                    ))}
                  </SpringCard>
                </div>

                <div>
                  <SpringCard style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <h3 style={{ fontSize: '16px', fontWeight: 800 }}>4. Nagpur Scarcity & Live Tanker Route Map</h3>
                      <span className="wm-pill aqua">Live Fleet & Colony Stress</span>
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
                  </SpringCard>

                  <SpringCard delay={70} style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>5. Verified Tanker Indents & Active Deliveries</h3>
                    {ov.tanker_orders.map((o) => (
                      <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', padding: '11px 13px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13.5px' }}>{o.id} · {o.layout_name} ({o.volume_l.toLocaleString()} L)</div>
                          <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>Verified by {o.verified_by} · {o.vehicle_no || 'Pending Truck'} ({o.depot_name || 'Unassigned'})</div>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <StatusBadge status={o.status} />
                          {o.status === 'PENDING_DISPATCH' && <SpringButton variant="primary" onClick={() => dispatchExisting(o.id)}>Dispatch</SpringButton>}
                          {o.status === 'DISPATCHED' && <SpringButton variant="mint" onClick={() => markUnloaded(o.id)}>Mark Unloaded</SpringButton>}
                        </div>
                      </div>
                    ))}
                  </SpringCard>

                  <SpringCard delay={120}>
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
                              <td>{e.groundwater_summary.live_calibrated_depth_m} m</td>
                              <td>{e.groundwater_summary.pump_runway.days ?? 'Stable'} d</td>
                              <td>{e.signals.signal_3_community_shortage.dry_percentage}%</td>
                              <td>{e.raw_stage1.rain_48h_mm} mm</td>
                              <td><StatusBadge status={e.scarcity_status} /></td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </SpringCard>
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
            self._send_html(build_react_page("JalSetu  —  UI Network", "login", boot))
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
            self._send_html(build_react_page("Citizen Portal — JalSetu", "citizen", boot))
            return

        if url.path == "/verifier":
            if not sess or sess["role"] != "verifier":
                self._redirect("/login?role=verifier")
                return
            boot = json.dumps({
                "user_name": sess["name"],
                "layouts": backend.ALL_LAYOUTS,
            })
            self._send_html(build_react_page("Field Verifier Portal — JalSetu", "verifier", boot))
            return

        if url.path == "/utility":
            if not sess or sess["role"] != "utility":
                self._redirect("/login?role=utility")
                return
            boot = json.dumps({"user_name": sess["name"]})
            self._send_html(build_react_page("Utility & Tanker Operations — JalSetu", "utility", boot))
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
    print(f" JalSetu — Watermelon UI + React Spring ({len(backend.ALL_LAYOUTS)} locations)")
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