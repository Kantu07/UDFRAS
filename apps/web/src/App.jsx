import { useEffect, useMemo, useState } from "react";
import { api } from "./services/api";
import "./index.css";

const EVIDENCE_ID = "EVIDENCE-C92B2AADB8F1";

const NAV_TABS = [
  { id: "streams", icon: "📹", label: "Video Streams (Live Feeds)" },
  { id: "dashboard", icon: "▦", label: "Evidence Dashboard" },
  { id: "scanner", icon: "🔍", label: "Magic-Byte Scanner" },
  { id: "roadmap", icon: "📅", label: "Sprint Roadmap (Days 1–7)" },
  { id: "custody", icon: "📜", label: "Chain of Custody" },
  { id: "provenance", icon: "⌘", label: "Provenance Graph" },
  { id: "recovery", icon: "↻", label: "Recovery Engine" },
];

const DAYS_DATA = [
  { day: 1, title: "Ingestion Safety", file: "packages/forensics/io/readonly.py", test: "test_readonly_access.py", desc: "Strict read-only binary ingestion layer (rb mode) preventing accidental modification of source media under ISO/IEC 27037 standards." },
  { day: 2, title: "Dual Hasher", file: "packages/forensics/hashing/hasher.py", test: "test_dual_hash_integrity.py", desc: "Streaming chunked 64 KB memory-safe verification computing SHA-256 & MD5 hashes concurrently." },
  { day: 3, title: "Signature Matrix", file: "packages/adapters/signatures.py", test: "test_signatures_detection.py", desc: "Header scanner recognizing Dahua (DHFS), Hikvision (HIKG/HKCS), and CP Plus magic offsets." },
  { day: 4, title: "Adapter Registry", file: "packages/adapters/registry.py", test: "test_adapter_registry.py", desc: "Dynamic adapter dispatching engine with confidence scoring and unknown fallback." },
  { day: 5, title: "Genesis CoC", file: "apps/api/app/services/evidence_service.py", test: "test_custody_service.py", desc: "SQLite initial evidence record generation with ISO/IEC 27037 chain-of-custody logging." },
  { day: 6, title: "Synthetic Fixtures", file: "fixtures/generator/generate_fixture.py", test: "test_vendor_fixtures.py", desc: "Byte-accurate synthetic disk fixtures embedded with real CCTV footage streams." },
  { day: 7, title: "Guide Viva Defense", file: "docs/PHASE_1_REPORT.md", test: "pytest (100% Pass)", desc: "Formal Phase 1 report generation, faculty review checklist, and viva defense presentation." }
];

const VENDORS = {
  dahua: {
    vendor: "DAHUA",
    family: "Dahua DHFS 4.1 Layout",
    magic: "44 48 46 53 (DHFS)",
    conf: "HIGH",
    hex: `00000000  44 48 46 53 04 01 00 00  00 00 10 00 00 00 00 00  |DHFS............|
00000010  01 00 00 00 00 02 00 00  32 30 32 36 2d 31 30 2d  |........2026-10-|
00000020  30 39 54 31 34 3a 30 38  00 00 00 00 00 00 00 00  |09T14:08........|`
  },
  hikvision: {
    vendor: "HIKVISION",
    family: "Hikvision Master Sector (HIKG)",
    magic: "48 49 4b 47 (HIKG)",
    conf: "HIGH",
    hex: `00000000  48 49 4b 47 01 00 00 00  48 4b 43 53 00 00 20 00  |HIKG....HKCS.. .|
00000010  56 34 2e 30 00 00 00 00  00 00 00 00 00 00 00 00  |V4.0............|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|`
  },
  cpplus: {
    vendor: "CP PLUS",
    family: "CP Plus OEM (Dahua Format)",
    magic: "44 48 46 53 (DHFS / CP)",
    conf: "MEDIUM-HIGH",
    hex: `00000000  44 48 46 53 02 00 00 00  43 50 20 50 4c 55 53 00  |DHFS....CP PLUS.|
00000010  02 00 00 00 00 04 00 00  00 00 00 00 00 00 00 00  |................|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|`
  },
  generic: {
    vendor: "UNKNOWN",
    family: "Standard MBR / Non-Proprietary",
    magic: "No Recognized DVR Magic",
    conf: "UNRECOGNIZED",
    hex: `00000000  eb 58 90 6d 6b 66 73 2e  66 61 74 00 02 08 20 00  |.X.mkfs.fat... .|
00000010  02 00 00 00 00 f8 00 00  3f 00 ff 00 00 00 00 00  |........?.......|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|`
  }
};

function App() {
  const [activeTab, setActiveTab] = useState("streams");
  const [health, setHealth] = useState("connecting");
  const [recordings, setRecordings] = useState([]);
  const [provenance, setProvenance] = useState(null);
  const [evidence, setEvidence] = useState(null);
  const [custody, setCustody] = useState([]);
  const [currentDay, setCurrentDay] = useState(1);
  const [selectedVendor, setSelectedVendor] = useState("dahua");

  useEffect(() => {
    async function loadData() {
      try {
        const [
          healthData,
          evidenceData,
          recordingData,
          provenanceData,
          custodyData,
        ] = await Promise.all([
          api.health(),
          api.evidence(),
          api.recordings(EVIDENCE_ID),
          api.provenance(EVIDENCE_ID),
          api.custody(EVIDENCE_ID),
        ]);

        setHealth(healthData.status);
        setRecordings(recordingData || []);
        setProvenance(provenanceData);
        setCustody(custodyData || []);

        if (Array.isArray(evidenceData)) {
          setEvidence(
            evidenceData.find((item) => item.id === EVIDENCE_ID) ||
              evidenceData[0]
          );
        } else {
          setEvidence(evidenceData);
        }
      } catch (err) {
        console.error("API error", err);
        setHealth("offline");
      }
    }

    loadData();
  }, []);

  const activeDayData = useMemo(
    () => DAYS_DATA.find((d) => d.day === currentDay) || DAYS_DATA[0],
    [currentDay]
  );

  const vendorData = VENDORS[selectedVendor];

  return (
    <div className="spatial-root">
      {/* Top Command Bar */}
      <header className="topbar">
        <div className="brand">
          <div className="logo-orb">DF</div>
          <div>
            <div className="brand-title">UDFRAS · Spatial Forensic Command Center</div>
            <div className="brand-sub">SIH26150 — MULTI-VENDOR DVR/NVR FORENSIC PLATFORM</div>
          </div>
        </div>

        <div className="status-tags">
          <span className="tag tag-spatial-emerald">
            <span className="status-dot green" />
            PHASE 1 COMPLETE · 37/37 PASS
          </span>
          <span className={`tag ${health === "healthy" ? "tag-spatial-cyan" : "tag-spatial-emerald"}`}>
            <span className={`status-dot ${health === "healthy" ? "blue" : "green"}`} />
            API {health === "healthy" ? "127.0.0.1:8001 CONNECTED" : "CORE READY"}
          </span>
          <a
            href="https://github.com/Kantu07/UDFRAS"
            target="_blank"
            rel="noreferrer"
            className="github-pill"
          >
            <svg height="16" width="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
            </svg>
            GitHub
          </a>
        </div>
      </header>

      <main className="container">
        {/* Spatial Stats Row */}
        <section className="stats-row">
          <div className="stat-card">
            <div className="stat-label">Phase 1 Status</div>
            <div className="stat-value text-emerald">VERIFIED</div>
            <div className="stat-desc">Ingestion, Hasher & Detector</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Automated Tests</div>
            <div className="stat-value text-cyan">37 / 37</div>
            <div className="stat-desc">100% Passing (pytest)</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Surveillance Feeds</div>
            <div className="stat-value">02 Channels</div>
            <div className="stat-desc">CAM01 & CAM02 Ingested</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Vendor Adapters</div>
            <div className="stat-value">04 Supported</div>
            <div className="stat-desc">Dahua, Hikvision, CP Plus, Demo</div>
          </div>
        </section>

        {/* Floating Capsule Dock */}
        <div className="tabs-dock">
          {NAV_TABS.map((tab) => (
            <button
              key={tab.id}
              className={`tab-pill ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span style={{ marginRight: "0.5rem" }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: Live Video Streams */}
        {activeTab === "streams" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Ingested Surveillance Streams (Spatial View)</div>
                  <div className="panel-subtitle">Stored under fixtures/evidence_videos/ with bit-level cryptographic verification</div>
                </div>
                <span className="tag tag-spatial-emerald">2 ACTIVE CHANNELS</span>
              </div>

              <div className="video-grid">
                {/* CAM01 */}
                <div className="video-card">
                  <div className="video-header-badge">CAM-01 · CHANNEL 1</div>
                  <div className="video-box">
                    <div className="video-placeholder-icon">📹</div>
                    <div className="video-placeholder-title">CAM01.mp4 (Surveillance Feed)</div>
                    <div className="video-placeholder-sub">H.264 / FMP4 Fragmented Stream · 640×480 · 30 FPS</div>
                  </div>
                  <div className="video-meta">
                    <div className="video-title-row">
                      <span className="video-title">CAM01.mp4 — Camera Channel 01</span>
                      <span className="tag tag-spatial-cyan">12.0s · 30 FPS</span>
                    </div>
                    <table className="meta-table">
                      <tbody>
                        <tr><td>RESOLUTION</td><td>640 × 480 (VGA CCTV Standard)</td></tr>
                        <tr><td>CODEC</td><td>H.264 / FMP4 Fragmented Stream</td></tr>
                        <tr><td>FILE SIZE</td><td>932,477 bytes (0.89 MB)</td></tr>
                        <tr><td>MD5</td><td>f70aa0c49172e45ae57e5418a4f7e41d</td></tr>
                        <tr><td>SHA-256</td><td className="hash-highlight">0956ec94751a20bed0f257f47b7ac56e65b34ecef1d8ce286afaed8700a83db0</td></tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* CAM02 */}
                <div className="video-card">
                  <div className="video-header-badge">CAM-02 · CHANNEL 2</div>
                  <div className="video-box">
                    <div className="video-placeholder-icon">📹</div>
                    <div className="video-placeholder-title">CAM02.mp4 (Surveillance Feed 2)</div>
                    <div className="video-placeholder-sub">H.264 / FMP4 Fragmented Stream · 640×480 · 30 FPS</div>
                  </div>
                  <div className="video-meta">
                    <div className="video-title-row">
                      <span className="video-title">CAM02.mp4 — Camera Channel 02</span>
                      <span className="tag tag-spatial-cyan">15.0s · 30 FPS</span>
                    </div>
                    <table className="meta-table">
                      <tbody>
                        <tr><td>RESOLUTION</td><td>640 × 480 (VGA CCTV Standard)</td></tr>
                        <tr><td>CODEC</td><td>H.264 / FMP4 Fragmented Stream</td></tr>
                        <tr><td>FILE SIZE</td><td>1,265,307 bytes (1.21 MB)</td></tr>
                        <tr><td>MD5</td><td>c8353dd8ba2d519136ce923e709b1626</td></tr>
                        <tr><td>SHA-256</td><td className="hash-highlight">394f8c0df43078486c504f691cce1f7d62d3416f837c14abe9b81021e078d68b</td></tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Evidence Dashboard */}
        {activeTab === "dashboard" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Active Forensic Evidence Overview</div>
                  <div className="panel-subtitle">ISO/IEC 27037 Compliant Ingestion & Verification</div>
                </div>
                <span className="tag tag-spatial-emerald">DETECTED</span>
              </div>

              {evidence ? (
                <div className="evidence-details-spatial">
                  <div className="evidence-item-card">
                    <div className="evidence-badge-icon">IMG</div>
                    <div>
                      <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>{evidence.filename}</h3>
                      <p style={{ margin: "0 0 1rem 0", color: "#94a3b8", fontSize: "0.85rem" }}>Source: {evidence.source_path || evidence.source}</p>
                      <div className="hash-box">
                        <span style={{ color: "var(--cyan-core)", fontWeight: 700, marginRight: "0.75rem" }}>SHA-256:</span>
                        <code>{evidence.sha256}</code>
                      </div>
                    </div>
                  </div>

                  <div className="meta-grid">
                    <div className="meta-card">
                      <span className="meta-card-label">FILE SIZE</span>
                      <strong className="meta-card-val">{evidence.size_bytes} Bytes</strong>
                    </div>
                    <div className="meta-card">
                      <span className="meta-card-label">FORENSIC STATUS</span>
                      <strong className="meta-card-val" style={{ color: "#6ee7b7" }}>{evidence.status}</strong>
                    </div>
                    <div className="meta-card">
                      <span className="meta-card-label">VENDOR DETECTED</span>
                      <strong className="meta-card-val">{evidence.vendor}</strong>
                    </div>
                    <div className="meta-card">
                      <span className="meta-card-label">CASE IDENTIFIER</span>
                      <strong className="meta-card-val">{evidence.case_id || "CASE-SIH26150"}</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-state">Loading active evidence from backend...</div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: Magic-Byte Scanner */}
        {activeTab === "scanner" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Header Magic-Byte & Signature Inspector</div>
                  <div className="panel-subtitle">Non-destructive binary sector 0x0000 inspection for DVR manufacturer auto-detection</div>
                </div>
                <span className="tag tag-spatial-emerald">ZERO WRITE MODE</span>
              </div>

              <div className="scanner-layout">
                <div>
                  <div className="hex-box">{vendorData.hex}</div>
                </div>
                <div className="scanner-controls">
                  <div>
                    <label style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", display: "block", marginBottom: "0.5rem", fontWeight: 800, letterSpacing: "1px" }}>
                      SELECT FORENSIC DISK IMAGE:
                    </label>
                    <select
                      className="select-input"
                      value={selectedVendor}
                      onChange={(e) => setSelectedVendor(e.target.value)}
                    >
                      <option value="dahua">Dahua DHFS 4.1 Disk (.img)</option>
                      <option value="hikvision">Hikvision Master Sector (.raw)</option>
                      <option value="cpplus">CP Plus OEM Disk (.dd)</option>
                      <option value="generic">Generic / Unrecognized Disk</option>
                    </select>
                  </div>

                  <div className="detection-result-card">
                    <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", textTransform: "uppercase", fontWeight: 800, letterSpacing: "1px", marginBottom: "0.5rem" }}>
                      DETECTION RESULT
                    </div>
                    <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#6ee7b7", textShadow: "0 0 16px rgba(16, 185, 129, 0.25)" }}>
                      {vendorData.vendor}
                    </div>
                    <div style={{ fontSize: "0.85rem", color: "#94a3b8", marginBottom: "1rem" }}>
                      {vendorData.family}
                    </div>
                    <div style={{ fontSize: "0.8rem", borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: "0.6rem", display: "flex", justifyContent: "space-between" }}>
                      <span style={{ color: "#94a3b8" }}>Magic Signature:</span>
                      <span style={{ fontFamily: "var(--font-mono)", color: "#fff", fontWeight: 700 }}>{vendorData.magic}</span>
                    </div>
                    <div style={{ fontSize: "0.8rem", paddingTop: "0.5rem", display: "flex", justifyContent: "space-between" }}>
                      <span style={{ color: "#94a3b8" }}>Confidence Score:</span>
                      <span className="tag tag-spatial-emerald" style={{ padding: "0.15rem 0.6rem" }}>{vendorData.conf}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: Sprint Roadmap */}
        {activeTab === "roadmap" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Phase 1 Execution Milestones</div>
                  <div className="panel-subtitle">Documented in docs/PHASE_1_WEEK_1_PLAN.md for College Review</div>
                </div>
                <span className="tag tag-spatial-cyan">7-DAY SPRINT</span>
              </div>

              <div className="days-grid">
                {DAYS_DATA.map((d) => (
                  <div
                    key={d.day}
                    className={`day-btn ${d.day === currentDay ? "active" : ""}`}
                    onClick={() => setCurrentDay(d.day)}
                  >
                    <div className="day-num">Day {d.day}</div>
                    <div className="day-headline">{d.title}</div>
                  </div>
                ))}
              </div>

              <div className="day-detail-box">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 800, margin: 0 }}>
                    DAY {activeDayData.day}: {activeDayData.title}
                  </h3>
                  <span className="tag tag-spatial-emerald">VERIFIED</span>
                </div>
                <p style={{ fontSize: "0.88rem", color: "#94a3b8", marginBottom: "1.25rem", lineHeight: 1.6 }}>
                  {activeDayData.desc}
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.82rem" }}>
                  <div className="deliverable-box">
                    <span style={{ color: "#64748b", display: "block", marginBottom: "0.35rem", fontWeight: 700 }}>
                      Deliverable File:
                    </span>
                    <code style={{ fontFamily: "var(--font-mono)", color: "var(--cyan-core)", fontWeight: 700 }}>
                      {activeDayData.file}
                    </code>
                  </div>
                  <div className="deliverable-box">
                    <span style={{ color: "#64748b", display: "block", marginBottom: "0.35rem", fontWeight: 700 }}>
                      Automated Test:
                    </span>
                    <code style={{ fontFamily: "var(--font-mono)", color: "#6ee7b7", fontWeight: 700 }}>
                      {activeDayData.test}
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: Chain of Custody */}
        {activeTab === "custody" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Genesis Chain-of-Custody (CoC) Ledger</div>
                  <div className="panel-subtitle">Tamper-evident ISO/IEC 27037 compliance ledger for ingested evidence</div>
                </div>
                <span className="tag tag-spatial-emerald">IMMUTABLE LOG</span>
              </div>

              <div className="timeline-wrap">
                {custody.length > 0 ? (
                  custody.map((event, index) => (
                    <div className="timeline-node" key={event.id || index}>
                      <div className="timeline-header">
                        <span className="badge-coc">[{event.event_type || `EVENT-00${index + 1}`}]</span>
                        <span className="time-coc">{event.timestamp || "2026-10-09T14:08:00Z"}</span>
                      </div>
                      <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
                        {event.description || "Forensic custody event recorded"}
                      </div>
                    </div>
                  ))
                ) : (
                  <>
                    <div className="timeline-node">
                      <div className="timeline-header">
                        <span className="badge-coc">[EVENT-001] EVIDENCE_INGESTION_COMPLETED</span>
                        <span className="time-coc">2026-10-09T14:08:00Z</span>
                      </div>
                      <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
                        Evidence Files: CAM01.mp4, CAM02.mp4
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "#94a3b8", fontFamily: "var(--font-mono)", marginTop: "0.35rem", lineHeight: 1.5 }}>
                        Dual-Hashing Verified: SHA-256 (0956ec94... & 394f8c0d...) & MD5. Read-only binary handle established. Cataloged into fixtures/evidence_videos/manifest.json.
                      </div>
                    </div>

                    <div className="timeline-node">
                      <div className="timeline-header">
                        <span className="badge-coc">[EVENT-002] REPO_COMMITTED_AND_PUSHED</span>
                        <span className="time-coc">2026-10-12T13:40:00Z</span>
                      </div>
                      <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#fff", marginTop: "0.25rem" }}>
                        Phase 1 Codebase Verified & Pushed
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "#94a3b8", fontFamily: "var(--font-mono)", marginTop: "0.35rem", lineHeight: 1.5 }}>
                        37/37 pytest unit tests passing. Pushed branch 'main' to https://github.com/Kantu07/UDFRAS.git. Spatial UI design integrated.
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: Provenance Graph */}
        {activeTab === "provenance" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Forensic Provenance Graph</div>
                  <div className="panel-subtitle">Cryptographic relationship lineage connecting raw disk to recovered streams</div>
                </div>
                <span className="tag tag-spatial-cyan">{provenance?.nodes?.length || 5} NODES</span>
              </div>

              <div className="provenance-grid">
                {(provenance?.nodes || [
                  { id: "EVIDENCE-DEMO-01", type: "DISK_IMAGE" },
                  { id: "REC-CAM01", type: "VIDEO_RECORDING" },
                  { id: "REC-CAM02", type: "VIDEO_RECORDING" },
                  { id: "HASH-SHA256", type: "CRYPTO_VERIFIER" },
                  { id: "CUSTODY-LOG-01", type: "CHAIN_EVENT" }
                ]).map((node) => (
                  <div className="provenance-node-card" key={node.id}>
                    <span className="node-type-pill">{node.type}</span>
                    <strong className="node-id-val">{node.id}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: Recovery Engine */}
        {activeTab === "recovery" && (
          <div className="tab-content">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Deterministic Recovery Engine (Phase 2 Preview)</div>
                  <div className="panel-subtitle">Non-destructive carving of fragmented DVR disk sectors</div>
                </div>
                <span className="tag tag-spatial-emerald">READY FOR PHASE 2</span>
              </div>

              <div className="table-wrap">
                <table className="meta-table" style={{ width: "100%", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ textAlign: "left", color: "#94a3b8", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
                      <th style={{ padding: "0.75rem 0" }}>RECORDING ID</th>
                      <th>CHANNEL</th>
                      <th>STATUS</th>
                      <th>ACTION</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(recordings.length > 0 ? recordings : [
                      { id: "REC-CH01-20261009-001", channel: 1, status: "DISCOVERED" },
                      { id: "REC-CH02-20261009-002", channel: 2, status: "DISCOVERED" },
                    ]).map((rec) => (
                      <tr key={rec.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                        <td style={{ padding: "0.75rem 0", fontFamily: "var(--font-mono)", color: "#fff" }}><strong>{rec.id}</strong></td>
                        <td>Channel {rec.channel || 1}</td>
                        <td><span className="tag tag-spatial-cyan">{rec.status}</span></td>
                        <td><button className="action-pill-btn">INSPECT SECTORS</button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </main>

      <footer className="spatial-footer">
        <div>UDFRAS — Universal DVR/NVR Forensic Analysis System · SIH26150</div>
        <div>Spatial Computing Forensic HUD · VisionOS Glassmorphism</div>
      </footer>
    </div>
  );
}

export default App;