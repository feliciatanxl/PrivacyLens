import { Link } from "react-router-dom";
import {
  Scan,
  Sparkles,
  Lock,
  Layers,
  CheckCircle2,
  ArrowRight
} from "lucide-react";

export default function HowItWorks() {
  return (
    <div className="info-page">
      <div className="info-hero">
        <div className="info-hero-container">
          <span className="info-eyebrow">TECHNOLOGY & ARCHITECTURE</span>
          <h1 className="info-title">How PrivacyLens Works</h1>
          <p className="info-subtitle">
            An inside look at our multi-modal AI detection pipeline, on-device local execution, and the science behind AI Exposure Reconstruction.
          </p>
        </div>
      </div>

      <div className="info-content-container">
        {/* Section 1: The Mosaic Effect */}
        <section className="info-section" id="mosaic-effect">
          <div className="info-card">
            <div className="info-card-header">
              <Sparkles className="text-violet" size={24} />
              <h2>The Mosaic Effect in Everyday Photos</h2>
            </div>
            <p>
              In cybersecurity and privacy intelligence, <strong>The Mosaic Effect</strong> describes the phenomenon where disparate, seemingly innocuous pieces of information are gathered from multiple sources to create a complete, sensitive profile of an individual.
            </p>
            <p>
              When youths post photos on TikTok, Instagram, or Discord, they often check for obvious secrets (like bank cards or house keys) but overlook contextual clues:
            </p>
            <div className="mosaic-examples-grid">
              <div className="mosaic-card-item">
                <span className="item-icon">👕</span>
                <h4>Physical Attire</h4>
                <p>School PE uniforms, house colors, or CCA badges reveal school affiliation.</p>
              </div>
              <div className="mosaic-card-item">
                <span className="item-icon">🚏</span>
                <h4>Transit Corridors</h4>
                <p>Bus stop numbers, street signs, and MRT exits indicate neighborhood transit paths.</p>
              </div>
              <div className="mosaic-card-item">
                <span className="item-icon">📅</span>
                <h4>Visible Schedules</h4>
                <p>Tuition center timetables or study planners broadcast recurring dismissal times.</p>
              </div>
            </div>
            <div className="info-callout">
              <strong>The PrivacyLens Difference:</strong> Rather than just blurring a single badge, our AI Exposure Reconstruction engine explains to users how these clues connect and allows one-click defense across all converging points.
            </div>
          </div>
        </section>

        {/* Section 2: 15 Detection Categories */}
        <section className="info-section" id="15-categories">
          <div className="info-card">
            <div className="info-card-header">
              <Layers className="text-cyan" size={24} />
              <h2>The 15 Detection Categories</h2>
            </div>
            <p>
              PrivacyLens combines specialized optical character recognition, deep vision transformers, computer vision cascades, and cryptographic validators:
            </p>

            <div className="tech-table-wrap">
              <table className="tech-table">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Detection Engine</th>
                    <th>Why It Matters</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>School Uniforms</strong></td>
                    <td>Florence-2 Object Detection</td>
                    <td>Identifies educational institution & student attire</td>
                  </tr>
                  <tr>
                    <td><strong>School Badges & Crests</strong></td>
                    <td>Vision Grounding + Contextual OCR</td>
                    <td>Pinpoints specific school attended</td>
                  </tr>
                  <tr>
                    <td><strong>API Keys & Tokens</strong></td>
                    <td>Shannon Entropy + Prefix Regex</td>
                    <td>Prevents critical cloud & developer credential takeover</td>
                  </tr>
                  <tr>
                    <td><strong>Passwords</strong></td>
                    <td>Contextual Key-Value Heuristics</td>
                    <td>Prevents account compromise</td>
                  </tr>
                  <tr>
                    <td><strong>Email Addresses</strong></td>
                    <td>RFC 5322 Regex Extraction</td>
                    <td>Prevents phishing, spam, and identity matching</td>
                  </tr>
                  <tr>
                    <td><strong>Phone Numbers</strong></td>
                    <td>SG (+65) & International Formats</td>
                    <td>Guards against scam calls and SIM-swap attacks</td>
                  </tr>
                  <tr>
                    <td><strong>Personal Names</strong></td>
                    <td>Pass/Recipient Contextual Parsing</td>
                    <td>Prevents direct personal identification</td>
                  </tr>
                  <tr>
                    <td><strong>Residential Addresses</strong></td>
                    <td>Blk, Unit, Street & Postal Regex</td>
                    <td>Protects physical home address privacy</td>
                  </tr>
                  <tr>
                    <td><strong>NRIC / FIN / SSN</strong></td>
                    <td>Format Verification Regex</td>
                    <td>Mitigates severe national identity theft and fraud</td>
                  </tr>
                  <tr>
                    <td><strong>Payment Cards</strong></td>
                    <td>Luhn Algorithm Checksum</td>
                    <td>Validates and redacts 13-19 digit payment cards</td>
                  </tr>
                  <tr>
                    <td><strong>Faces</strong></td>
                    <td>OpenCV Haar Cascades</td>
                    <td>Biometric face localization without storing identities</td>
                  </tr>
                  <tr>
                    <td><strong>QR Codes</strong></td>
                    <td>OpenCV Multi-Threshold Detector</td>
                    <td>Detects hidden URLs and authentication QR codes</td>
                  </tr>
                  <tr>
                    <td><strong>IP Addresses</strong></td>
                    <td>IPv4 & IPv6 Subnet Parsers</td>
                    <td>Shields home router and network endpoint topology</td>
                  </tr>
                  <tr>
                    <td><strong>Street & Transit Signs</strong></td>
                    <td>OCR Road Suffixes & SG Transit</td>
                    <td>Identifies commute corridors and neighborhood landmarks</td>
                  </tr>
                  <tr>
                    <td><strong>GPS / EXIF Metadata</strong></td>
                    <td>Pillow IFD 34853 & ExifRead</td>
                    <td>Detects & strips covert GPS coordinates from image files</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Section 3: Redaction & Verification */}
        <section className="info-section">
          <div className="info-card">
            <div className="info-card-header">
              <Lock className="text-emerald" size={24} />
              <h2>True Opaque Redaction vs Client-Side Blurs</h2>
            </div>
            <p>
              Many popular photo apps apply lightweight blur or pixelation filters on photos. In recent years, automated de-blurring neural networks (such as Depix) can reliably reconstruct blurred text and faces.
            </p>
            <p>
              PrivacyLens utilizes <strong>Server-Side Solid Opaque Overwrite</strong>:
            </p>
            <ul className="check-list">
              <li>
                <CheckCircle2 size={16} className="text-emerald" />
                <span>Every redacted region is filled with 100% solid black pixels with a 4px safety boundary.</span>
              </li>
              <li>
                <CheckCircle2 size={16} className="text-emerald" />
                <span>The underlying original pixels are permanently destroyed and cannot be reversed by any AI algorithm.</span>
              </li>
              <li>
                <CheckCircle2 size={16} className="text-emerald" />
                <span>All EXIF headers, GPS metadata, and device serial numbers are completely stripped upon PNG export.</span>
              </li>
            </ul>

            <div className="cta-inline">
              <Link to="/app" className="btn-primary-hero">
                <Scan size={18} />
                <span>Try the Scanner Now</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
