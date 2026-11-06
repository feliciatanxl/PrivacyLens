import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Shield, Scan, Menu, X, Sparkles } from "lucide-react";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { path: "/", label: "Home" },
    { path: "/how-it-works", label: "How It Works" },
    { path: "/privacy", label: "Privacy & Ethics" },
  ];

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link to="/" className="brand-logo" onClick={() => setMobileMenuOpen(false)}>
          <div className="brand-symbol">
            <Shield className="symbol-icon" size={20} />
            <div className="symbol-pulse" />
          </div>
          <div className="brand-text">
            <span className="brand-title">PrivacyLens</span>
            <span className="brand-pill">AI Scanner</span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="desktop-nav" aria-label="Main Navigation">
          <ul className="nav-menu">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className={`nav-link ${isActive ? "active" : ""}`}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Desktop CTA */}
        <div className="header-actions">
          <Link to="/app" className="launch-btn">
            <Scan size={16} />
            <span>Launch Scanner</span>
            <Sparkles size={14} className="sparkle-hint" />
          </Link>
          <button
            type="button"
            className="mobile-toggle-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-drawer">
          <ul className="mobile-menu">
            {navLinks.map((link) => (
              <li key={link.path}>
                <Link
                  to={link.path}
                  className={`mobile-link ${location.pathname === link.path ? "active" : ""}`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
            <li>
              <Link
                to="/app"
                className="mobile-cta-btn"
                onClick={() => setMobileMenuOpen(false)}
              >
                <Scan size={18} />
                <span>Launch AI Scanner</span>
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
