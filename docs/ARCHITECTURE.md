# 🏗️ CineForge Replit — Architecture Whitepaper (Replit Track)

## 1. System Overview
**CineForge Replit** combines a published **Replit App** with **Google Gemini 2.5 Flash** to provide a zero-setup cinema review studio.

```mermaid
graph TD
    Judge([🎬 Creator / Judge]) --> |1-Click Run| ReplitContainer[⚡ Replit Container<br/>.replit + replit.nix Engine]
    ReplitContainer --> WebUI[🖥️ Interactive Studio Web UI<br/>(Script & Camera Staging Console)]
    WebUI --> CoDirector[🤖 CoDirectorAgent]
    CoDirector --> Gemini[🌟 Google Gemini 2.5 Flash<br/>(Dialogue & Visual Direction)]
    CoDirector --> ReplitEngine[☁️ Replit Runtime Evidence]
    ReplitEngine --> Snapshot[📋 In-Session Review Snapshot]
    Snapshot --> WebUI
```

---

## 2. End-to-End Workflow
1. **1-Click Launch**: Replit triggers `replit.nix` and `run_backend.py`, serving the studio on port 8004.
2. **Collaborative Script Input**: Creator inputs a scene draft and director instruction.
3. **Gemini 2.5 Co-Direction**: Calls `google-genai` in live mode to generate dialogue delivery notes and camera, lighting, sound, and visual-staging guidance.
4. **Review Snapshot**: The runtime service records an in-memory review packet and derives hosting evidence from Replit's predefined environment variables.
5. **UI Rendering**: Displays the review packet, runtime mode, measured request latency, and whether the process is a published Replit deployment.
