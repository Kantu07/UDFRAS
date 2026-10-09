# UDFRAS: Universal DVR/NVR Forensic Recovery & Analysis System

[![SIH Problem Statement](https://img.shields.io/badge/SIH-SIH26150-blue.svg)](https://www.sih.gov.in)
[![Domain](https://img.shields.io/badge/Domain-Cybersecurity%20%26%20Digital%20Forensics-red.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-green.svg)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal.svg)](#)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](#)

> **Development of a Multi-Vendor DVR/NVR Forensic Analysis Tool for Standardized Acquisition, Recovery, and Analysis of Surveillance Evidence.**

---

## 📌 Project Overview

Digital forensic examiners frequently encounter closed-circuit television (CCTV) DVRs/NVRs from diverse manufacturers (Dahua, Hikvision, CP Plus, etc.) that implement non-standard, proprietary file systems (such as `DHFS`, raw disk blocks, and custom partition indexes). Standard forensic and commercial tools are often vendor-locked, prohibitively expensive, or incapable of automated cross-vendor detection.

**UDFRAS** provides an open, standardized, and court-admissible forensic pipeline:
1. **Forensic Acquisition & Hashing:** Enforces strict read-only bit-stream ingestion with dual cryptographic verification (**SHA-256** and **MD5**).
2. **Automated Vendor Detection:** Fingerprints proprietary header magic bytes and sector layouts without modifying source media.
3. **Stream Parsing & File Carving:** Recovers deleted, damaged, or fragmented video streams via H.264/H.265 I-frame/P-frame NAL boundary inspection.
4. **Timeline Reconstruction:** Normalizes proprietary timestamps to UTC ISO-8601 with multi-camera chronological alignment and clock drift correction.
5. **Chain-of-Custody & Forensic Reporting:** Auto-generates tamper-evident forensic reports complying with ISO/IEC 27037 standards.

---

## 🏗️ System Architecture

```text
Raw Storage Media (.dd / .img)
   │
   ├──> [1. Read-Only Ingestion Gate & Dual Hasher (SHA-256 / MD5)]
   │
   ├──> [2. Header Signature & Vendor Detection Engine]
   │       ├── Dahua (DHFS4.1 / DHFS)
   │       ├── Hikvision (HIKG / HKCS)
   │       ├── CP Plus (OEM DHFS variant)
   │       └── Generic / Fallback
   │
   ├──> [3. Storage Adapters & Carving Engine]
   │       └── Frame boundary & NAL carving
   │
   ├──> [4. Normalization & Timeline Correlator]
   │       └── Multi-channel chronological mapping
   │
   └──> [5. Court-Admissible Reporting & Web Dashboard]
```

---

## 📁 Repository Structure

```text
├── apps/
│   ├── api/                 # FastAPI backend services and REST endpoints
│   └── web/                 # React + Vite forensic dashboard
├── docs/
│   └── PHASE_1_WEEK_1_PLAN.md # Phase 1 sprint plan & faculty review checklist
├── fixtures/
│   ├── demo_dvr/            # Reference synthetic DVR test image and manifest
│   ├── evidence_videos/     # Multi-channel sample surveillance videos (CAM01, CAM02)
│   └── generator/           # Synthetic disk image generator scripts
├── packages/
│   ├── adapters/            # Multi-vendor parser adapters & signature registry
│   ├── core/                # Models, timeline events, evidence structures
│   └── forensics/           # Streaming cryptographic hashing & integrity modules
├── SAT-SA/                  # Supervisory analytics module
└── tests/                   # Pytest automated test suites
```

---

## 🚀 Quick Start

### 1. Backend (FastAPI)

```bash
cd apps/api
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Frontend (React + Vite)

```bash
cd apps/web
npm install
npm run dev
```

---

## 📜 Phase 1 Roadmap (Week 1)
Detailed task breakdown, deliverables, test plan, and viva defense Q&A are documented in:
👉 **[`docs/PHASE_1_WEEK_1_PLAN.md`](docs/PHASE_1_WEEK_1_PLAN.md)**
