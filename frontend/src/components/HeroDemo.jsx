import { useState } from "react";
import { AlertTriangle, Eye, EyeOff, Sparkles, CheckCircle2 } from "lucide-react";

export default function HeroDemo() {
  const [isRedacted, setIsRedacted] = useState(false);
  const [activeClue, setActiveClue] = useState(null);

  const clues = [
    {
      id: "badge",
      title: "School Uniform Badge",
      category: "School badge / logo",
      risk: "High",
      box: { top: "18%", left: "28%", width: "16%", height: "18%" },
      explanation: "Identifies the specific educational institution attended.",
    },
    {
      id: "sign",
      title: "Street & Transit Sign",
      category: "Location clue",
      risk: "Review",
      box: { top: "12%", left: "68%", width: "24%", height: "20%" },
      explanation: "Exposes neighborhood transit corridor and bus route.",
    },
    {
      id: "schedule",
      title: "Class Schedule Sheet",
      category: "Timetable / routine",
      risk: "High",
      box: { top: "58%", left: "15%", width: "32%", height: "26%" },
      explanation: "Reveals recurring dismissal times and activity days.",
    },
    {
      id: "name",
      title: "Parcel Label with Name",
      category: "Personal name & phone",
      risk: "Critical",
      box: { top: "64%", left: "55%", width: "36%", height: "24%" },
      explanation: "Directly reveals individual identity and contact number.",
    },
  ];

  return (
    <div className="hero-demo-container">
      <div className="hero-demo-header">
        <div className="demo-header-left">
          <div className="demo-live-badge">
            <span className="live-dot" />
            <span>Interactive AI Demonstration</span>
          </div>
          <span className="demo-meta">Simulated Social Media Post Inspection</span>
        </div>

        <div className="demo-toggle-group">
          <button
            type="button"
            className={`demo-toggle-btn ${!isRedacted ? "active" : ""}`}
            onClick={() => setIsRedacted(false)}
          >
            <Eye size={15} />
            <span>AI Clue Detection</span>
          </button>
          <button
            type="button"
            className={`demo-toggle-btn ${isRedacted ? "active" : ""}`}
            onClick={() => setIsRedacted(true)}
          >
            <EyeOff size={15} />
            <span>Protected Redaction</span>
          </button>
        </div>
      </div>

      <div className="hero-demo-stage">
        {/* Synthetic Mock Post Viewport */}
        <div className="mock-canvas">
          <div className="mock-canvas-bg">
            <div className="scene-element street-backdrop">
              <span className="scene-label">BUS STOP 17099 · CLEMENTI AVE 3</span>
            </div>
            <div className="scene-element student-jersey">
              <span className="scene-badge">PE CREST</span>
            </div>
            <div className="scene-element desk-schedule">
              <span className="scene-text">FRIDAY · 3:30PM DISMISSAL</span>
            </div>
            <div className="scene-element delivery-slip">
              <span className="scene-text">JORDAN TAN · +65 9123 ••••</span>
            </div>
          </div>

          {/* Interactive Bounding Boxes or Solid Redactions */}
          {!isRedacted ? (
            <div className="demo-boxes-layer">
              {clues.map((clue) => {
                const isHovered = activeClue === clue.id;
                return (
                  <div
                    key={clue.id}
                    className={`demo-box ${clue.risk.toLowerCase()} ${isHovered ? "hovered" : ""}`}
                    style={clue.box}
                    onMouseEnter={() => setActiveClue(clue.id)}
                    onMouseLeave={() => setActiveClue(null)}
                  >
                    <div className="demo-box-tag">
                      <span className="tag-name">{clue.title}</span>
                      <span className={`tag-risk risk-${clue.risk.toLowerCase()}`}>
                        {clue.risk}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="demo-boxes-layer">
              {clues.map((clue) => (
                <div
                  key={clue.id}
                  className="demo-solid-block"
                  style={clue.box}
                >
                  <div className="redacted-stamp">
                    <CheckCircle2 size={12} />
                    <span>REDACTED</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mock-canvas-badge">
            {isRedacted ? "🛡️ Solid Opaque Blackout Applied (EXIF Metadata Stripped)" : "⚡ 4 Sensitive Vectors Detected via PaddleOCR + Florence-2"}
          </div>
        </div>

        {/* AI Exposure Reconstruction Card (USP) */}
        <div className="demo-exposure-card">
          <div className="exposure-card-top">
            <div className="exposure-icon-wrap">
              <Sparkles size={18} className="sparkle-cyan" />
            </div>
            <div>
              <span className="exposure-badge">CORE USP: THE MOSAIC EFFECT</span>
              <h4 className="exposure-title">AI Exposure Reconstruction</h4>
            </div>
          </div>

          <div className="exposure-convergence-flow">
            <div className="convergence-clues">
              {clues.map((c) => (
                <div
                  key={c.id}
                  className={`clue-chip ${activeClue === c.id ? "highlighted" : ""}`}
                  onMouseEnter={() => setActiveClue(c.id)}
                  onMouseLeave={() => setActiveClue(null)}
                >
                  <span className="chip-bullet">•</span>
                  <span>{c.title}</span>
                </div>
              ))}
            </div>

            <div className="convergence-arrow">
              <span className="arrow-line" />
              <span className="arrow-text">Synthesizes Into</span>
              <span className="arrow-line" />
            </div>

            <div className="synthesized-risk-box">
              <div className="risk-header">
                <AlertTriangle size={16} className="risk-warning-icon" />
                <strong>Composite Vulnerability Identified</strong>
              </div>
              <p className="risk-narrative">
                Individually, a school jersey or street sign may seem harmless. Together with a dismissal schedule and name, an observer can infer <strong>school affiliation, daily commute corridor, and recurring dismissal routine</strong>.
              </p>
              <div className="safety-advice">
                <strong>Safety Recommendation:</strong> Redact school insignia and background signage before uploading to public social platforms.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
