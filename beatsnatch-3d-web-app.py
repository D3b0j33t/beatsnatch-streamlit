import streamlit as st
import asyncio
import re
import os
import tempfile
from shazamio import Shazam
import yt_dlp
from urllib.parse import quote
import requests

st.set_page_config(
    page_title="BeatSnatch - By Debojeet",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS — all containers transparent so the 3D background shows through
# ══════════════════════════════════════════════════════════════════════════════
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --primary:  #00ffcc;
  --blue:     #3b6cf8;
  --purple:   #7c3aed;
  --spotify:  #1DB954;
  --youtube:  #ff0000;
  --gold:     #fbbf24;
  --danger:   #f87171;
  --success:  #34d399;
  --bg:       #07070f;
  --text:     #f1f5f9;
  --text2:    #94a3b8;
  --text3:    #7a8fa6;
  --border:   rgba(255,255,255,0.08);
  --card:     rgba(6,6,18,0.72);
  --r:        18px;
  --rb:       100px;
}

/* ── Make every Streamlit layer transparent so 3D canvas shows through ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, .block-container,
[data-testid="block-container"],
[data-testid="stVerticalBlock"],
[data-testid="element-container"],
[data-testid="stMarkdownContainer"] {
  background: transparent !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* Deep fallback bg colour in case canvas hasn't loaded yet */
body { background-color: #07070f !important; }

/* Remove any pseudo-element backgrounds */
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after { display: none !important; }

[data-testid="stMain"] { position: relative; z-index: 1; }

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stSidebarNav"],
.viewerBadge_container__1QSob,
[data-testid="manage-app-button"] { display: none !important; }

[data-testid="block-container"] {
  max-width: 680px !important;
  width: 100% !important;
  margin: 0 auto !important;
  padding: clamp(1rem,4vw,2.4rem) clamp(0.9rem,4vw,1.6rem) clamp(2rem,5vw,4rem) !important;
}

/* fix Streamlit default <p> margins */
[data-testid="stMarkdownContainer"] p {
  margin-bottom: 0 !important;
  margin-top: 0 !important;
}
[data-testid="stMarkdownContainer"] a {
  color: inherit !important;
  text-decoration: none !important;
}

/* ── HEADER ── */
.bs-header {
  text-align: center;
  padding: clamp(.4rem,2vw,.9rem) 0 clamp(.3rem,1.5vw,.5rem);
}
.bs-logo-wrap {
  display: inline-flex; align-items: center; gap: clamp(8px,2vw,14px);
  margin-bottom: 6px;
}
.bs-logo-box {
  width: clamp(38px,7vw,50px); height: clamp(38px,7vw,50px);
  border-radius: 13px;
  background: linear-gradient(135deg, rgba(0,255,204,0.15), rgba(59,108,248,0.12));
  border: 1px solid rgba(0,255,204,0.3);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(18px,4vw,26px);
  box-shadow: 0 0 22px rgba(0,255,204,0.18), inset 0 1px 0 rgba(255,255,255,0.1);
  flex-shrink: 0;
}

/* h1 — beat Streamlit high-specificity rules */
.bs-title,
h1.bs-title,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h1.bs-title {
  font-family: 'Orbitron', sans-serif !important;
  font-size: clamp(2rem,7vw,3.1rem) !important;
  font-weight: 900 !important;
  color: var(--primary) !important;
  letter-spacing: .05em !important;
  text-shadow: 0 0 12px rgba(0,255,204,.7), 0 0 28px rgba(0,255,204,.4), 0 0 55px rgba(0,255,204,.2) !important;
  animation: flicker 3s infinite alternate !important;
  line-height: 1 !important;
  margin: 0 0 0.2rem 0 !important;
  padding: 0 !important;
}
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
  font-family: 'Orbitron', sans-serif !important;
  color: var(--text) !important;
  margin: 0 !important;
}

.bs-tagline {
  font-family: 'Orbitron', sans-serif !important;
  font-size: clamp(.5rem,1.4vw,.62rem) !important;
  color: rgba(0,255,204,.5) !important;
  letter-spacing: .3em; text-transform: uppercase;
  margin-top: 5px !important;
}
.bs-badges {
  display: flex; gap: 8px; justify-content: center;
  margin-top: 12px; flex-wrap: wrap;
}
.bs-badge {
  font-size: clamp(.6rem,1.5vw,.66rem); font-weight: 600;
  letter-spacing: .07em; text-transform: uppercase;
  padding: 3px 11px; border-radius: 100px;
  background: rgba(0,0,0,.4); border: 1px solid rgba(255,255,255,.12);
  color: var(--text2);
}
.bs-badge.teal {
  background: rgba(0,255,204,.1); border-color: rgba(0,255,204,.25); color: var(--primary);
}

/* ── DIVIDER ── */
.bs-divider {
  border: none; height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,.3), rgba(59,108,248,.2), transparent);
  margin: clamp(.7rem,2vw,1.3rem) 0;
}

/* ── GLASS CARD — stronger backdrop so content is readable over 3D ── */
.bs-glass {
  background: var(--card);
  backdrop-filter: blur(28px) saturate(160%) brightness(0.9);
  -webkit-backdrop-filter: blur(28px) saturate(160%) brightness(0.9);
  border: 1px solid var(--border);
  border-radius: var(--r);
  position: relative; overflow: hidden;
}
.bs-glass::before {
  content: ''; position: absolute; inset: 0; border-radius: inherit;
  background: linear-gradient(135deg, rgba(255,255,255,.05) 0%, transparent 55%);
  pointer-events: none;
}

/* ── RECORD CARD ── */
.bs-record-card {
  padding: clamp(1.1rem,3vw,1.7rem) clamp(.9rem,3vw,1.7rem) clamp(.9rem,2.5vw,1.4rem);
  border-color: rgba(0,255,204,.14);
  box-shadow: 0 8px 32px rgba(0,0,0,.6), 0 0 0 1px rgba(0,0,0,.3);
}
.bs-record-card::after {
  content: ''; position: absolute;
  top: 0; left: 30%; right: 30%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,.5), transparent);
}
.bs-rec-hint { text-align: center; margin-bottom: clamp(.7rem,2vw,1rem); }
.bs-rec-hint-label {
  font-size: clamp(.68rem,1.8vw,.77rem);
  color: var(--text3) !important;
  text-transform: uppercase; letter-spacing: .14em; font-weight: 600;
}
.bs-steps {
  display: flex; justify-content: center; gap: clamp(10px,3vw,22px);
  margin-top: 8px; flex-wrap: wrap;
}
.bs-step {
  display: flex; align-items: center; gap: 6px;
  font-size: clamp(.63rem,1.7vw,.7rem); color: var(--text2); font-weight: 500;
}
.bs-step-n {
  width: 18px; height: 18px; border-radius: 50%;
  background: rgba(0,255,204,.1); border: 1px solid rgba(0,255,204,.28);
  color: var(--primary); font-size: .6rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

/* ── AUDIO INPUT ── */
[data-testid="stAudioInput"] {
  background: rgba(0,0,0,.3) !important;
  border: 1px solid rgba(0,255,204,.16) !important;
  border-radius: 13px !important;
  padding: 5px 7px !important;
}
[data-testid="stAudioInput"] label { display: none !important; }
[data-testid="stAudioInput"] button {
  background: radial-gradient(circle at 40% 35%, #191930, #090914) !important;
  border: 2px solid rgba(0,255,204,.32) !important;
  color: var(--primary) !important;
  border-radius: 50% !important;
  transition: all .28s ease !important;
}
[data-testid="stAudioInput"] button:hover {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 8px rgba(0,255,204,.08), 0 0 26px rgba(0,255,204,.4) !important;
  transform: scale(1.09) !important;
}
[data-testid="stAudioInput"] > div > p {
  color: rgba(0,255,204,.35) !important;
  font-size: .73rem !important; font-family: 'Inter', sans-serif !important;
}
[data-testid="stAudioInput"] audio,
[data-testid="stAudio"] audio { border-radius: 10px; width: 100%; }

/* ── BUTTONS ── */
[data-testid="stButton"] button {
  width: 100% !important;
  background: linear-gradient(135deg, #00d4a8, #0093b8) !important;
  color: #001810 !important;
  font-weight: 700 !important; font-family: 'Inter', sans-serif !important;
  border: none !important; border-radius: var(--rb) !important;
  padding: clamp(.58rem,2vw,.72rem) 2rem !important;
  font-size: clamp(.87rem,2.2vw,.97rem) !important;
  letter-spacing: .04em !important; text-transform: uppercase !important;
  transition: all .28s ease !important;
  box-shadow: 0 4px 22px rgba(0,212,168,.3), 0 1px 0 rgba(255,255,255,.15) inset !important;
}
[data-testid="stButton"] button:hover {
  background: linear-gradient(135deg, #00ffcc, #00b0d8) !important;
  box-shadow: 0 8px 32px rgba(0,255,204,.5) !important;
  transform: translateY(-2px) !important; color: #001810 !important;
}
[data-testid="stButton"] button:active { transform: scale(.98) !important; }

[data-testid="stDownloadButton"] button {
  width: 100% !important;
  background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
  color: #1c1000 !important;
  font-weight: 700 !important; font-family: 'Inter', sans-serif !important;
  border: none !important; border-radius: var(--rb) !important;
  padding: clamp(.58rem,2vw,.72rem) 2rem !important;
  font-size: clamp(.87rem,2.2vw,.97rem) !important;
  letter-spacing: .04em !important; text-transform: uppercase !important;
  transition: all .28s ease !important;
  box-shadow: 0 4px 22px rgba(251,191,36,.35), 0 1px 0 rgba(255,255,255,.25) inset !important;
}
[data-testid="stDownloadButton"] button:hover {
  background: linear-gradient(135deg, #fcd34d, #fbbf24) !important;
  box-shadow: 0 8px 32px rgba(251,191,36,.55) !important;
  transform: translateY(-2px) !important; color: #1c1000 !important;
}

/* ── STATUS ── */
.bs-status {
  text-align: center;
  font-size: clamp(.8rem,2vw,.9rem) !important;
  color: var(--text2);
  padding: clamp(.4rem,1.2vw,.65rem) 0 0;
  letter-spacing: .02em;
}
.bs-status.p { color: var(--primary) !important; }
.bs-status.e { color: var(--danger)  !important; }
.bs-status.s { color: var(--success) !important; }

/* ── SONG CARD ── */
.bs-song-card {
  padding: clamp(1.1rem,3.5vw,1.7rem);
  border-color: rgba(0,255,204,.16);
  margin: clamp(.7rem,2vw,1.1rem) 0;
  animation: slideUp .5s cubic-bezier(.16,1,.3,1);
  box-shadow: 0 8px 32px rgba(0,0,0,.7);
}
.bs-song-card::after {
  content: ''; position: absolute;
  top: 0; left: 35%; right: 35%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(0,255,204,.6), transparent);
}
.bs-song-inner { display: flex; gap: clamp(10px,3vw,18px); align-items: flex-start; }
.bs-art {
  flex-shrink: 0;
  width: clamp(64px,15vw,88px); height: clamp(64px,15vw,88px);
  border-radius: 13px;
  background: linear-gradient(135deg, rgba(0,255,204,.1), rgba(59,108,248,.15));
  border: 1px solid rgba(0,255,204,.22);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.5rem,4vw,2rem);
  position: relative; overflow: hidden;
  box-shadow: 0 0 28px rgba(0,255,204,.12);
}
.bs-art::before {
  content: ''; position: absolute; inset: -50%;
  background: conic-gradient(from 0deg, transparent 0deg, rgba(0,255,204,.16) 60deg,
    transparent 120deg, transparent 360deg);
  animation: spin 5s linear infinite;
}
.bs-art-em { position: relative; z-index: 1; }
.bs-meta { flex: 1; min-width: 0; }
.bs-chip {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: clamp(.58rem,1.5vw,.64rem); font-weight: 700;
  letter-spacing: .13em; text-transform: uppercase;
  color: var(--primary);
  background: rgba(0,255,204,.1); border: 1px solid rgba(0,255,204,.24);
  border-radius: 100px; padding: 3px 10px; margin-bottom: 9px;
}
.bs-stitle {
  font-size: clamp(.96rem,3.2vw,1.28rem) !important;
  font-weight: 700 !important; color: #fff !important;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  line-height: 1.2; margin-bottom: 4px;
}
.bs-sartist {
  font-size: clamp(.75rem,2vw,.88rem) !important;
  color: var(--text2) !important;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.bs-sep { height: 1px; background: rgba(255,255,255,.06); margin: clamp(.8rem,2.5vw,1.1rem) 0; }
.bs-links { display: grid; grid-template-columns: 1fr 1fr; gap: clamp(7px,2vw,11px); }
@media (max-width: 340px) { .bs-links { grid-template-columns: 1fr; } }
.bs-btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: clamp(5px,1.5vw,7px); font-weight: 600; font-family: 'Inter', sans-serif;
  padding: clamp(9px,2.5vw,12px) clamp(9px,2.5vw,14px);
  border-radius: var(--rb); text-decoration: none !important;
  transition: all .24s ease; font-size: clamp(.76rem,2vw,.85rem);
  cursor: pointer; border: none; text-align: center;
}
.bs-sp { background: linear-gradient(135deg,#1DB954,#15a347) !important; color:#fff !important; box-shadow: 0 4px 15px rgba(29,185,84,.3); }
.bs-sp:hover { background: linear-gradient(135deg,#1ed760,#1DB954) !important; transform: translateY(-2px); box-shadow: 0 7px 22px rgba(29,185,84,.45); color:#fff !important; }
.bs-yt { background: linear-gradient(135deg,#ff0000,#bb0000) !important; color:#fff !important; box-shadow: 0 4px 15px rgba(255,0,0,.3); }
.bs-yt:hover { background: linear-gradient(135deg,#ff3333,#ff0000) !important; transform: translateY(-2px); box-shadow: 0 7px 22px rgba(255,0,0,.4); color:#fff !important; }

/* ── DOWNLOAD CARD ── */
.bs-dl-card {
  border-color: rgba(251,191,36,.16);
  background: rgba(6,5,0,.65);
  padding: clamp(1.1rem,3vw,1.5rem) clamp(.9rem,3vw,1.6rem);
  margin-top: clamp(.6rem,1.5vw,.9rem);
  animation: slideUp .4s cubic-bezier(.16,1,.3,1);
  box-shadow: 0 8px 32px rgba(0,0,0,.6);
}
.bs-dl-card::after {
  content: ''; position: absolute; top: 0; left: 40%; right: 40%; height: 1px;
  background: linear-gradient(to right, transparent, rgba(251,191,36,.55), transparent);
}
.bs-dl-top { display: flex; align-items: center; gap: 10px; margin-bottom: clamp(.8rem,2.5vw,1.1rem); }
.bs-dl-ico {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  background: rgba(251,191,36,.12); border: 1px solid rgba(251,191,36,.24);
  display: flex; align-items: center; justify-content: center; font-size: 13px;
}
.bs-dl-lbl { font-size: clamp(.66rem,1.7vw,.73rem); font-weight: 700; letter-spacing: .17em; text-transform: uppercase; color: rgba(251,191,36,.88) !important; }
.bs-dl-sub { font-size: clamp(.64rem,1.6vw,.7rem); color: var(--text3) !important; margin-top: 1px; }
.bs-gap { margin-top: clamp(7px,2vw,11px); }

/* ── LOADER ── */
.bs-loader { display: flex; gap: clamp(7px,2vw,10px); justify-content: center; align-items: center; padding: clamp(.7rem,2vw,1.1rem) 0 clamp(.3rem,1vw,.5rem); }
.bs-loader span { width: clamp(8px,2vw,10px); height: clamp(8px,2vw,10px); background: var(--primary); border-radius: 50%; animation: ldBounce 1.4s infinite ease-in-out; box-shadow: 0 0 10px rgba(0,255,204,.5); }
.bs-loader span:nth-child(2) { animation-delay:.18s; opacity:.75; }
.bs-loader span:nth-child(3) { animation-delay:.36s; opacity:.5; }

/* ── FOOTER ── */
.bs-footer { margin-top: clamp(1.8rem,4vw,3rem); padding-top: clamp(.9rem,2vw,1.3rem); border-top: 1px solid rgba(255,255,255,.06); text-align: center; }
.bs-foot-row { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.bs-foot-name { font-size: 1rem; color: var(--text2) !important; font-weight: 500; font-family: 'Orbitron', sans-serif !important; }
.bs-foot-name .heart { color: #ef4444 !important; }
.bs-foot-link { font-size: 0.95rem; color: rgba(0,255,204,.65) !important; text-decoration: none !important; transition: color .2s; font-weight: 500; font-family: 'Orbitron', sans-serif !important; }
.bs-foot-link:hover { color: var(--primary) !important; }
.bs-foot-copy { font-size: 0.8rem; color: var(--text2) !important; opacity: .5; font-family: 'Orbitron', sans-serif !important; }

/* ── SPINNER / ALERT ── */
[data-testid="stSpinner"] > div { border-top-color: var(--primary) !important; }
[data-testid="stSpinner"] p { color: var(--text2) !important; font-family:'Inter',sans-serif !important; }
[data-testid="stAlert"] { border-radius: 12px !important; background: rgba(248,113,113,.08) !important; border: 1px solid rgba(248,113,113,.2) !important; color: var(--danger) !important; }

/* ── RESPONSIVE ── */
@media (max-width: 460px) {
  .bs-song-inner { flex-direction: column; align-items: center; text-align: center; }
  .bs-art { margin: 0 auto; }
  .bs-chip { margin: 0 auto 9px; }
  .bs-stitle, .bs-sartist { white-space: normal; }
}

/* ── KEYFRAMES ── */
@keyframes flicker {
  0%,19%,21%,23%,25%,54%,56%,100% { opacity:1; }
  20%,22%,24%,55% { opacity:.58; }
}
@keyframes slideUp {
  from { opacity:0; transform:translateY(20px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes ldBounce {
  0%,80%,100% { transform:scale(.35); opacity:.3; }
  40%         { transform:scale(1);   opacity:1; }
}
@keyframes spin {
  from { transform:rotate(0deg); }
  to   { transform:rotate(360deg); }
}
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
# THREE.JS BACKGROUND INJECTOR
# Injects a <canvas> + Three.js directly into window.parent.document.body
# so it becomes a true full-page fixed background behind all Streamlit content.
# ══════════════════════════════════════════════════════════════════════════════
THREEJS_BG_INJECTOR = """
<script>
(function(){
  var p = window.parent.document;

  /* ── inject fonts ── */
  if(!p.getElementById('bs-fonts')){
    var lf=p.createElement('link');
    lf.id='bs-fonts'; lf.rel='stylesheet';
    lf.href='https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap';
    p.head.appendChild(lf);
  }

  /* ── already injected? skip ── */
  if(p.getElementById('bs-3d-canvas')) return;

  /* ── create fixed canvas ── */
  var canvas = p.createElement('canvas');
  canvas.id  = 'bs-3d-canvas';
  canvas.style.cssText = [
    'position:fixed','top:0','left:0',
    'width:100vw','height:100vh',
    'z-index:0','pointer-events:none',
    'display:block'
  ].join(';');
  p.body.prepend(canvas);

  /* ── load Three.js into parent then start scene ── */
  var s = p.createElement('script');
  s.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
  s.onload = function(){ startScene(canvas); };
  p.head.appendChild(s);

  function startScene(canvas){
    var THREE = window.parent.THREE;

    var renderer = new THREE.WebGLRenderer({canvas:canvas, antialias:true, alpha:true});
    renderer.setPixelRatio(Math.min(window.parent.devicePixelRatio||1, 2));
    renderer.toneMapping         = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.4;
    renderer.shadowMap.enabled   = true;
    renderer.shadowMap.type      = THREE.PCFSoftShadowMap;

    var scene  = new THREE.Scene();
    scene.fog  = new THREE.FogExp2(0x07070f, 0.016);
    var camera = new THREE.PerspectiveCamera(65, 1, 0.1, 200);
    camera.position.set(0,7,20);
    camera.lookAt(0,0,0);

    function resize(){
      var W = window.parent.innerWidth;
      var H = window.parent.innerHeight;
      renderer.setSize(W, H, false);
      camera.aspect = W/H;
      camera.updateProjectionMatrix();
    }
    resize();
    window.parent.addEventListener('resize', resize);

    /* floor */
    var grid = new THREE.GridHelper(80,50,0x001a14,0x000d0d);
    grid.position.y = -4; scene.add(grid);
    var floor = new THREE.Mesh(
      new THREE.PlaneGeometry(80,80),
      new THREE.MeshStandardMaterial({color:0x040408,metalness:.85,roughness:.25,transparent:true,opacity:.45})
    );
    floor.rotation.x=-Math.PI/2; floor.position.y=-4.01; floor.receiveShadow=true; scene.add(floor);

    /* vinyl */
    var disc = new THREE.Mesh(
      new THREE.CylinderGeometry(2.8,2.8,.2,80),
      new THREE.MeshStandardMaterial({color:0x0a0a0a,metalness:.9,roughness:.08})
    );
    disc.receiveShadow=true; scene.add(disc);
    [1.5,2.0,2.5].forEach(function(r){
      var m=new THREE.Mesh(new THREE.TorusGeometry(r,.025,8,80),
        new THREE.MeshStandardMaterial({color:0x001510,metalness:.7,roughness:.3}));
      m.rotation.x=Math.PI/2; scene.add(m);
    });
    var lbl=new THREE.Mesh(new THREE.CylinderGeometry(.6,.6,.22,40),
      new THREE.MeshStandardMaterial({color:0x00ffcc,emissive:0x00ffcc,emissiveIntensity:.6,metalness:.4,roughness:.3}));
    lbl.position.y=.01; scene.add(lbl);

    /* rings */
    function makeRing(r,tube,col,ei){
      return new THREE.Mesh(new THREE.TorusGeometry(r,tube,16,90),
        new THREE.MeshStandardMaterial({color:col,emissive:col,emissiveIntensity:ei,transparent:true,opacity:.88}));
    }
    var gR=makeRing(3.0,.07,0x00ffcc,2.5); gR.rotation.x=Math.PI/2; scene.add(gR);
    var bR=makeRing(3.8,.04,0x3b6cf8,1.8); bR.rotation.x=Math.PI/2; scene.add(bR);
    var pR=makeRing(4.5,.035,0x7c3aed,1.5); pR.rotation.x=Math.PI/2; pR.rotation.z=.3; scene.add(pR);

    /* frequency bars */
    var BC=72, BR=6.5, bars=[];
    for(var i=0;i<BC;i++){
      var a=(i/BC)*Math.PI*2, r=(i%3===0)?BR+.4:BR;
      var col=new THREE.Color().setHSL(.45+(i/BC)*.22,1,.58);
      var b=new THREE.Mesh(new THREE.CylinderGeometry(.1,.13,1,6),
        new THREE.MeshStandardMaterial({color:col,emissive:col,emissiveIntensity:.85,
          metalness:.5,roughness:.18,transparent:true,opacity:.92}));
      b.position.set(Math.cos(a)*r,0,Math.sin(a)*r);
      b.castShadow=true; scene.add(b); bars.push(b);
    }

    /* stars */
    var SC=2000,sp=new Float32Array(SC*3),sc=new Float32Array(SC*3);
    var tC=new THREE.Color(0x00ffcc),bC=new THREE.Color(0x3b6cf8),wC=new THREE.Color(0xffffff);
    for(var i=0;i<SC;i++){
      var th=Math.random()*Math.PI*2,ph=Math.acos(2*Math.random()-1),rd=18+Math.random()*28;
      sp[i*3]=rd*Math.sin(ph)*Math.cos(th); sp[i*3+1]=(Math.random()-.5)*26; sp[i*3+2]=rd*Math.sin(ph)*Math.sin(th);
      var pp=Math.random(),cl=pp<.35?tC:pp<.6?bC:wC;
      sc[i*3]=cl.r; sc[i*3+1]=cl.g; sc[i*3+2]=cl.b;
    }
    var sG=new THREE.BufferGeometry();
    sG.setAttribute('position',new THREE.BufferAttribute(sp,3));
    sG.setAttribute('color',new THREE.BufferAttribute(sc,3));
    var stars=new THREE.Points(sG,new THREE.PointsMaterial({size:.12,vertexColors:true,transparent:true,opacity:.72,sizeAttenuation:true}));
    scene.add(stars);

    /* inner particles */
    var IC=350,ip=new Float32Array(IC*3);
    for(var i=0;i<IC;i++){ip[i*3]=(Math.random()-.5)*14;ip[i*3+1]=(Math.random()-.5)*10;ip[i*3+2]=(Math.random()-.5)*14;}
    var iG=new THREE.BufferGeometry();
    iG.setAttribute('position',new THREE.BufferAttribute(ip,3));
    var iPts=new THREE.Points(iG,new THREE.PointsMaterial({color:0x00ffcc,size:.07,transparent:true,opacity:.5,sizeAttenuation:true}));
    scene.add(iPts);

    /* knots */
    var kd=[{p:[8,2,-4],s:.28,c:0x00ffcc,sp:.008},{p:[-9,3,2],s:.22,c:0x3b6cf8,sp:.011},
            {p:[5,-1,8],s:.18,c:0x7c3aed,sp:.014},{p:[-6,1,-7],s:.2,c:0x00ffcc,sp:.009}];
    var knots=kd.map(function(d){
      var m=new THREE.Mesh(new THREE.TorusKnotGeometry(1,.3,80,12,2,3),
        new THREE.MeshStandardMaterial({color:d.c,emissive:d.c,emissiveIntensity:.7,
          metalness:.6,roughness:.2,transparent:true,opacity:.65,wireframe:true}));
      m.position.set(d.p[0],d.p[1],d.p[2]); m.scale.setScalar(d.s); m.userData=d; scene.add(m); return m;
    });

    /* lights */
    scene.add(new THREE.AmbientLight(0x0a0a14,2));
    var mL=new THREE.PointLight(0x00ffcc,3.5,25); mL.position.set(0,4,0); mL.castShadow=true; scene.add(mL);
    var bL=new THREE.PointLight(0x3b6cf8,2.2,20); bL.position.set(-10,4,-6); scene.add(bL);
    var pL=new THREE.PointLight(0x7c3aed,1.8,18); pL.position.set(10,3,6); scene.add(pL);
    var dL=new THREE.DirectionalLight(0x001a10,1.2); dL.position.set(0,10,-10); scene.add(dL);

    /* animate */
    var t=0;
    function sim(i,t){
      var n=i/BC;
      return .12+1.2*Math.abs(Math.sin(n*4.1+t*1.8))+.8*Math.abs(Math.sin(n*9.3+t*2.6))
            +.5*Math.abs(Math.sin(n*17.7+t*1.1))+.3*Math.abs(Math.sin(n*2.5+t*3.4))+.2*Math.sin(t*5+i*.18);
    }
    function animate(){
      window.parent.requestAnimationFrame(animate); t+=.016;
      bars.forEach(function(b,i){var h=Math.max(.08,sim(i,t));b.scale.y=h;b.position.y=h*.5-.3;b.material.emissiveIntensity=.4+h*.45;});
      disc.rotation.y+=.006; lbl.rotation.y+=.006;
      gR.rotation.z+=.003; bR.rotation.z+=.004;
      pR.rotation.z-=.003; pR.rotation.x=Math.PI/2+Math.sin(t*.4)*.15;
      knots.forEach(function(k,i){k.rotation.x+=k.userData.sp;k.rotation.y+=k.userData.sp*.7;k.position.y=kd[i].p[1]+Math.sin(t*.6+i)*.6;});
      stars.rotation.y+=.0004; iPts.rotation.y-=.0007;
      mL.intensity=3+Math.sin(t*2.8)*.7;
      bL.position.x=-10+Math.sin(t*.5)*2; bL.position.z=-6+Math.cos(t*.5)*2;
      var ca=t*.12;
      camera.position.x=Math.cos(ca)*20; camera.position.z=Math.sin(ca)*20;
      camera.position.y=7+Math.sin(t*.2)*1.5; camera.lookAt(0,.5,0);
      renderer.render(scene,camera);
    }
    animate();
  }
})();
</script>
"""

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

async def _recognize(path):
    return await Shazam().recognize(path)

def recognize_song(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes); tmp = f.name
    try:
        return asyncio.run(_recognize(tmp))
    except Exception as e:
        st.error(f"Recognition error: {e}"); return None
    finally:
        os.unlink(tmp)

# def search_youtube_id(title, artist):
#     q = quote(f"{title} {artist} audio")
#     try:
#         r = requests.get(f"https://www.youtube.com/results?search_query={q}",
#                          headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
#         m = re.search(r"watch\?v=(\S{11})", r.text)
#         return m.group(1) if m else None
#     except Exception:
#         return None

def download_mp3_bytes(title, artist):
    query    = f"ytsearch1:{title} {artist} audio"
    filename = sanitize(f"{title} - {artist or 'Unknown'}.mp3")

    # Each tuple is tried in order until one succeeds
    client_attempts = [
        ["android_music"],
        ["tv_embedded"],
        ["android"],
        ["mweb"],
    ]

    for clients in client_attempts:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(tmpdir, "song.%(ext)s"),
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "prefer_ffmpeg": True,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "extractor_args": {
                    "youtube": {"player_client": clients}
                },
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Mobile Safari/537.36"
                    ),
                },
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])
                mp3 = os.path.join(tmpdir, "song.mp3")
                if os.path.exists(mp3):
                    with open(mp3, "rb") as f:
                        return f.read(), filename
            except Exception:
                continue  # try next client

    st.error("Download failed — all player clients blocked. Try adding a yt-cookies.txt file.")
    return None, ""

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {"song":None,"mp3_bytes":None,"mp3_filename":""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(STYLE, unsafe_allow_html=True)

# Inject Three.js as fixed background + fonts — height=1 to avoid iframe collapse
st.components.v1.html(THREEJS_BG_INJECTOR, height=1, scrolling=False)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-header">
  <div class="bs-logo-wrap">
    <!-- <div class="bs-logo-box">🎵</div> -->
    <h1 class="bs-title">Beatsnatch</h1>
  </div>
  <p class="bs-tagline">Music Recognition &amp; Download</p>
  <div class="bs-badges">
    <span class="bs-badge teal">✦ 192 kbps MP3</span>
    <span class="bs-badge teal">✦ Zero Storage</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="bs-divider"/>', unsafe_allow_html=True)

# ── RECORD CARD ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-glass bs-record-card">
  <div class="bs-rec-hint">
    <p class="bs-rec-hint-label">Record the song for 10 seconds</p>
    <div class="bs-steps">
      <div class="bs-step"><span class="bs-step-n">1</span>Tap the mic</div>
      <div class="bs-step"><span class="bs-step-n">2</span>Play the song</div>
      <div class="bs-step"><span class="bs-step-n">3</span>Hit stop</div>
    </div>
  </div>
""", unsafe_allow_html=True)

try:
    audio_value = st.audio_input("Record audio", label_visibility="collapsed")
except AttributeError:
    audio_value = st.file_uploader("Upload a short audio clip",
        type=["wav","mp3","webm","ogg"], label_visibility="collapsed")

if audio_value is not None:
    raw = audio_value.read() if hasattr(audio_value,"read") else bytes(audio_value)
    identify_clicked = st.button("Identify Song", use_container_width=True)
else:
    identify_clicked = False
    st.markdown('<p class="bs-status p">Ready — tap the mic above to begin</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── RECOGNITION ────────────────────────────────────────────────────────────────
if identify_clicked:
    st.session_state.song = None
    st.session_state.mp3_bytes = None
    st.markdown('<div class="bs-loader"><span></span><span></span><span></span></div><p class="bs-status p">Analyzing the audio…</p>', unsafe_allow_html=True)
    result = recognize_song(raw)
    if result and "track" in result:
        track = result["track"]
        st.session_state.song = {"title":track.get("title","Unknown Title"),"artist":track.get("subtitle","Unknown Artist")}
    else:
        st.markdown('<p class="bs-status e">&#10060; Not recognized — try a longer clip.</p>', unsafe_allow_html=True)

# ── SONG CARD ──────────────────────────────────────────────────────────────────
if st.session_state.song:
    s = st.session_state.song
    title, artist = s["title"], s["artist"]
    sp_url = f"https://open.spotify.com/search/{quote(title+' '+artist)}"
    yt_url = f"https://www.youtube.com/results?search_query={quote(title+' '+artist)}"

    st.markdown(f"""
    <div class="bs-glass bs-song-card">
      <div class="bs-song-inner">
        <div class="bs-art"><div class="bs-art-em">🎶</div></div>
        <div class="bs-meta">
          <div class="bs-chip">&#10003;&nbsp;Identified</div>
          <div class="bs-stitle">{title}</div>
          <div class="bs-sartist">{artist}</div>
        </div>
      </div>
      <div class="bs-sep"></div>
      <div class="bs-links">
        <a class="bs-btn bs-sp" href="{sp_url}" target="_blank" rel="noopener">&#9654;&nbsp;Spotify</a>
        <a class="bs-btn bs-yt" href="{yt_url}" target="_blank" rel="noopener">&#9654;&nbsp;YouTube</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Fetch the Song", use_container_width=True, key="prep_dl"):
        with st.spinner(f'Fetching "{title}" and converting…'):
            mp3, fname = download_mp3_bytes(title, artist)
        if mp3:
            st.session_state.mp3_bytes = mp3
            st.session_state.mp3_filename = fname
        else:
            st.markdown('<p class="bs-status e">&#10060; Download failed.</p>', unsafe_allow_html=True)

    if st.session_state.mp3_bytes:
        st.markdown('<div class="bs-gap">', unsafe_allow_html=True)
        st.download_button(
            label=f"Download MP3  ·  {st.session_state.mp3_filename}",
            data=st.session_state.mp3_bytes,
            file_name=st.session_state.mp3_filename,
            mime="audio/mpeg",
            use_container_width=True,
            key="dl_btn",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p class="bs-status s" style="padding-bottom:.5rem">&#10003; Your file is ready — click Download above</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bs-footer">
  <div class="bs-foot-row">
    <div class="bs-foot-name">Made with <span class="heart">&#9829;</span> by Debojeet Bhowmick</div>
    <a class="bs-foot-link" href="https://debojeet-bhowmick.netlify.app" target="_blank" rel="noopener">Visit My Website</a>
    <div class="bs-foot-copy">Copyright &copy; 2026 DEWizards Pvt. Ltd. All rights reserved.</div>
  </div>
</div>
""", unsafe_allow_html=True)