import { Link } from "react-router-dom";
import { Shield, Lock, Cpu, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        <div className="footer-top">
          <div className="footer-brand-col">
            <div className="footer-logo">
              <Shield className="footer-logo-icon" size={22} />
              <span className="footer-logo-title">PrivacyLens</span>
            </div>
            <p className="footer-tagline">
              Empowering youths to understand and protect their digital privacy before sharing online.
              Combining multi-modal AI with Exposure Reconstruction to set boundaries in a hyper-connected world.
            </p>
            <div className="hackathon-tag">
              <span className="tag-dot" />
              <span>Spot It! Stop It! Hackathon · Problem Statement 01: Set Boundaries Online</span>
            </div>
          </div>

          <div className="footer-links-col">
            <h4>Product</h4>
            <ul>
              <li><Link to="/app">AI Privacy Scanner</Link></li>
              <li><Link to="/how-it-works">How It Works</Link></li>
              <li><Link to="/how-it-works#mosaic-effect">The Mosaic Effect</Link></li>
              <li><Link to="/how-it-works#15-categories">15 Detection Vectors</Link></li>
            </ul>
          </div>

          <div className="footer-links-col">
            <h4>Ethics & Trust</h4>
            <ul>
              <li><Link to="/privacy">Local-First Processing</Link></li>
              <li><Link to="/privacy#data-handling">Zero Cloud Storage</Link></li>
              <li><Link to="/privacy#limitations">Model Limitations</Link></li>
              <li><a href="https://github.com/feliciatanxl/PrivacyLens" target="_blank" rel="noopener noreferrer">GitHub Repository</a></li>
            </ul>
          </div>

          <div className="footer-info-col">
            <h4>Technology Stack</h4>
            <div className="tech-pills">
              <span className="tech-pill"><Cpu size={12} /> Microsoft Florence-2</span>
              <span className="tech-pill"><Cpu size={12} /> PaddleOCR PP-OCRv4</span>
              <span className="tech-pill"><Cpu size={12} /> OpenCV Cascades</span>
              <span className="tech-pill"><Lock size={12} /> EXIF Decontamination</span>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="disclaimer-text">
            <strong>Prototype Disclaimer:</strong> PrivacyLens is a research & hackathon prototype designed for privacy education and awareness. While our AI engine detects 15 privacy categories, no computer vision system can guarantee 100% detection under all image conditions. Always review your images carefully before posting.
          </p>
          <div className="footer-copyright">
            <span>© 2026 PrivacyLens Team. Built with <Heart size={12} className="heart-icon" /> for safe youth digital expression.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
