import streamlit as st
import asyncio
import re
import os
import tempfile
from shazamio import Shazam
import yt_dlp
from urllib.parse import quote
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BeatSnatch",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════
STYLE = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ─── DESIGN TOKENS ─────────────────────────────────────────────────────── */
:root {
  --c-primary:   #00ffcc;
  --c-primary2:  #00c9a0;
  --c-blue:      #3b6cf8;
  --c-purple:    #7c3aed;
  --c-spotify:   #1DB954;
  --c-youtube:   #ff0000;
  --c-gold:      #fbbf24;
  --c-gold2:     #f59e0b;
  --c-danger:    #f87171;
  --c-success:   #34d399;
  --c-bg:        #080812;
  --c-bg2:       #0e0e1c;
  --c-surface:   rgba(255,255,255,0.04);
  --c-surface2:  rgba(255,255,255,0.07);
  --c-border:    rgba(255,255,255,0.08);
  --c-border2:   rgba(0,255,204,0.2);
  --c-text:      #f1f5f9;
  --c-text2:     #94a3b8;
  --c-text3:     #475569;
  --r-card:      20px;
  --r-btn:       100px;
  --blur:        backdrop-filter: blur(20px) saturate(180%);
  --t-fast:      0.18s ease;
  --t-med:       0.3s ease;
  --t-slow:      0.5s cubic-bezier(.16,1,.3,1);
}

/* ─── GLOBAL ──────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section[data-testid="stMain"],
.main, .block-container {
  background: var(--c-bg) !important;
  color: var(--c-text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* Deep mesh background */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,255,204,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 110%, rgba(59,108,248,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 100% 80% at 50% 50%, #0d0d20 0%, #080812 100%);
  pointer-events: none;
  z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarNav"],
.viewerBadge_container__1QSob,
[data-testid="manage-app-button"] { display: none !important; }

/* Streamlit container width */
[data-testid="block-container"] {
  max-width: 680px !important;
  width: 100% !important;
  margin: 0 auto !important;
  padding: clamp(1.2rem, 4vw, 2.8rem) clamp(1rem, 4vw, 1.8rem) clamp(2rem, 5vw, 4rem) !important;
}

/* ─── HEADER ──────────────────────────────────────────────────────────────── */
.bs-header {
  text-align: center;
  padding: clamp(0.5rem, 2vw, 1rem) 0 clamp(0.3rem, 1.5vw, 0.6rem);
}
.bs-logo-wrap {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}
.bs-logo-icon {
  width: clamp(36px, 6vw, 48px);
  height: clamp(36px, 6vw, 48px);
  background: linear-gradient(135deg, rgba(0,255,204,0.15), rgba(0,255,204,0.05));
  border: 1px solid rgba(0,255,204,0.3);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(18px, 3vw, 24px);
  box-shadow: 0 0 20px rgba(0,255,204,0.15);
  flex-shrink: 0;
}
.bs-title {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(1.9rem, 6.5vw, 3rem);
  font-weight: 900;
  color: var(--c-primary);
  letter-spacing: 0.04em;
  text-shadow:
    0 0 10px rgba(0,255,204,0.6),
    0 0 25px rgba(0,255,204,0.3),
    0 0 50px rgba(0,255,204,0.15);
  animation: flicker 3s infinite alternate;
  line-height: 1;
}
.bs-tagline {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(0.52rem, 1.5vw, 0.65rem);
  color: rgba(0,255,204,0.4);
  letter-spacing: 0.3em;
  text-transform: uppercase;
  margin-top: 4px;
}
.bs-badge-row {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
  flex-wrap: wrap;
}
.bs-badge {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 100px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: var(--c-text2);
}
.bs-badge.green { background: rgba(0,255,204,0.08); border-color: rgba(0,255,204,0.2); color: var(--c-primary); }

/* ─── DIVIDER ─────────────────────────────────────────────────────────────── */
.bs-divider {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,0.25), rgba(59,108,248,0.15), transparent);
  margin: clamp(0.8rem, 2vw, 1.4rem) 0;
}

/* ─── GLASS CARD BASE ─────────────────────────────────────────────────────── */
.bs-glass {
  background: rgba(255,255,255,0.035);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--r-card);
  position: relative;
  overflow: hidden;
}
.bs-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 60%);
  pointer-events: none;
}

/* ─── RECORD CARD ─────────────────────────────────────────────────────────── */
.bs-record-card {
  padding: clamp(1.2rem, 3.5vw, 1.8rem) clamp(1rem, 3.5vw, 1.8rem) clamp(1rem, 3vw, 1.5rem);
  border-color: rgba(0,255,204,0.12);
  margin-bottom: 0;
  box-shadow:
    0 1px 0 rgba(255,255,255,0.05) inset,
    0 20px 60px rgba(0,0,0,0.5),
    0 0 0 1px rgba(0,0,0,0.3);
}
.bs-record-card::after {
  content: '';
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 60%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,0.4), transparent);
}
.bs-record-hint {
  text-align: center;
  margin-bottom: clamp(0.8rem, 2vw, 1.1rem);
}
.bs-record-hint p {
  font-size: clamp(0.72rem, 2vw, 0.82rem);
  color: var(--c-text3);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 500;
}
.bs-step-row {
  display: flex;
  justify-content: center;
  gap: clamp(12px, 3vw, 24px);
  margin-top: 8px;
  flex-wrap: wrap;
}
.bs-step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: clamp(0.65rem, 1.8vw, 0.72rem);
  color: var(--c-text2);
  font-weight: 500;
}
.bs-step-num {
  width: 18px; height: 18px;
  border-radius: 50%;
  background: rgba(0,255,204,0.1);
  border: 1px solid rgba(0,255,204,0.25);
  color: var(--c-primary);
  font-size: 0.62rem;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* ─── AUDIO INPUT OVERRIDE ────────────────────────────────────────────────── */
[data-testid="stAudioInput"] {
  background: rgba(0,255,204,0.03) !important;
  border: 1px solid rgba(0,255,204,0.15) !important;
  border-radius: 14px !important;
  padding: 6px 8px !important;
}
[data-testid="stAudioInput"] label { display: none !important; }
[data-testid="stAudioInput"] button {
  background: radial-gradient(circle at center, #15152a, #0a0a17) !important;
  border: 2px solid rgba(0,255,204,0.3) !important;
  color: var(--c-primary) !important;
  border-radius: 50% !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 0 0 0 rgba(0,255,204,0) !important;
}
[data-testid="stAudioInput"] button:hover {
  border-color: var(--c-primary) !important;
  box-shadow: 0 0 0 8px rgba(0,255,204,0.08), 0 0 24px rgba(0,255,204,0.35) !important;
  transform: scale(1.08) !important;
}
[data-testid="stAudioInput"] > div > p {
  color: rgba(0,255,204,0.35) !important;
  font-size: 0.75rem !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stAudioInput"] audio,
[data-testid="stAudio"] audio { border-radius: 10px; width: 100%; }

/* ─── STREAMLIT NATIVE BUTTONS ────────────────────────────────────────────── */
/* Identify / Prepare – teal gradient */
[data-testid="stButton"] button {
  width: 100% !important;
  background: linear-gradient(135deg, #00d4a8 0%, #0099a8 100%) !important;
  color: #001a14 !important;
  font-weight: 700 !important;
  font-family: 'Inter', sans-serif !important;
  border: none !important;
  border-radius: var(--r-btn) !important;
  padding: clamp(0.6rem, 2vw, 0.75rem) clamp(1.2rem, 4vw, 2rem) !important;
  font-size: clamp(0.88rem, 2.2vw, 0.98rem) !important;
  letter-spacing: 0.04em !important;
  transition: all 0.3s ease !important;
  box-shadow:
    0 4px 20px rgba(0,212,168,0.3),
    0 1px 0 rgba(255,255,255,0.15) inset !important;
  text-transform: uppercase !important;
}
[data-testid="stButton"] button:hover {
  background: linear-gradient(135deg, #00ffcc 0%, #00b8d4 100%) !important;
  box-shadow: 0 8px 30px rgba(0,255,204,0.45) !important;
  transform: translateY(-2px) !important;
  color: #001a14 !important;
}
[data-testid="stButton"] button:active { transform: translateY(0) scale(0.98) !important; }

/* Download – gold */
[data-testid="stDownloadButton"] button {
  width: 100% !important;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
  color: #1a0e00 !important;
  font-weight: 700 !important;
  font-family: 'Inter', sans-serif !important;
  border: none !important;
  border-radius: var(--r-btn) !important;
  padding: clamp(0.6rem, 2vw, 0.75rem) clamp(1.2rem, 4vw, 2rem) !important;
  font-size: clamp(0.88rem, 2.2vw, 0.98rem) !important;
  letter-spacing: 0.04em !important;
  transition: all 0.3s ease !important;
  box-shadow:
    0 4px 20px rgba(251,191,36,0.35),
    0 1px 0 rgba(255,255,255,0.3) inset !important;
  text-transform: uppercase !important;
}
[data-testid="stDownloadButton"] button:hover {
  background: linear-gradient(135deg, #fcd34d 0%, #fbbf24 100%) !important;
  box-shadow: 0 8px 30px rgba(251,191,36,0.5) !important;
  transform: translateY(-2px) !important;
}

/* ─── STATUS MESSAGES ─────────────────────────────────────────────────────── */
.bs-status {
  text-align: center;
  font-size: clamp(0.82rem, 2.2vw, 0.92rem);
  color: var(--c-text2);
  padding: clamp(0.5rem, 1.5vw, 0.75rem) 0 0;
  letter-spacing: 0.02em;
}
.bs-status.primary { color: var(--c-primary); }
.bs-status.danger  { color: var(--c-danger); }
.bs-status.success { color: var(--c-success); }

/* ─── SONG CARD ───────────────────────────────────────────────────────────── */
.bs-song-card {
  padding: clamp(1.2rem, 4vw, 1.8rem);
  border-color: rgba(0,255,204,0.15);
  margin: clamp(0.8rem, 2vw, 1.2rem) 0;
  animation: slideUp 0.5s cubic-bezier(.16,1,.3,1) forwards;
  box-shadow:
    0 1px 0 rgba(255,255,255,0.05) inset,
    0 30px 80px rgba(0,0,0,0.6),
    0 0 60px rgba(0,255,204,0.04);
}
.bs-song-card::after {
  content: '';
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 40%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,0.5), transparent);
}

/* Inner layout: art + info */
.bs-song-inner {
  display: flex;
  gap: clamp(12px, 3vw, 20px);
  align-items: flex-start;
}
.bs-art {
  flex-shrink: 0;
  width: clamp(68px, 16vw, 90px);
  height: clamp(68px, 16vw, 90px);
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(0,255,204,0.08), rgba(59,108,248,0.12));
  border: 1px solid rgba(0,255,204,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.6rem, 4.5vw, 2.2rem);
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0,255,204,0.1);
}
.bs-art::before {
  content: '';
  position: absolute;
  inset: -50%;
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(0,255,204,0.15) 60deg,
    transparent 120deg,
    transparent 360deg
  );
  animation: artSpin 6s linear infinite;
}
.bs-art-inner {
  position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  width: 100%; height: 100%;
}
.bs-song-meta { flex: 1; min-width: 0; }
.bs-song-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: clamp(0.6rem, 1.6vw, 0.66rem);
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--c-primary);
  background: rgba(0,255,204,0.08);
  border: 1px solid rgba(0,255,204,0.2);
  border-radius: 100px;
  padding: 3px 10px;
  margin-bottom: 10px;
}
.bs-song-title {
  font-size: clamp(1rem, 3.5vw, 1.32rem);
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
  margin-bottom: 4px;
}
.bs-song-artist {
  font-size: clamp(0.78rem, 2.2vw, 0.9rem);
  color: var(--c-text2);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bs-song-divider {
  height: 1px;
  background: rgba(255,255,255,0.06);
  margin: clamp(0.9rem, 2.5vw, 1.2rem) 0;
}

/* Service link buttons */
.bs-btn-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(8px, 2vw, 12px);
}
@media (max-width: 380px) {
  .bs-btn-row { grid-template-columns: 1fr; }
}
.bs-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: clamp(5px, 1.5vw, 8px);
  font-weight: 600;
  padding: clamp(9px, 2.5vw, 12px) clamp(10px, 3vw, 16px);
  border-radius: var(--r-btn);
  text-decoration: none !important;
  transition: all 0.25s ease;
  font-size: clamp(0.78rem, 2.2vw, 0.87rem);
  cursor: pointer;
  border: none;
  font-family: 'Inter', sans-serif;
  letter-spacing: 0.02em;
  text-align: center;
}
.bs-btn-spotify {
  background: linear-gradient(135deg, #1DB954, #15a347);
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(29,185,84,0.3);
}
.bs-btn-spotify:hover {
  background: linear-gradient(135deg, #1ed760, #1DB954);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(29,185,84,0.45);
  color: #fff !important;
}
.bs-btn-youtube {
  background: linear-gradient(135deg, #ff0000, #cc0000);
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(255,0,0,0.3);
}
.bs-btn-youtube:hover {
  background: linear-gradient(135deg, #ff3333, #ff0000);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255,0,0,0.4);
  color: #fff !important;
}

/* ─── DOWNLOAD CARD ───────────────────────────────────────────────────────── */
.bs-dl-card {
  border-color: rgba(251,191,36,0.15);
  background: rgba(251,191,36,0.03);
  padding: clamp(1.2rem, 3.5vw, 1.6rem) clamp(1rem, 3.5vw, 1.8rem);
  margin-top: clamp(0.6rem, 2vw, 1rem);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.04) inset,
    0 20px 60px rgba(0,0,0,0.5),
    0 0 40px rgba(251,191,36,0.04);
  animation: slideUp 0.4s cubic-bezier(.16,1,.3,1) forwards;
}
.bs-dl-card::after {
  content: '';
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 30%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(251,191,36,0.5), transparent);
}
.bs-dl-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: clamp(0.9rem, 2.5vw, 1.2rem);
}
.bs-dl-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  background: rgba(251,191,36,0.1);
  border: 1px solid rgba(251,191,36,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}
.bs-dl-label {
  font-size: clamp(0.68rem, 1.8vw, 0.75rem);
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(251,191,36,0.7);
}
.bs-dl-desc {
  font-size: clamp(0.7rem, 1.8vw, 0.76rem);
  color: var(--c-text3);
  margin-top: 1px;
}
.bs-btn-gap { margin-top: clamp(8px, 2vw, 12px); }

/* ─── LOADER DOTS ─────────────────────────────────────────────────────────── */
.bs-loader {
  display: flex;
  gap: clamp(7px, 2vw, 10px);
  justify-content: center;
  padding: clamp(0.8rem, 2.5vw, 1.2rem) 0 clamp(0.4rem, 1.2vw, 0.6rem);
  align-items: center;
}
.bs-loader span {
  width: clamp(8px, 2vw, 10px);
  height: clamp(8px, 2vw, 10px);
  background: var(--c-primary);
  border-radius: 50%;
  animation: loaderBounce 1.4s infinite ease-in-out;
  box-shadow: 0 0 10px rgba(0,255,204,0.5);
}
.bs-loader span:nth-child(2) { animation-delay: 0.18s; background: rgba(0,255,204,0.7); }
.bs-loader span:nth-child(3) { animation-delay: 0.36s; background: rgba(0,255,204,0.5); }

/* ─── FOOTER ──────────────────────────────────────────────────────────────── */
.bs-footer {
  margin-top: clamp(2rem, 5vw, 3.5rem);
  padding-top: clamp(1rem, 2.5vw, 1.5rem);
  border-top: 1px solid rgba(255,255,255,0.05);
  text-align: center;
}
.bs-footer-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.bs-footer-name {
  font-size: clamp(0.72rem, 1.9vw, 0.8rem);
  color: var(--c-text3);
  font-weight: 500;
}
.bs-footer-name span { color: #ef4444; }
.bs-footer-link {
  font-size: clamp(0.68rem, 1.8vw, 0.75rem);
  color: rgba(0,255,204,0.4);
  text-decoration: none;
  transition: color 0.2s;
  font-weight: 500;
}
.bs-footer-link:hover { color: var(--c-primary); }
.bs-footer-copy {
  font-size: clamp(0.6rem, 1.6vw, 0.66rem);
  color: var(--c-text3);
  margin-top: 2px;
  opacity: 0.6;
}

/* ─── STREAMLIT SPINNER ───────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-top-color: var(--c-primary) !important; }
[data-testid="stSpinner"] p { color: var(--c-text2) !important; font-family: 'Inter', sans-serif !important; }

/* ─── STREAMLIT ALERT BOXES ───────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: 12px !important;
  background: rgba(248,113,113,0.08) !important;
  border: 1px solid rgba(248,113,113,0.2) !important;
  color: var(--c-danger) !important;
}

/* ─── KEYFRAMES ───────────────────────────────────────────────────────────── */
@keyframes flicker {
  0%,19%,21%,23%,25%,54%,56%,100% { opacity: 1; }
  20%,22%,24%,55% { opacity: 0.6; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(22px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes loaderBounce {
  0%,80%,100% { transform: scale(0.4); opacity: 0.3; }
  40%         { transform: scale(1);   opacity: 1; }
}
@keyframes artSpin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(0,255,204,0.25); }
  50%      { box-shadow: 0 0 0 12px rgba(0,255,204,0); }
}

/* ─── RESPONSIVE PATCHES ──────────────────────────────────────────────────── */
@media (max-width: 480px) {
  .bs-song-inner { flex-direction: column; align-items: center; text-align: center; }
  .bs-art { margin: 0 auto; }
  .bs-song-chip { margin: 0 auto 10px; }
  .bs-song-title, .bs-song-artist { white-space: normal; }
}
@media (min-width: 768px) {
  .bs-btn-row { gap: 14px; }
  .bs-btn { padding: 13px 20px; }
}
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
# VISUALIZER (full-width, multi-layer, responsive via ResizeObserver)
# ══════════════════════════════════════════════════════════════════════════════
VISUALIZER_HTML = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent !important; overflow: hidden; }
#wrap {
  width: 100%; height: 110px;
  position: relative; overflow: hidden;
  border-radius: 16px;
  background: linear-gradient(160deg, rgba(0,20,15,0.95) 0%, rgba(4,4,22,0.97) 100%);
  border: 1px solid rgba(0,255,204,0.1);
  box-shadow:
    0 0 30px rgba(0,255,153,0.12),
    0 0 60px rgba(0,51,200,0.1),
    inset 0 1px 0 rgba(255,255,255,0.05);
}
/* top glow line */
#wrap::before {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,0.5), rgba(59,108,248,0.3), transparent);
}
canvas { display: block; width: 100%; height: 100%; }
</style>
<div id="wrap"><canvas id="c"></canvas></div>
<script>
(function(){
  const wrap = document.getElementById('wrap');
  const c    = document.getElementById('c');
  const ctx  = c.getContext('2d');

  function resize() {
    c.width  = wrap.offsetWidth  || 640;
    c.height = wrap.offsetHeight || 110;
  }
  resize();
  new ResizeObserver(resize).observe(wrap);

  let t = 0;

  function drawWave(amp, freq, speed, phase, color, lineW, blur) {
    const W = c.width, H = c.height;
    ctx.beginPath();
    ctx.lineWidth   = lineW;
    ctx.strokeStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur  = blur;
    for (let i = 0; i <= W; i++) {
      const y = H/2
        + Math.sin(i * freq       + t * speed + phase)       * amp
        + Math.sin(i * freq * 2.1 + t * speed * 1.3 + phase) * (amp * 0.4)
        + Math.sin(i * freq * 0.4 + t * speed * 0.6)         * (amp * 0.25);
      i === 0 ? ctx.moveTo(i, y) : ctx.lineTo(i, y);
    }
    ctx.stroke();
  }

  function drawParticles() {
    const W = c.width;
    // small glowing dots riding the main wave
    for (let i = 0; i < W; i += Math.floor(W / 12)) {
      const y = c.height/2
        + Math.sin(i * 0.017 + t) * 22
        + Math.sin(i * 0.034 + t * 1.4) * 9;
      const alpha = 0.4 + 0.5 * Math.sin(t * 2 + i * 0.3);
      ctx.beginPath();
      ctx.arc(i, y, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0,255,204,${alpha})`;
      ctx.shadowColor = '#00ffcc';
      ctx.shadowBlur  = 10;
      ctx.fill();
    }
  }

  function draw() {
    const W = c.width, H = c.height;
    ctx.clearRect(0, 0, W, H);

    // Wave 3 – deep purple ghost
    drawWave(10, 0.012, 0.4,  2.5, 'rgba(124,58,237,0.18)', 1,   0);
    // Wave 2 – blue mid-layer
    drawWave(14, 0.019, 0.6,  1.2, 'rgba(59,108,248,0.3)',  1.5, 6);
    // Wave 1 – main teal
    drawWave(22, 0.017, 1.0,  0,   'rgba(0,255,204,0.82)',  2.8, 14);
    // Wave 0 – bright highlight (thin)
    drawWave(22, 0.017, 1.0,  0,   'rgba(180,255,240,0.4)', 1.2, 4);

    drawParticles();

    t += 0.036;
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>
"""

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS  (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
def sanitize(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

async def _recognize(path: str):
    return await Shazam().recognize(path)

def recognize_song(audio_bytes: bytes) -> dict | None:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        return asyncio.run(_recognize(tmp))
    except Exception as e:
        st.error(f"Recognition error: {e}")
        return None
    finally:
        os.unlink(tmp)

def search_youtube_id(title: str, artist: str) -> str | None:
    q = quote(f"{title} {artist} audio")
    try:
        r = requests.get(
            f"https://www.youtube.com/results?search_query={q}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        m = re.search(r"watch\?v=(\S{11})", r.text)
        return m.group(1) if m else None
    except Exception:
        return None

def download_mp3_bytes(title: str, artist: str) -> tuple[bytes | None, str]:
    vid_id = search_youtube_id(title, artist)
    if not vid_id:
        return None, ""
    filename = sanitize(f"{title} - {artist or 'Unknown'}.mp3")
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdir, "song.%(ext)s"),
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "prefer_ffmpeg": True,
            "quiet": True,
            "no_warnings": True,
            **({"cookiefile": "yt-cookies.txt"} if os.path.exists("yt-cookies.txt") else {}),
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={vid_id}"])
        except Exception as e:
            st.error(f"yt-dlp error: {e}")
            return None, ""
        mp3 = os.path.join(tmpdir, "song.mp3")
        if not os.path.exists(mp3):
            return None, ""
        with open(mp3, "rb") as f:
            return f.read(), filename

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {"song": None, "mp3_bytes": None, "mp3_filename": ""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(STYLE, unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-header">
  <div class="bs-logo-wrap">
    <div class="bs-logo-icon">🎵</div>
    <h1 class="bs-title">BeatSnatch</h1>
  </div>
  <p class="bs-tagline">Music Recognition &amp; Download</p>
  <div class="bs-badge-row">
    <span class="bs-badge green">192kbps MP3</span>
    <span class="bs-badge green">No Files Saved</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── VISUALIZER ──────────────────────────────────────────────────────────────────
st.components.v1.html(VISUALIZER_HTML, height=124, scrolling=False)

st.markdown('<hr class="bs-divider"/>', unsafe_allow_html=True)

# ── RECORD CARD ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-glass bs-record-card">
  <div class="bs-record-hint">
    <p>Record to identify</p>
    <p>Only 10 seconds is enough</p>
    <div class="bs-step-row">
      <div class="bs-step"><span class="bs-step-num">1</span> Tap mic</div>
      <div class="bs-step"><span class="bs-step-num">2</span> Play song nearby</div>
      <div class="bs-step"><span class="bs-step-num">3</span> Press stop</div>
    </div>
  </div>
""", unsafe_allow_html=True)

try:
    audio_value = st.audio_input("Record audio", label_visibility="collapsed")
except AttributeError:
    audio_value = st.file_uploader(
        "Upload a short audio clip (WAV / MP3 / WebM)",
        type=["wav", "mp3", "webm", "ogg"],
        label_visibility="collapsed",
    )

if audio_value is not None:
    raw = audio_value.read() if hasattr(audio_value, "read") else bytes(audio_value)
    identify_clicked = st.button("🔍  Identify Song", use_container_width=True)
else:
    identify_clicked = False
    st.markdown('<p class="bs-status primary">Ready — tap the mic above to begin</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close bs-record-card

# ── RECOGNITION ────────────────────────────────────────────────────────────────
if identify_clicked:
    st.session_state.song      = None
    st.session_state.mp3_bytes = None
    st.markdown("""
    <div class="bs-loader">
      <span></span><span></span><span></span>
    </div>
    <p class="bs-status primary">Analyzing audio with Shazam…</p>
    """, unsafe_allow_html=True)
    result = recognize_song(raw)
    if result and "track" in result:
        track = result["track"]
        st.session_state.song = {
            "title":  track.get("title",    "Unknown Title"),
            "artist": track.get("subtitle", "Unknown Artist"),
        }
    else:
        st.markdown(
            '<p class="bs-status danger">❌ Song not recognized — try a longer or clearer clip.</p>',
            unsafe_allow_html=True,
        )

# ── SONG CARD ──────────────────────────────────────────────────────────────────
if st.session_state.song:
    s      = st.session_state.song
    title  = s["title"]
    artist = s["artist"]
    sp_url = f"https://open.spotify.com/search/{quote(title + ' ' + artist)}"
    yt_url = f"https://www.youtube.com/results?search_query={quote(title + ' ' + artist)}"

    st.markdown(f"""
    <div class="bs-glass bs-song-card">
      <div class="bs-song-inner">
        <div class="bs-art">
          <div class="bs-art-inner">🎶</div>
        </div>
        <div class="bs-song-meta">
          <div class="bs-song-chip">
            <i class="fas fa-check-circle" style="font-size:.7rem"></i>&nbsp; Identified
          </div>
          <div class="bs-song-title">{title}</div>
          <div class="bs-song-artist">{artist}</div>
        </div>
      </div>
      <div class="bs-song-divider"></div>
      <div class="bs-btn-row">
        <a class="bs-btn bs-btn-spotify" href="{sp_url}" target="_blank" rel="noopener">
          <i class="fab fa-spotify"></i>&nbsp; Spotify
        </a>
        <a class="bs-btn bs-btn-youtube" href="{yt_url}" target="_blank" rel="noopener">
          <i class="fab fa-youtube"></i>&nbsp; YouTube
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── DOWNLOAD CARD ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="bs-glass bs-dl-card">
      <div class="bs-dl-header">
        <div class="bs-dl-icon">⬇</div>
        <div>
          <div class="bs-dl-label">Download MP3</div>
          <div class="bs-dl-desc">High-quality 192 kbps · no files stored on server</div>
        </div>
      </div>
    """, unsafe_allow_html=True)

    if st.button("⚡  Prepare MP3", use_container_width=True, key="prep_dl"):
        with st.spinner(f'Fetching "{title}" from YouTube and converting to MP3…'):
            mp3, fname = download_mp3_bytes(title, artist)
        if mp3:
            st.session_state.mp3_bytes    = mp3
            st.session_state.mp3_filename = fname
        else:
            st.markdown(
                '<p class="bs-status danger">❌ Download failed — YouTube may have blocked the request.</p>',
                unsafe_allow_html=True,
            )

    if st.session_state.mp3_bytes:
        st.markdown('<div class="bs-btn-gap">', unsafe_allow_html=True)
        st.download_button(
            label=f"💾  Save MP3  ·  {st.session_state.mp3_filename}",
            data=st.session_state.mp3_bytes,
            file_name=st.session_state.mp3_filename,
            mime="audio/mpeg",
            use_container_width=True,
            key="dl_btn",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="bs-status success" style="padding-bottom:.5rem">✅ MP3 ready — click Save above to download</p>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)  # close bs-dl-card

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-footer">
  <div class="bs-footer-inner">
    <div class="bs-footer-name">Made with <span>♥</span> by Debojeet Bhowmick</div>
    <a class="bs-footer-link" href="https://debojeet-bhowmick.netlify.app" target="_blank" rel="noopener">
      debojeet-bhowmick.netlify.app
    </a>
    <div class="bs-footer-copy">Copyright &copy; 2026 DEWizards Pvt. Ltd. All rights reserved.</div>
  </div>
</div>
""", unsafe_allow_html=True)