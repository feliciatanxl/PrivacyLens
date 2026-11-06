import { Link } from "react-router-dom";
import {
  Scan,
  Sparkles,
  ArrowRight,
  Eye,
  Lock,
  Layers,
  AlertTriangle,
  UserCheck,
  MapPin,
  Clock,
  KeyRound,
  FileText,
  Camera,
  CheckCircle2,
  ChevronRight,
  Cpu
} from "lucide-react";
import HeroDemo from "../components/HeroDemo";

export default function Home() {
  const problemClues = [
    {
      icon: <Layers size={22} className="text-violet" />,
      title: "School Uniforms & Crests",
      desc: "A sports jersey or blazer pocket crest immediately pinpoints your exact educational institution.",
    },
    {
      icon: <MapPin size={22} className="text-cyan" />,
      title: "Street Signs & Transit Stops",
      desc: "Background road names, MRT pillar codes, or bus stop signs reveal your physical travel corridor.",
    },
    {
      icon: <Clock size={22} className="text-amber" />,
      title: "Schedules & Desk Timetables",
      desc: "A study planner or exam sheet on your desk broadcasts recurring routines and free periods.",
    },
    {
      icon: <FileText size={22} className="text-emerald" />,
      title: "Delivery Slips & Passes",
      desc: "Unboxing photos often accidentally expose unit numbers, contact numbers, and recipient names.",
    },
    {
      icon: <KeyRound size={22} className="text-rose" />,
      title: "Accidental Credentials",
      desc: "IDE screenshots and browser tabs frequently leak API keys, auth tokens, and session passwords.",
    },
    {
      icon: <Camera size={22} className="text-blue" />,
      title: "Embedded GPS Coordinates",
      desc: "Camera EXIF headers silently record precise latitude and longitude coordinates inside the file.",
    },
  ];

  const detectionCategories = [
    {
      family: "Personal Identity",
      badge: "Identity Vectors",
      items: [
        { name: "Personal Names", desc: "Detected via contextual recipient & pass prefixes" },
        { name: "Singapore NRIC / FIN & SSN", desc: "National identification number formats" },
        { name: "Phone Numbers", desc: "Singapore (+65 / 8xxx / 9xxx) & international" },
        { name: "Email Addresses", desc: "RFC 5322 standard address patterns" },
        { name: "Residential Addresses", desc: "Block numbers, street suffixes, unit #, 6-digit postal codes" },
      ],
    },
    {
      family: "Digital Security",
      badge: "Credentials & Network",
      items: [
        { name: "API Keys & Access Tokens", desc: "OpenAI, GitHub, AWS, Stripe, Google, and high-entropy secrets" },
        { name: "Passwords & Auth Pairs", desc: "Visible passwords, credentials, and token assignments" },
        { name: "IP Addresses", desc: "Public & internal IPv4 / IPv6 network endpoints" },
        { name: "Payment Card Numbers", desc: "13-19 digit card sequences validated via Luhn checksum" },
      ],
    },
    {
      family: "Visual Context & Biometrics",
      badge: "Real-World Clues",
      items: [
        { name: "Human Faces", desc: "OpenCV Haar cascade biometric face localization" },
        { name: "School Uniforms", desc: "Florence-2 object detection & student clothing grounding" },
        { name: "School Badges & Crests", desc: "Institutional logos and educational emblems" },
        { name: "Street Signs & Transit Clues", desc: "Road names, expressways, MRT signs, and bus routes" },
        { name: "QR Codes & 2D Barcodes", desc: "OpenCV multi-threshold QR decoders for hidden URLs" },
      ],
    },
    {
      family: "Hidden Geolocation",
      badge: "Metadata Layer",
      items: [
        { name: "GPS Latitude & Longitude", desc: "EXIF IFD 34853 embedded geographic coordinates" },
        { name: "Camera & Device Footprints", desc: "Device serials, lens metadata, and timestamp stamps" },
      ],
    },
  ];

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-glow-sphere" />
        <div className="hero-container">
          <div className="hero-badge">
            <span className="badge-pulse" />
            <span>Spot It! Stop It! Hackathon · Problem Statement 01: Set Boundaries Online</span>
          </div>

          <h1 className="hero-headline">
            Your photo reveals <br />
            <span className="text-gradient">more than you think.</span>
          </h1>

          <p className="hero-subheadline">
            A single image can reveal your identity, location, school or routine through details you might never notice.
            PrivacyLens finds sensitive information, connects hidden privacy clues, and helps you protect what matters — <strong>before you post</strong>.
          </p>

          <div className="hero-cta-group">
            <Link to="/app" className="btn-primary-hero">
              <Scan size={18} />
              <span>Scan an Image — Free</span>
              <ArrowRight size={16} />
            </Link>
            <Link to="/how-it-works" className="btn-secondary-hero">
              <Eye size={18} />
              <span>See How It Works</span>
            </Link>
          </div>

          {/* Interactive Hero Visual */}
          <HeroDemo />
        </div>
      </section>

      {/* The Problem Section */}
      <section className="section-problem">
        <div className="section-container">
          <div className="section-header-center">
            <span className="section-eyebrow">THE SHARING BLINDSPOT</span>
            <h2 className="section-title">
              It&apos;s not just what you post. <br />
              <span className="text-gradient-purple">It&apos;s what people can piece together.</span>
            </h2>
            <p className="section-desc">
              Privacy leaks rarely occur through one giant disclosure. Malicious actors and digital stalkers use <strong>The Mosaic Effect</strong>: gathering small, ordinary details scattered across your photos to construct your identity, daily schedule, and home location.
            </p>
          </div>

          <div className="problem-grid">
            {problemClues.map((clue, idx) => (
              <div key={idx} className="problem-card">
                <div className="problem-card-icon">{clue.icon}</div>
                <h3 className="problem-card-title">{clue.title}</h3>
                <p className="problem-card-desc">{clue.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The Solution: 3 Core Stages */}
      <section className="section-solution">
        <div className="section-container">
          <div className="section-header-center">
            <span className="section-eyebrow">OUR 3-STAGE AI PIPELINE</span>
            <h2 className="section-title">
              One scan. A clearer picture of your privacy.
            </h2>
            <p className="section-desc">
              PrivacyLens transforms complex machine learning into simple, actionable digital agency for everyday sharing.
            </p>
          </div>

          <div className="stages-grid">
            <div className="stage-card">
              <div className="stage-number">01</div>
              <div className="stage-icon-wrap">
                <Scan size={24} className="text-cyan" />
              </div>
              <h3>1. Detect</h3>
              <p>
                Lightweight PaddleOCR and Florence-2 computer vision locate text, uniforms, credentials, faces, QR codes, and EXIF metadata in milliseconds.
              </p>
            </div>

            <div className="stage-card active-stage">
              <div className="stage-number">02</div>
              <div className="stage-icon-wrap">
                <Sparkles size={24} className="text-violet" />
              </div>
              <div className="usp-pill">CORE USP</div>
              <h3>2. Understand</h3>
              <p>
                Our AI Exposure Reconstruction engine connects observed clues, explaining in plain language how combined details create real-world privacy risks.
              </p>
            </div>

            <div className="stage-card">
              <div className="stage-number">03</div>
              <div className="stage-icon-wrap">
                <Lock size={24} className="text-emerald" />
              </div>
              <h3>3. Protect</h3>
              <p>
                Review individual bounding boxes, add custom selections, and download a sanitized image with solid-opaque blackouts and stripped GPS metadata.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Main USP Showcase: AI Exposure Reconstruction */}
      <section className="section-usp">
        <div className="section-container">
          <div className="usp-split-wrapper">
            <div className="usp-text-col">
              <div className="usp-tag">
                <Sparkles size={16} />
                <span>INNOVATION HIGHLIGHT</span>
              </div>
              <h2 className="usp-headline">
                Introducing AI Exposure Reconstruction.
              </h2>
              <p className="usp-lead">
                The real risk isn&apos;t always one detail. <br />
                <strong>It&apos;s what those details reveal together.</strong>
              </p>
              <p className="usp-body">
                Conventional photo tools only offer blunt blur filters on whatever you manually highlight. PrivacyLens is the first privacy tool that synthesizes contextual reasoning: identifying when harmless fragments converge into a severe vulnerability.
              </p>

              <div className="usp-comparison-box">
                <div className="comp-col traditional">
                  <h4>Traditional Redaction Tools</h4>
                  <ul>
                    <li>❌ Found a school crest</li>
                    <li>❌ Found a street sign</li>
                    <li>❌ Found a dismissal time</li>
                    <li>❌ Leaves user wondering why it matters</li>
                  </ul>
                </div>
                <div className="comp-col privacylens">
                  <h4>PrivacyLens Exposure Reconstruction</h4>
                  <ul>
                    <li>✅ Explains that these clues reveal affiliation & commute routine</li>
                    <li>✅ Suggests specific proactive redaction areas</li>
                    <li>✅ Provides verifiable opaque blackout & EXIF stripping</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="usp-visual-col">
              <div className="interactive-mosaic-demo">
                <div className="mosaic-card-header">
                  <AlertTriangle size={18} className="text-amber" />
                  <span>Mosaic Effect Synthesis in Action</span>
                </div>

                <div className="mosaic-inputs">
                  <div className="mosaic-node">
                    <span className="node-icon">👕</span>
                    <div>
                      <strong>School Uniform</strong>
                      <small>Guangyang Secondary PE attire</small>
                    </div>
                  </div>
                  <div className="mosaic-plus">+</div>
                  <div className="mosaic-node">
                    <span className="node-icon">🚏</span>
                    <div>
                      <strong>Transit Marker</strong>
                      <small>Bishan St 12 Bus Stop</small>
                    </div>
                  </div>
                  <div className="mosaic-plus">+</div>
                  <div className="mosaic-node">
                    <span className="node-icon">📅</span>
                    <div>
                      <strong>Weekly Timetable</strong>
                      <small>Thursday CCA Dismissal 5:30PM</small>
                    </div>
                  </div>
                </div>

                <div className="mosaic-result">
                  <div className="result-badge">AI EXPOSURE ANALYSIS</div>
                  <p className="result-text">
                    &ldquo;These details together make it possible to deduce that the subject attends a specific school and regularly waits at this transit point around 5:30PM on Thursdays.&rdquo;
                  </p>
                  <div className="action-hint">
                    💡 <strong>Suggested Defense:</strong> Select &apos;School Crest&apos; and &apos;Transit Sign&apos; for one-click solid blackout before sharing.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 15 Detection Categories Capability Grid */}
      <section className="section-capabilities">
        <div className="section-container">
          <div className="section-header-center">
            <span className="section-eyebrow">COMPREHENSIVE COVERAGE</span>
            <h2 className="section-title">
              15 Privacy Vectors We Analyze
            </h2>
            <p className="section-desc">
              Engineered with specialized computer vision, optical character recognition, and cryptographic heuristics.
            </p>
          </div>

          <div className="categories-grid">
            {detectionCategories.map((group, idx) => (
              <div key={idx} className="category-group-card">
                <div className="group-header">
                  <span className="group-badge">{group.badge}</span>
                  <h3>{group.family}</h3>
                </div>
                <ul className="group-list">
                  {group.items.map((item, itemIdx) => (
                    <li key={itemIdx} className="category-item">
                      <div className="item-name">
                        <CheckCircle2 size={16} className="text-cyan" />
                        <strong>{item.name}</strong>
                      </div>
                      <p className="item-desc">{item.desc}</p>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="capability-footnote">
            ℹ️ Supported detection targets for awareness and educational safety. No automated system replaces careful human review.
          </div>
        </div>
      </section>

      {/* Why PrivacyLens Matters */}
      <section className="section-why">
        <div className="section-container">
          <div className="why-box">
            <div className="why-content">
              <span className="section-eyebrow">EMPOWERING YOUTHS</span>
              <h2>Setting boundaries online without losing your voice.</h2>
              <p>
                Social media is how youths connect, express themselves, and share achievements. We don&apos;t believe in telling students to stop posting. Instead, PrivacyLens equips young people with the awareness to spot invisible privacy risks and the agency to protect their boundaries before hitting publish.
              </p>
              <div className="why-bullets">
                <div className="why-bullet">
                  <UserCheck size={20} className="text-cyan" />
                  <span>Preserves digital freedom while preventing accidental oversharing</span>
                </div>
                <div className="why-bullet">
                  <Cpu size={20} className="text-violet" />
                  <span>100% on-device AI analysis keeping your photos private</span>
                </div>
                <div className="why-bullet">
                  <Lock size={20} className="text-emerald" />
                  <span>Permanent opaque blackout protection that cannot be reversed</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="section-final-cta">
        <div className="final-cta-container">
          <div className="final-cta-card">
            <div className="final-cta-glow" />
            <span className="final-cta-eyebrow">READY TO INSPECT YOUR PHOTOS?</span>
            <h2 className="final-cta-title">
              Before you share, see what you&apos;re sharing.
            </h2>
            <p className="final-cta-desc">
              Try our instant AI scanner on your own screenshots or test one of our pre-loaded sample images. Free, private, and running locally.
            </p>
            <div className="final-cta-actions">
              <Link to="/app" className="btn-final-launch">
                <Scan size={20} />
                <span>Launch PrivacyLens Scanner</span>
                <ChevronRight size={18} />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
