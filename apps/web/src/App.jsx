import { useState } from "react";
import "./index.css";

const EVIDENCE = [
  {
    id: "CAM-01",
    filename: "CAM01.mp4",
    title: "Channel 01 — Main Surveillance",
    src: "/CAM01.mp4",
    duration: "12.0s",
    fps: "30 FPS",
    resolution: "640 × 480",
    size: "932,477 bytes",
    codec: "H.264 / FMP4",
    md5: "f70aa0c49172e45ae57e5418a4f7e41d",
    sha256: "0956ec94751a20bed0f257f47b7ac56e65b34ecef1d8ce286afaed8700a83db0",
    status: "INTACT (READ-ONLY)",
  },
  {
    id: "CAM-02",
    filename: "CAM02.mp4",
    title: "Channel 02 — Perimeter Surveillance",
    src: "/CAM02.mp4",
    duration: "15.0s",
    fps: "30 FPS",
    resolution: "640 × 480",
    size: "1,265,307 bytes",
    codec: "H.264 / FMP4",
    md5: "c8353dd8ba2d519136ce923e709b1626",
    sha256: "394f8c0df43078486c504f691cce1f7d62d3416f837c14abe9b81021e078d68b",
    status: "INTACT (READ-ONLY)",
  },
];

function App() {
  const [selectedCam, setSelectedCam] = useState(EVIDENCE[0]);
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <div className="spatial-viewport">
      {/* VisionOS Floating Top Glass Capsule */}
      <header className="spatial-header">
        <div className="brand-group">
          <div className="vision-orb">
            <span>DF</span>
          </div>
          <div>
            <div className="brand-title">UDFRAS FORENSIC PLAYER</div>
            <div className="brand-sub">SIH26150 · CCTV EVIDENCE HUD</div>
          </div>
        </div>

        <div className="dock-pill-selector">
          {EVIDENCE.map((cam) => (
            <button
              key={cam.id}
              className={`pill-btn ${selectedCam.id === cam.id ? "active" : ""}`}
              onClick={() => setSelectedCam(cam)}
            >
              <span className="live-dot" />
              {cam.id}
            </button>
          ))}
        </div>

        <div className="integrity-capsule">
          <span className="shield-icon">🛡️</span>
          <span>ISO/IEC 27037 LOCKED</span>
        </div>
      </header>

      {/* Main Spatial Stage */}
      <main className="spatial-stage">
        {/* Left: Glass Player */}
        <section className="glass-player-card">
          <div className="player-toolbar">
            <div className="channel-indicator">
              <span className="pulsing-record-dot" />
              <strong>{selectedCam.title}</strong>
            </div>
            <span className="pill-badge">{selectedCam.codec}</span>
          </div>

          <div className="video-viewport">
            <video
              key={selectedCam.src}
              src={selectedCam.src}
              controls
              autoPlay
              muted
              playsInline
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              className="native-video-elem"
            />
          </div>

          <div className="player-subbar">
            <span>RES: {selectedCam.resolution}</span>
            <span>FPS: {selectedCam.fps}</span>
            <span>LEN: {selectedCam.duration}</span>
            <span className="status-highlight">{selectedCam.status}</span>
          </div>
        </section>

        {/* Right: Glass Forensic Metadata Capsule */}
        <aside className="glass-meta-card">
          <div className="card-heading">
            <h3>CRYPTOGRAPHIC INTEGRITY</h3>
            <span className="verified-pill">✓ VERIFIED</span>
          </div>

          <div className="meta-field">
            <label>FILE NAME</label>
            <div className="field-val">{selectedCam.filename}</div>
          </div>

          <div className="meta-field">
            <label>EXACT SIZE</label>
            <div className="field-val">{selectedCam.size}</div>
          </div>

          <div className="meta-field">
            <label>MD5 CHECKSUM</label>
            <div className="field-code">{selectedCam.md5}</div>
          </div>

          <div className="meta-field">
            <label>SHA-256 HASH (DUAL HASHER)</label>
            <div className="field-code highlight-sha">{selectedCam.sha256}</div>
          </div>

          <div className="meta-field">
            <label>EVIDENCE ACCESS MODE</label>
            <div className="immutable-box">
              <span className="lock-icon">🔒</span>
              Strict Read-Only Binary Handle (O_RDONLY / "rb")
            </div>
          </div>

          <div className="quick-switch-section">
            <label>SELECT EVIDENCE CHANNEL</label>
            <div className="switch-grid">
              {EVIDENCE.map((cam) => (
                <div
                  key={cam.id}
                  className={`switch-card ${selectedCam.id === cam.id ? "selected" : ""}`}
                  onClick={() => setSelectedCam(cam)}
                >
                  <div className="switch-top">
                    <strong>{cam.id}</strong>
                    <span>{cam.duration}</span>
                  </div>
                  <div className="switch-name">{cam.filename}</div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </main>

      {/* Floating Ambient Footer */}
      <footer className="spatial-bottom-dock">
        <span>UDFRAS · Universal DVR/NVR Forensic Recovery and Analysis System</span>
        <span className="dot-sep">·</span>
        <span className="glow-cyan">Spatial HUD</span>
      </footer>
    </div>
  );
}

export default App;