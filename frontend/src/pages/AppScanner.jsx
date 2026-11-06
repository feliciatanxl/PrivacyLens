import { useEffect, useRef, useState } from "react";
import {
  Upload,
  Scan,
  Shield,
  Eye,
  EyeOff,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Download,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Layers,
  X
} from "lucide-react";
import { API_BASE } from "../config";

export default function AppScanner() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState("");
  const [error, setError] = useState("");
  const [scanMode, setScanMode] = useState("fast"); // 'fast' | 'comprehensive'

  // Redaction state
  const [selectedIndices, setSelectedIndices] = useState(new Set());
  const [manualBoxes, setManualBoxes] = useState([]);
  const [previewMode, setPreviewMode] = useState("inspect"); // 'inspect' | 'redacted'
  const [drawingMode, setDrawingMode] = useState(false);
  const [dragStart, setDragStart] = useState(null);
  const [currentDragBox, setCurrentDragBox] = useState(null);
  const [focusedIndex, setFocusedIndex] = useState(null);
  const [redacting, setRedacting] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showBoxes, setShowBoxes] = useState(true);
  const [imageDims, setImageDims] = useState({ width: 1, height: 1 });

  const imageContainerRef = useRef(null);
  const imageElementRef = useRef(null);

  useEffect(() => {
    return () => {
      if (preview && preview.startsWith("blob:")) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    if (!["image/png", "image/jpeg", "image/jpg", "image/webp"].includes(selectedFile.type)) {
      setError("Please upload a PNG, JPEG, or WebP image.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("Image file exceeds the 10 MB limit.");
      return;
    }

    loadFile(selectedFile);
  }

  function loadFile(newFile) {
    setFile(newFile);
    setPreview(URL.createObjectURL(newFile));
    setResult(null);
    setSelectedIndices(new Set());
    setManualBoxes([]);
    setPreviewMode("inspect");
    setDrawingMode(false);
    setError("");
    setFocusedIndex(null);
    setZoomLevel(1);
  }

  // Quick Demo Loader for Judges
  async function loadDemoImage(samplePath, sampleName) {
    setError("");
    setLoading(true);
    setLoadingPhase("Loading pre-configured demo sample...");
    try {
      const response = await fetch(samplePath);
      if (!response.ok) throw new Error("Could not load sample file.");
      const blob = await response.blob();
      const demoFile = new File([blob], sampleName, { type: blob.type || "image/png" });
      loadFile(demoFile);
    } catch (err) {
      setError(`Failed to load sample: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    if (!file) return;

    setLoading(true);
    setLoadingPhase(
      scanMode === "fast"
        ? "Running PaddleOCR & Fast Privacy Detectors..."
        : "Executing Deep Florence-2 Vision & Multimodal Scanners..."
    );
    setError("");
    setResult(null);
    setFocusedIndex(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("scan_mode", scanMode);

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let detail = `Analysis failed (${response.status}).`;
        try {
          const body = await response.json();
          if (typeof body.detail === "string") {
            detail = body.detail;
          }
        } catch {
          // Keep status error
        }
        throw new Error(detail);
      }

      const data = await response.json();
      setResult(data);

      // Default: auto-select all findings with valid bounding boxes
      const findings = data?.privacy?.findings ?? [];
      const initialSelected = new Set();
      findings.forEach((f, idx) => {
        if (f.box && Array.isArray(f.box) && f.box.length === 4) {
          initialSelected.add(idx);
        }
      });
      setSelectedIndices(initialSelected);
    } catch (err) {
      setError(err.message || "Could not connect to the PrivacyLens AI server. Please verify backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  function toggleFindingRedaction(idx) {
    setSelectedIndices((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  }

  function toggleSelectAll(select) {
    const findings = result?.privacy?.findings ?? [];
    if (select) {
      const all = new Set();
      findings.forEach((f, idx) => {
        if (f.box) all.add(idx);
      });
      setSelectedIndices(all);
    } else {
      setSelectedIndices(new Set());
    }
  }

  // Interactive Drag-to-Draw Custom Redaction Box
  function getCanvasCoords(event) {
    if (!imageElementRef.current) return null;
    const rect = imageElementRef.current.getBoundingClientRect();
    const naturalWidth = imageElementRef.current.naturalWidth || 1;
    const naturalHeight = imageElementRef.current.naturalHeight || 1;

    const scaleX = naturalWidth / rect.width;
    const scaleY = naturalHeight / rect.height;

    const x = Math.max(0, Math.min(naturalWidth, (event.clientX - rect.left) * scaleX));
    const y = Math.max(0, Math.min(naturalHeight, (event.clientY - rect.top) * scaleY));

    return [Math.round(x), Math.round(y)];
  }

  function handleMouseDown(event) {
    if (!drawingMode) return;
    const pt = getCanvasCoords(event);
    if (!pt) return;
    setDragStart(pt);
    setCurrentDragBox([pt[0], pt[1], pt[0], pt[1]]);
  }

  function handleMouseMove(event) {
    if (!drawingMode || !dragStart) return;
    const pt = getCanvasCoords(event);
    if (!pt) return;
    setCurrentDragBox([
      Math.min(dragStart[0], pt[0]),
      Math.min(dragStart[1], pt[1]),
      Math.max(dragStart[0], pt[0]),
      Math.max(dragStart[1], pt[1]),
    ]);
  }

  function handleMouseUp() {
    if (!drawingMode || !currentDragBox) {
      setDragStart(null);
      setCurrentDragBox(null);
      return;
    }
    const [x1, y1, x2, y2] = currentDragBox;
    // Discard tiny clicks
    if (x2 - x1 > 8 && y2 - y1 > 8) {
      const newBox = {
        id: `manual_${Date.now()}`,
        box: [x1, y1, x2, y2],
        label: "Custom User Redaction",
      };
      setManualBoxes((prev) => [...prev, newBox]);
    }
    setDragStart(null);
    setCurrentDragBox(null);
  }

  function removeManualBox(id) {
    setManualBoxes((prev) => prev.filter((b) => b.id !== id));
  }

  // Export Redacted Image via /redact Endpoint
  async function handleExportRedacted() {
    if (!file) return;

    const findings = result?.privacy?.findings ?? [];
    const boxesToRedact = [];

    // Add selected AI detected boxes
    selectedIndices.forEach((idx) => {
      const f = findings[idx];
      if (f?.box && Array.isArray(f.box) && f.box.length === 4) {
        boxesToRedact.push(f.box);
      }
    });

    // Add manual custom drawn boxes
    manualBoxes.forEach((mb) => {
      if (mb.box && Array.isArray(mb.box) && mb.box.length === 4) {
        boxesToRedact.push(mb.box);
      }
    });

    if (boxesToRedact.length === 0) {
      setError("Please select at least one region to redact.");
      return;
    }

    setRedacting(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("boxes", JSON.stringify(boxesToRedact));
    formData.append("margin", "4");

    try {
      const response = await fetch(`${API_BASE}/redact`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Redaction export failed with HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `privacylens_protected_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
    } catch (err) {
      setError(err.message || "Failed to export redacted image.");
    } finally {
      setRedacting(false);
    }
  }

  const findings = result?.privacy?.findings ?? [];
  const exposure = result?.exposure ?? null;
  const metadata = result?.metadata ?? null;

  // Active detected boxes for image overlays
  const activeDetectedBoxes = findings
    .map((finding, idx) => ({ finding, idx, box: finding.box }))
    .filter((item) => item.box && Array.isArray(item.box) && item.box.length === 4);

  const imgWidth = result?.image_size?.width || imageDims.width;
  const imgHeight = result?.image_size?.height || imageDims.height;

  return (
    <div className="scanner-app-page">
      {/* App Subheader */}
      <div className="app-topbar">
        <div className="app-topbar-inner">
          <div className="app-topbar-title">
            <Shield size={20} className="text-cyan" />
            <h2>AI Privacy Scanner Workspace</h2>
          </div>

          <div className="demo-picker">
            <span className="demo-picker-label">⚡ Judge Quick Demos:</span>
            <div className="demo-chips">
              <button
                type="button"
                className="demo-chip-btn"
                onClick={() => loadDemoImage("/samples/demo_delivery.png", "01_delivery_label.png")}
              >
                📦 Demo 1: Delivery PII
              </button>
              <button
                type="button"
                className="demo-chip-btn"
                onClick={() => loadDemoImage("/samples/demo_composite.png", "12_multi_exposure_composite.png")}
              >
                🏫 Demo 2: Uniform & Transit Mosaic
              </button>
              <button
                type="button"
                className="demo-chip-btn"
                onClick={() => loadDemoImage("/samples/demo_credentials.png", "06_api_credentials.png")}
              >
                🔑 Demo 3: API & Secrets
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <main className="scanner-workspace-container">
        {/* Left Column: Visual Canvas & Viewport */}
        <section className="viewport-panel">
          <div className="panel-toolbar">
            <div className="toolbar-left">
              <span className="toolbar-label">
                {preview ? "1. Visual Inspection & Redaction Canvas" : "1. Select or Drop Image"}
              </span>
            </div>

            {preview && (
              <div className="toolbar-controls">
                <button
                  type="button"
                  className={`view-mode-btn ${previewMode === "inspect" ? "active" : ""}`}
                  onClick={() => setPreviewMode("inspect")}
                  title="View detected clues and highlights"
                >
                  <Eye size={15} />
                  <span>Highlights</span>
                </button>
                <button
                  type="button"
                  className={`view-mode-btn ${previewMode === "redacted" ? "active" : ""}`}
                  onClick={() => setPreviewMode("redacted")}
                  title="Preview solid opaque blackouts"
                >
                  <EyeOff size={15} />
                  <span>Redacted Preview</span>
                </button>

                <div className="zoom-controls">
                  <button
                    type="button"
                    onClick={() => setZoomLevel((z) => Math.max(0.5, z - 0.25))}
                    title="Zoom out"
                  >
                    <ZoomOut size={14} />
                  </button>
                  <span className="zoom-value">{Math.round(zoomLevel * 100)}%</span>
                  <button
                    type="button"
                    onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.25))}
                    title="Zoom in"
                  >
                    <ZoomIn size={14} />
                  </button>
                  <button
                    type="button"
                    onClick={() => setZoomLevel(1)}
                    title="Fit to canvas"
                  >
                    <Maximize2 size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Canvas Area */}
          <div className="canvas-wrapper">
            {preview ? (
              <div
                className={`canvas-inner ${drawingMode ? "is-drawing" : ""}`}
                ref={imageContainerRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                style={{ transform: `scale(${zoomLevel})`, transformOrigin: "top left" }}
              >
                <img
                  ref={imageElementRef}
                  src={preview}
                  alt="Subject under inspection"
                  className="canvas-image"
                  onLoad={(e) => {
                    const nw = e.currentTarget.naturalWidth || 1;
                    const nh = e.currentTarget.naturalHeight || 1;
                    setImageDims({ width: nw, height: nh });
                  }}
                />

                {/* Overlays in Inspection Mode */}
                {previewMode === "inspect" && showBoxes && (
                  <div className="canvas-overlay-layer">
                    {activeDetectedBoxes.map(({ finding, idx, box }) => {
                      const isSelected = selectedIndices.has(idx);
                      const isFocused = focusedIndex === idx;
                      const leftPct = (box[0] / imgWidth) * 100;
                      const topPct = (box[1] / imgHeight) * 100;
                      const widthPct = ((box[2] - box[0]) / imgWidth) * 100;
                      const heightPct = ((box[3] - box[1]) / imgHeight) * 100;
                      const severity = finding.severity || "review";

                      return (
                        <div
                          key={idx}
                          className={`box-marker marker-${severity} ${isSelected ? "is-selected" : "is-deselected"} ${isFocused ? "is-focused" : ""}`}
                          style={{
                            left: `${leftPct}%`,
                            top: `${topPct}%`,
                            width: `${widthPct}%`,
                            height: `${heightPct}%`,
                          }}
                          onClick={() => {
                            toggleFindingRedaction(idx);
                            setFocusedIndex(idx);
                          }}
                          title={`${finding.category} (${severity}) - Click to toggle redaction`}
                        >
                          <span className="marker-badge">
                            {finding.category}
                          </span>
                        </div>
                      );
                    })}

                    {/* Manual User Added Boxes */}
                    {manualBoxes.map((mb) => {
                      const [x1, y1, x2, y2] = mb.box;
                      return (
                        <div
                          key={mb.id}
                          className="box-marker marker-manual is-selected"
                          style={{
                            left: `${(x1 / imgWidth) * 100}%`,
                            top: `${(y1 / imgHeight) * 100}%`,
                            width: `${((x2 - x1) / imgWidth) * 100}%`,
                            height: `${((y2 - y1) / imgHeight) * 100}%`,
                          }}
                        >
                          <span className="marker-badge">
                            Custom
                            <button
                              type="button"
                              className="manual-delete-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                removeManualBox(mb.id);
                              }}
                              title="Remove custom box"
                              style={{ background: "transparent", border: "none", color: "#f87171", marginLeft: 4, cursor: "pointer" }}
                            >
                              <X size={10} />
                            </button>
                          </span>
                        </div>
                      );
                    })}

                    {/* Active Dragging Rectangle */}
                    {currentDragBox && (
                      <div
                        className="box-drawing-rect"
                        style={{
                          left: `${(currentDragBox[0] / imgWidth) * 100}%`,
                          top: `${(currentDragBox[1] / imgHeight) * 100}%`,
                          width: `${((currentDragBox[2] - currentDragBox[0]) / imgWidth) * 100}%`,
                          height: `${((currentDragBox[3] - currentDragBox[1]) / imgHeight) * 100}%`,
                        }}
                      />
                    )}
                  </div>
                )}

                {/* Overlays in Solid Redacted Mode */}
                {previewMode === "redacted" && (
                  <div className="canvas-overlay-layer">
                    {activeDetectedBoxes
                      .filter(({ idx }) => selectedIndices.has(idx))
                      .map(({ idx, box }) => {
                        const leftPct = (box[0] / imgWidth) * 100;
                        const topPct = (box[1] / imgHeight) * 100;
                        const widthPct = ((box[2] - box[0]) / imgWidth) * 100;
                        const heightPct = ((box[3] - box[1]) / imgHeight) * 100;
                        return (
                          <div
                            key={idx}
                            className="solid-blackout-block"
                            style={{
                              left: `${leftPct}%`,
                              top: `${topPct}%`,
                              width: `${widthPct}%`,
                              height: `${heightPct}%`,
                            }}
                          />
                        );
                      })}

                    {manualBoxes.map((mb) => {
                      const [x1, y1, x2, y2] = mb.box;
                      return (
                        <div
                          key={mb.id}
                          className="solid-blackout-block"
                          style={{
                            left: `${(x1 / imgWidth) * 100}%`,
                            top: `${(y1 / imgHeight) * 100}%`,
                            width: `${((x2 - x1) / imgWidth) * 100}%`,
                            height: `${((y2 - y1) / imgHeight) * 100}%`,
                          }}
                        />
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              <label className="dropzone-area">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={handleFileChange}
                />
                <div className="dropzone-body">
                  <div className="dropzone-icon">
                    <Upload size={32} />
                  </div>
                  <h3>Select or Drop a Photo</h3>
                  <p>PNG, JPEG, WebP up to 10 MB. Local CPU inference ensures images remain private.</p>
                  <div className="dropzone-formats">
                    <span>Delivery Slips</span> · <span>Student Passes</span> · <span>School Photos</span> · <span>Screenshots</span>
                  </div>
                </div>
              </label>
            )}
          </div>

          {/* Canvas Bottom Action Bar */}
          {preview && (
            <div className="canvas-footer">
              <div className="canvas-footer-left">
                <button
                  type="button"
                  className={`draw-toggle-btn ${drawingMode ? "active" : ""}`}
                  onClick={() => setDrawingMode(!drawingMode)}
                >
                  ✏️ {drawingMode ? "Click & Drag to Draw (Active)" : "Add Custom Box"}
                </button>

                <button
                  type="button"
                  className="toggle-boxes-btn"
                  onClick={() => setShowBoxes(!showBoxes)}
                >
                  <Layers size={14} />
                  <span>{showBoxes ? "Hide Boxes" : "Show Boxes"}</span>
                </button>

                <label className="change-img-label">
                  📁 Replace Image
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    onChange={handleFileChange}
                    style={{ display: "none" }}
                  />
                </label>
              </div>

              {manualBoxes.length > 0 && (
                <div className="manual-boxes-summary">
                  <span>{manualBoxes.length} Custom Box(es)</span>
                  <button
                    type="button"
                    className="clear-manual-btn"
                    onClick={() => setManualBoxes([])}
                  >
                    Clear Custom
                  </button>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Right Column: Scan Config, Exposure Reconstruction & Findings */}
        <section className="results-panel">
          {/* Scan Options Card */}
          <div className="scan-config-card">
            <div className="config-header">
              <Scan size={18} className="text-cyan" />
              <h3>Scan Configuration</h3>
            </div>

            <div className="scan-mode-tabs">
              <button
                type="button"
                className={`scan-tab ${scanMode === "fast" ? "active" : ""}`}
                onClick={() => setScanMode("fast")}
              >
                <div className="tab-title">⚡ Fast Scan</div>
                <div className="tab-desc">PaddleOCR + CV (~2-3s)</div>
              </button>
              <button
                type="button"
                className={`scan-tab ${scanMode === "comprehensive" ? "active" : ""}`}
                onClick={() => setScanMode("comprehensive")}
              >
                <div className="tab-title">🔍 Deep Scan</div>
                <div className="tab-desc">Florence-2 + PaddleOCR (~5-8s)</div>
              </button>
            </div>

            <button
              type="button"
              className="run-scan-btn"
              onClick={handleAnalyze}
              disabled={!file || loading}
            >
              {loading ? (
                <div className="btn-loading-state">
                  <span className="spinner" />
                  <span>{loadingPhase || "Analyzing with AI..."}</span>
                </div>
              ) : (
                <div className="btn-content">
                  <Shield size={18} />
                  <span>{result ? "Re-Scan Image" : "Scan for Privacy Exposure"}</span>
                </div>
              )}
            </button>

            {metadata && (
              <div className="perf-summary-pill">
                <span>⚡ Analyzed in <strong>{metadata.execution_time_ms} ms</strong></span>
                <span className="sep">•</span>
                <span>Engine: <strong>{metadata.ocr_engine === "paddleocr" ? "PaddleOCR PP-OCRv4" : metadata.ocr_engine}</strong></span>
              </div>
            )}
          </div>

          {error && (
            <div className="error-alert">
              <AlertTriangle size={18} />
              <span>{error}</span>
            </div>
          )}

          {/* AI Exposure Reconstruction Card (USP) */}
          {exposure && (
            <div className="exposure-synthesis-card">
              <div className="exposure-head">
                <div className="head-icon">
                  <Sparkles size={20} className="text-violet" />
                </div>
                <div>
                  <div className="exposure-badge">CORE USP: THE MOSAIC EFFECT</div>
                  <h4>AI Exposure Reconstruction</h4>
                </div>
                <span className={`risk-tag risk-${exposure.exposure_risk?.toLowerCase() || "medium"}`}>
                  {exposure.exposure_risk?.toUpperCase() || "REVIEW"} RISK
                </span>
              </div>

              <p className="exposure-narrative">
                {exposure.exposure_narrative || "Multiple observed privacy clues combine to create identifiable exposure."}
              </p>

              {/* Multi-clue Exposure Scenarios */}
              {exposure.scenarios && exposure.scenarios.length > 0 && (
                <div className="exposure-scenarios-list">
                  <div className="scenarios-title">Converging Privacy Scenarios:</div>
                  {exposure.scenarios.map((sc, scIdx) => (
                    <div key={scIdx} className="scenario-item">
                      <div className="scenario-item-head">
                        <AlertTriangle size={14} className="text-amber" />
                        <strong>{sc.title}</strong>
                        <span className={`sc-badge sc-${sc.severity}`}>{sc.severity}</span>
                      </div>
                      <p className="scenario-desc">{sc.description}</p>
                      {sc.contributing_clues && (
                        <div className="contributing-clues">
                          <span>Linked Clues:</span>
                          {sc.contributing_clues.map((clue, cIdx) => (
                            <span key={cIdx} className="clue-tag">{clue}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {exposure.recommendations && exposure.recommendations.length > 0 && (
                <div className="exposure-recommendations">
                  <strong>Safety Actions:</strong>
                  <ul>
                    {exposure.recommendations.map((rec, rIdx) => (
                      <li key={rIdx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Findings List Section */}
          {result && (
            <div className="findings-section">
              <div className="findings-header">
                <div>
                  <h4>Detected Privacy Clues</h4>
                  <span className="findings-subtitle">
                    {findings.length} item(s) found across 15 categories
                  </span>
                </div>

                {findings.length > 0 && (
                  <div className="selection-actions">
                    <button
                      type="button"
                      className="select-action-btn"
                      onClick={() => toggleSelectAll(true)}
                    >
                      Select All
                    </button>
                    <button
                      type="button"
                      className="select-action-btn"
                      onClick={() => toggleSelectAll(false)}
                    >
                      Deselect
                    </button>
                  </div>
                )}
              </div>

              {findings.length === 0 ? (
                <div className="empty-findings">
                  <CheckCircle2 size={32} className="text-emerald" />
                  <h5>No High-Risk Sensitive Patterns Detected</h5>
                  <p>Our scanners did not detect clear PII, credentials, or metadata in this scan. Review your image visually before sharing.</p>
                </div>
              ) : (
                <div className="findings-scroll-list">
                  {findings.map((f, idx) => {
                    const isSelected = selectedIndices.has(idx);
                    const isFocused = focusedIndex === idx;
                    const severity = f.severity || "review";

                    return (
                      <div
                        key={idx}
                        className={`finding-card finding-${severity} ${isSelected ? "selected" : ""} ${isFocused ? "focused" : ""}`}
                        onClick={() => {
                          toggleFindingRedaction(idx);
                          setFocusedIndex(idx);
                        }}
                      >
                        <div className="finding-card-top">
                          <label className="checkbox-wrap" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => toggleFindingRedaction(idx)}
                            />
                            <span className="custom-checkmark" />
                          </label>

                          <div className="finding-meta">
                            <span className="finding-category">{f.category}</span>
                            <span className={`finding-severity sev-${severity}`}>{severity}</span>
                          </div>
                        </div>

                        <p className="finding-explanation">{f.explanation}</p>

                        {f.recommendation && (
                          <div className="finding-rec">
                            <strong>Action:</strong> {f.recommendation}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Redaction Export Bar */}
              <div className="export-action-card">
                <div className="export-status-info">
                  <div className="status-count">
                    <strong>{selectedIndices.size + manualBoxes.length}</strong> regions ready for solid opaque redaction
                  </div>
                  <div className="status-note">
                    Stripping embedded GPS coordinates & EXIF tags permanently.
                  </div>
                </div>

                <button
                  type="button"
                  className="btn-download-redacted"
                  onClick={handleExportRedacted}
                  disabled={redacting || (selectedIndices.size === 0 && manualBoxes.length === 0)}
                >
                  <Download size={18} />
                  <span>{redacting ? "Applying Solid Blackout..." : "Download Protected Image (Strip EXIF)"}</span>
                </button>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
