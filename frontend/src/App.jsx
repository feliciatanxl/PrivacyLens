import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Redaction state
  const [selectedIndices, setSelectedIndices] = useState(new Set());
  const [manualBoxes, setManualBoxes] = useState([]);
  const [previewMode, setPreviewMode] = useState("inspect"); // 'inspect' | 'redacted'
  const [drawingMode, setDrawingMode] = useState(false);
  const [dragStart, setDragStart] = useState(null);
  const [currentDragBox, setCurrentDragBox] = useState(null);
  const [focusedIndex, setFocusedIndex] = useState(null);
  const [redacting, setRedacting] = useState(false);

  const imageContainerRef = useRef(null);
  const imageElementRef = useRef(null);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
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

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setSelectedIndices(new Set());
    setManualBoxes([]);
    setPreviewMode("inspect");
    setDrawingMode(false);
    setError("");
    setFocusedIndex(null);
  }

  async function handleAnalyze() {
    if (!file) return;

    setLoading(true);
    setError("");
    setResult(null);
    setFocusedIndex(null);

    const formData = new FormData();
    formData.append("file", file);

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

      // Default: select all findings with valid bounding boxes for redaction
      const findings = data?.privacy?.findings ?? [];
      const initialSelected = new Set();
      findings.forEach((f, idx) => {
        if (f.box && Array.isArray(f.box) && f.box.length === 4) {
          initialSelected.add(idx);
        }
      });
      setSelectedIndices(initialSelected);
    } catch (err) {
      setError(err.message || "Something went wrong communicating with the server.");
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

  // Manual Box Drawing
  function getImageCoords(e) {
    const img = imageElementRef.current;
    if (!img) return null;
    const rect = img.getBoundingClientRect();
    const clientX = e.clientX ?? (e.touches && e.touches[0]?.clientX);
    const clientY = e.clientY ?? (e.touches && e.touches[0]?.clientY);

    const relX = Math.max(0, Math.min(rect.width, clientX - rect.left));
    const relY = Math.max(0, Math.min(rect.height, clientY - rect.top));

    const scaleX = (result?.image_size?.width || img.naturalWidth) / rect.width;
    const scaleY = (result?.image_size?.height || img.naturalHeight) / rect.height;

    return {
      x: Math.round(relX * scaleX),
      y: Math.round(relY * scaleY),
      relX,
      relY,
      rectWidth: rect.width,
      rectHeight: rect.height,
    };
  }

  function handleMouseDown(e) {
    if (!drawingMode) return;
    const coords = getImageCoords(e);
    if (!coords) return;
    setDragStart(coords);
    setCurrentDragBox([coords.x, coords.y, coords.x, coords.y]);
  }

  function handleMouseMove(e) {
    if (!drawingMode || !dragStart) return;
    const coords = getImageCoords(e);
    if (!coords) return;
    setCurrentDragBox([
      Math.min(dragStart.x, coords.x),
      Math.min(dragStart.y, coords.y),
      Math.max(dragStart.x, coords.x),
      Math.max(dragStart.y, coords.y),
    ]);
  }

  function handleMouseUp() {
    if (!drawingMode || !dragStart || !currentDragBox) return;
    const [x1, y1, x2, y2] = currentDragBox;
    if (Math.abs(x2 - x1) > 10 && Math.abs(y2 - y1) > 10) {
      setManualBoxes((prev) => [
        ...prev,
        {
          id: Date.now(),
          box: [x1, y1, x2, y2],
          category: "Manual Redaction Area",
          severity: "manual",
        },
      ]);
    }
    setDragStart(null);
    setCurrentDragBox(null);
  }

  function removeManualBox(id) {
    setManualBoxes((prev) => prev.filter((b) => b.id !== id));
  }

  // Export Redacted Image
  async function handleExportRedacted() {
    if (!file) return;
    setRedacting(true);

    const findings = result?.privacy?.findings ?? [];
    const boxesToRedact = [];

    selectedIndices.forEach((idx) => {
      const box = findings[idx]?.box;
      if (box && Array.isArray(box)) {
        boxesToRedact.push(box);
      }
    });

    manualBoxes.forEach((mb) => {
      if (mb.box && Array.isArray(mb.box)) {
        boxesToRedact.push(mb.box);
      }
    });

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("boxes", JSON.stringify(boxesToRedact));
      formData.append("margin", "4");

      const res = await fetch(`${API_BASE}/redact`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Redaction service returned error " + res.status);
      }

      const blob = await res.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `privacylens_protected_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError("Failed to export redacted image: " + err.message);
    } finally {
      setRedacting(false);
    }
  }

  const findings = result?.privacy?.findings ?? [];
  const exposure = result?.exposure;
  const imgWidth = result?.image_size?.width || 1;
  const imgHeight = result?.image_size?.height || 1;

  // Active boxes to display
  const activeDetectedBoxes = findings
    .map((f, idx) => ({ finding: f, idx, box: f.box }))
    .filter((item) => item.box && Array.isArray(item.box) && item.box.length === 4);

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-icon">◈</div>
          <div>
            <span className="brand-name">PrivacyLens</span>
            <span className="brand-sub">Spot It! Stop It!</span>
          </div>
        </div>

        <div className="header-badges">
          <span className="header-pill">AI Privacy Companion</span>
          <span className="header-badge">Florence-2 + Multi-CV</span>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <span className="eyebrow">SET BOUNDARIES ONLINE</span>
          <h1>
            See what you're <span>really sharing</span> before you post.
          </h1>
          <p>
            Benign photos and screenshots often reveal sensitive school badges, addresses, contact
            details, and credentials. PrivacyLens detects 15 privacy vectors, reconstructs
            composite exposure risks, and redacts sensitive areas with a single click.
          </p>
        </section>

        <div className="workspace">
          {/* Left Panel: Upload, Interactive Canvas & Redaction Controls */}
          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>1. Upload & Inspect Photo</h2>
                <p>Interactive bounding box inspection & manual redaction</p>
              </div>

              {preview && (
                <div className="view-toggle">
                  <button
                    className={`toggle-btn ${previewMode === "inspect" ? "active" : ""}`}
                    onClick={() => setPreviewMode("inspect")}
                  >
                    🔍 Highlights
                  </button>
                  <button
                    className={`toggle-btn ${previewMode === "redacted" ? "active" : ""}`}
                    onClick={() => setPreviewMode("redacted")}
                  >
                    🛡️ Redacted
                  </button>
                </div>
              )}
            </div>

            {preview ? (
              <div className="image-viewport-wrapper">
                <div
                  className={`image-canvas-container ${drawingMode ? "drawing" : ""}`}
                  ref={imageContainerRef}
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                >
                  <img
                    ref={imageElementRef}
                    src={preview}
                    alt="Uploaded subject"
                    className="viewport-img"
                  />

                  {/* Overlays in Inspection Mode */}
                  {previewMode === "inspect" && (
                    <div className="box-overlay-layer">
                      {activeDetectedBoxes.map(({ finding, idx, box }) => {
                        const isSelected = selectedIndices.has(idx);
                        const isFocused = focusedIndex === idx;
                        const leftPct = (box[0] / imgWidth) * 100;
                        const topPct = (box[1] / imgHeight) * 100;
                        const widthPct = ((box[2] - box[0]) / imgWidth) * 100;
                        const heightPct = ((box[3] - box[1]) / imgHeight) * 100;
                        const isHigh = finding.severity === "high" || finding.severity === "critical";

                        return (
                          <div
                            key={idx}
                            className={`detection-box ${isHigh ? "box-high" : "box-review"} ${
                              isSelected ? "box-selected" : "box-deselected"
                            } ${isFocused ? "box-focused" : ""}`}
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
                          >
                            <span className="box-pill">
                              {finding.category}
                              {isSelected ? " ✓" : ""}
                            </span>
                          </div>
                        );
                      })}

                      {/* Manual Boxes */}
                      {manualBoxes.map((mb) => {
                        const [x1, y1, x2, y2] = mb.box;
                        const leftPct = (x1 / imgWidth) * 100;
                        const topPct = (y1 / imgHeight) * 100;
                        const widthPct = ((x2 - x1) / imgWidth) * 100;
                        const heightPct = ((y2 - y1) / imgHeight) * 100;

                        return (
                          <div
                            key={mb.id}
                            className="detection-box box-manual"
                            style={{
                              left: `${leftPct}%`,
                              top: `${topPct}%`,
                              width: `${widthPct}%`,
                              height: `${heightPct}%`,
                            }}
                          >
                            <span className="box-pill manual-pill">Manual Redaction</span>
                          </div>
                        );
                      })}

                      {/* Dragging rectangle indicator */}
                      {currentDragBox && (
                        <div
                          className="detection-box box-drag"
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

                  {/* Solid Opaque Redaction Overlays in Protected Preview Mode */}
                  {previewMode === "redacted" && (
                    <div className="box-overlay-layer">
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
                              className="solid-redaction-block"
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
                            className="solid-redaction-block"
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

                <div className="canvas-controls">
                  <button
                    className={`control-chip ${drawingMode ? "chip-active" : ""}`}
                    onClick={() => setDrawingMode(!drawingMode)}
                  >
                    ✏️ {drawingMode ? "Click & Drag to Draw (Active)" : "Add Custom Box"}
                  </button>

                  <label className="control-chip change-file-chip">
                    📁 Choose Another Image
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp"
                      onChange={handleFileChange}
                      style={{ display: "none" }}
                    />
                  </label>
                </div>
              </div>
            ) : (
              <label className="upload-area">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={handleFileChange}
                />
                <div className="upload-placeholder">
                  <div className="upload-icon">↑</div>
                  <h3>Select or Drop a Photo</h3>
                  <p>Screenshots, student passes, documents, or social posts (PNG/JPEG up to 10MB)</p>
                </div>
              </label>
            )}

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={!file || loading}
            >
              {loading ? "Scanning 15 Privacy Categories with AI..." : "Scan for Privacy Exposure"}
            </button>

            {/* Redaction Export Actions */}
            {result && (
              <div className="redaction-export-bar">
                <div className="export-status">
                  <strong>{selectedIndices.size + manualBoxes.length}</strong> regions selected for
                  redaction
                </div>
                <button
                  className="export-button"
                  onClick={handleExportRedacted}
                  disabled={redacting || (selectedIndices.size === 0 && manualBoxes.length === 0)}
                >
                  {redacting ? "Exporting Protected Image..." : "🛡️ Download Redacted Image (Strip EXIF)"}
                </button>
              </div>
            )}

            {error && <div className="error">{error}</div>}

            <div className="privacy-note">
              🔒 <strong>On-Device Privacy First:</strong> Analysis runs locally. Redaction applies
              solid opaque blackouts and permanently removes all embedded GPS coordinates & EXIF
              metadata.
            </div>
          </section>

          {/* Right Panel: Exposure Reconstruction (USP) & Findings */}
          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>2. AI Exposure Reconstruction</h2>
                <p>Composite risk synthesis & sensitive clue breakdown</p>
              </div>

              {result && (
                <span className="result-count">
                  {findings.length} Clues Detected
                </span>
              )}
            </div>

            {!result && !loading && (
              <div className="empty-state">
                <div className="empty-icon">◎</div>
                <h3>Ready to Scan</h3>
                <p>
                  Upload an image and run the privacy scan to discover sensitive clues, examine
                  routine exposure, and redact vulnerable details.
                </p>
              </div>
            )}

            {loading && (
              <div className="empty-state">
                <div className="spinner" />
                <h3>Analyzing Image Across 15 Categories...</h3>
                <p>
                  Florence-2 OCR, Haar face cascades, QR decoders, and EXIF inspectors are auditing
                  this photo.
                </p>
              </div>
            )}

            {result && (
              <div className="results">
                {/* Core USP: Exposure Reconstruction Panel */}
                {exposure && (
                  <div className={`exposure-card exposure-${exposure.risk_level}`}>
                    <div className="exposure-top">
                      <span className="exposure-eyebrow">AI EXPOSURE RECONSTRUCTION (USP)</span>
                      <span className={`risk-badge risk-${exposure.risk_level}`}>
                        {exposure.risk_level.toUpperCase()} RISK
                      </span>
                    </div>

                    <h3 className="exposure-summary-title">{exposure.summary}</h3>

                    {/* Scenarios */}
                    {exposure.exposure_scenarios && exposure.exposure_scenarios.length > 0 && (
                      <div className="scenarios-list">
                        <h4>Composite Exposure Scenarios (The Mosaic Effect)</h4>
                        {exposure.exposure_scenarios.map((scen, sIdx) => (
                          <div className="scenario-item" key={sIdx}>
                            <div className="scenario-header">
                              <span className="scenario-dot">⚠️</span>
                              <strong>{scen.title}</strong>
                            </div>
                            <p className="scenario-evidence">
                              <strong>Visible Evidence:</strong> {scen.visible_evidence}
                            </p>
                            <p className="scenario-inference">
                              <strong>Potential Risk:</strong> {scen.potential_inference}
                            </p>
                            <p className="scenario-guidance">
                              <strong>Youth Guidance:</strong> {scen.educational_guidance}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Actionable Recommendations */}
                    {exposure.actionable_recommendations && (
                      <div className="recommendations-box">
                        <h4>Recommended Boundaries & Redactions:</h4>
                        <ul>
                          {exposure.actionable_recommendations.map((rec, rIdx) => (
                            <li key={rIdx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Findings List with Redaction Checkboxes */}
                <div className="findings-section-header">
                  <h3>Detected Sensitive Clues</h3>
                  <div className="select-all-group">
                    <button className="text-btn" onClick={() => toggleSelectAll(true)}>
                      Select All
                    </button>
                    <span>·</span>
                    <button className="text-btn" onClick={() => toggleSelectAll(false)}>
                      Deselect All
                    </button>
                  </div>
                </div>

                {findings.map((finding, index) => {
                  const hasBox = finding.box && Array.isArray(finding.box);
                  const isSelected = selectedIndices.has(index);
                  const isFocused = focusedIndex === index;
                  const isHigh = finding.severity === "high" || finding.severity === "critical";

                  return (
                    <div
                      className={`finding-card ${isHigh ? "finding-high" : "finding-review"} ${
                        isFocused ? "card-focused" : ""
                      }`}
                      key={index}
                      onClick={() => setFocusedIndex(index)}
                    >
                      <div className="finding-top">
                        <div className="finding-title-row">
                          {hasBox && (
                            <input
                              type="checkbox"
                              className="redact-checkbox"
                              checked={isSelected}
                              onChange={(e) => {
                                e.stopPropagation();
                                toggleFindingRedaction(index);
                              }}
                              title="Toggle redaction for this finding"
                            />
                          )}
                          <h4>{finding.category}</h4>
                        </div>

                        <div className="finding-badges">
                          <span className="source-pill">{finding.source}</span>
                          <span className={`severity ${isHigh ? "sev-high" : "sev-review"}`}>
                            {finding.severity}
                          </span>
                        </div>
                      </div>

                      <p className="finding-explanation">{finding.explanation}</p>
                      <div className="recommendation">👉 {finding.recommendation}</div>
                    </div>
                  );
                })}

                {/* Manual Box Cards */}
                {manualBoxes.map((mb) => (
                  <div className="finding-card finding-manual" key={mb.id}>
                    <div className="finding-top">
                      <div className="finding-title-row">
                        <input type="checkbox" checked={true} readOnly className="redact-checkbox" />
                        <h4>Custom Redaction Box</h4>
                      </div>
                      <button
                        className="delete-manual-btn"
                        onClick={() => removeManualBox(mb.id)}
                        title="Delete manual box"
                      >
                        ✕ Remove
                      </button>
                    </div>
                    <p className="finding-explanation">
                      User-drawn custom area covering coordinates [{mb.box.join(", ")}].
                    </p>
                  </div>
                ))}

                {findings.length === 0 && (
                  <p className="no-findings">
                    No matching privacy risks detected. Always perform a manual visual check before
                    publishing images online.
                  </p>
                )}

                <div className="disclaimer-note">
                  {result.privacy?.disclaimer}
                </div>
              </div>
            )}
          </section>
        </div>

        <footer className="footer">
          PrivacyLens · Hackathon: Spot It! Stop It! · AI Privacy Protection &amp; Redaction MVP
        </footer>
      </main>
    </div>
  );
}
