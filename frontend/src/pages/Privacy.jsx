import { Link } from "react-router-dom";
import { Cpu, AlertCircle, CheckCircle2, ArrowRight } from "lucide-react";

export default function Privacy() {
  return (
    <div className="info-page">
      <div className="info-hero">
        <div className="info-hero-container">
          <span className="info-eyebrow">TRANSPARENCY & ETHICS</span>
          <h1 className="info-title">Privacy, Security & Limitations</h1>
          <p className="info-subtitle">
            How we handle your image data, why local execution matters, and what our AI model can and cannot do.
          </p>
        </div>
      </div>

      <div className="info-content-container">
        {/* Local Processing Guarantee */}
        <section className="info-section">
          <div className="info-card">
            <div className="info-card-header">
              <Cpu className="text-cyan" size={24} />
              <h2>Local-First AI Execution</h2>
            </div>
            <p>
              When dealing with sensitive personal information, credentials, and family photos, sending data to remote third-party cloud servers introduces unnecessary security risks.
            </p>
            <div className="principles-grid">
              <div className="principle-item">
                <CheckCircle2 size={20} className="text-emerald" />
                <div>
                  <h4>Zero Remote Cloud Relaying</h4>
                  <p>In this MVP setup, all machine learning inference runs directly on your local CPU instance.</p>
                </div>
              </div>
              <div className="principle-item">
                <CheckCircle2 size={20} className="text-emerald" />
                <div>
                  <h4>Ephemeral In-Memory Handling</h4>
                  <p>Images uploaded to the scanner are processed in memory and are never written to permanent disk or database storage.</p>
                </div>
              </div>
              <div className="principle-item">
                <CheckCircle2 size={20} className="text-emerald" />
                <div>
                  <h4>Zero Secret Logging</h4>
                  <p>Our detector logging protocols strictly omit raw passwords, API keys, and national identifiers from console output.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Responsible AI & Known Limitations */}
        <section className="info-section" id="limitations">
          <div className="info-card">
            <div className="info-card-header">
              <AlertCircle className="text-amber" size={24} />
              <h2>Model Limitations & Responsible AI</h2>
            </div>
            <p>
              We believe in honest, transparent disclosure about AI capabilities. No computer vision or OCR system is infallible:
            </p>
            <ul className="limitations-list">
              <li>
                <strong>Image Quality & Compression:</strong> Heavy compression, extreme blur, or artistic filters can degrade OCR transcription accuracy.
              </li>
              <li>
                <strong>Handwriting & Unusual Fonts:</strong> Cursive or stylized artistic handwriting may not be recognized as reliably as printed typography.
              </li>
              <li>
                <strong>Contextual Interpretation:</strong> AI Exposure Reconstruction offers plausible inference scenarios, not definitive proof of real-world tracking.
              </li>
              <li>
                <strong>Human Review is Indispensable:</strong> PrivacyLens is an awareness tool and protective aid. Users should always review the redacted preview before sharing.
              </li>
            </ul>
          </div>
        </section>

        {/* Prototype Disclaimer */}
        <section className="info-section">
          <div className="info-card disclaimer-card">
            <h3>Hackathon Prototype Context</h3>
            <p>
              PrivacyLens was developed for the <strong>Spot It! Stop It! Hackathon</strong> addressing <em>Problem Statement 01: Set Boundaries Online</em>. It is designed to spark youth privacy literacy and provide immediate, practical self-defense tools.
            </p>
            <div className="cta-inline">
              <Link to="/app" className="btn-primary-hero">
                <span>Open Scanner</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
