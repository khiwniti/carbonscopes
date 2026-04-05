'use client';

import { useState } from "react";

const TABS = ["Logo", "Lockups", "System"];

function Mark({ size = 100, color = "#10B981", weight = null, animate = false, delay = 0 }: { size?: number; color?: string; weight?: number | null; animate?: boolean; delay?: number }) {
  const s = size, w = weight || s * 0.08;
  const r = s * 0.36, cx = s * 0.48, cy = s * 0.5;
  const gapDeg = 65;
  const toRad = (d: number) => (Math.PI / 180) * d;
  const startDeg = -gapDeg / 2, endDeg = 360 - gapDeg / 2;
  const x1 = cx + r * Math.cos(toRad(startDeg)), y1 = cy + r * Math.sin(toRad(startDeg));
  const x2 = cx + r * Math.cos(toRad(endDeg)), y2 = cy + r * Math.sin(toRad(endDeg));
  const arcPath = `M${x1.toFixed(1)},${y1.toFixed(1)} A${r},${r} 0 1,1 ${x2.toFixed(1)},${y2.toFixed(1)}`;
  const arcLen = 2 * Math.PI * r * ((360 - gapDeg) / 360);
  const bx = cx + r * 0.2, bTop = cy - r - s * 0.08, bBot = cy - r * 0.3;
  const lineLen = bBot - bTop;
  return (
    <svg viewBox={`0 0 ${s} ${s}`} width={s} height={s}>
      <path d={arcPath} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round"
        style={animate ? { strokeDasharray: arcLen + 10, strokeDashoffset: arcLen + 10, animation: `arcD 0.8s cubic-bezier(0.4,0,0.2,1) ${delay}s forwards` } : {}} />
      <line x1={bx} y1={bTop} x2={bx} y2={bBot} stroke={color} strokeWidth={w * 0.6} strokeLinecap="round"
        style={animate ? { strokeDasharray: lineLen + 5, strokeDashoffset: lineLen + 5, animation: `lineD 0.4s cubic-bezier(0.4,0,0.2,1) ${delay + 0.5}s forwards` } : {}} />
    </svg>
  );
}

function Type({ sz = 1, dark = true, full = false }: { sz?: number; dark?: boolean; full?: boolean }) {
  const fg = dark ? "#F1F5F9" : "#0F172A";
  const ac = dark ? "#10B981" : "#047857";
  const mu = dark ? "#475569" : "#94A3B8";
  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 2 * sz }}>
        <span style={{ fontFamily: "var(--fd)", fontSize: 32 * sz, fontWeight: 600, color: ac, letterSpacing: "-0.04em", lineHeight: 1 }}>c</span>
        <span style={{ fontFamily: "var(--fd)", fontSize: 32 * sz, fontWeight: 600, color: fg, letterSpacing: "-0.04em", lineHeight: 1 }}>BIM</span>
        <span style={{ fontFamily: "var(--fm)", fontSize: 11 * sz, fontWeight: 500, color: mu, letterSpacing: "0.06em", marginLeft: 2 * sz }}>AI</span>
      </div>
      {full && <div style={{ fontFamily: "var(--fm)", fontSize: 9.5 * sz, color: mu, letterSpacing: "0.15em", textTransform: "uppercase", marginTop: 6 * sz }}>Carbon Analytics</div>}
    </div>
  );
}

function Box({ children, bg = "#111827", border = "#1E293B", label, wide }: { children: React.ReactNode; bg?: string; border?: string; label?: string; wide?: boolean }) {
  const [h, sH] = useState(false);
  return (
    <div onMouseEnter={() => sH(true)} onMouseLeave={() => sH(false)} style={{
      background: bg, border: `1px solid ${h ? "#334155" : border}`, borderRadius: 20,
      padding: wide ? "48px 56px" : "40px 32px", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", gap: 20,
      transition: "all 0.3s ease", boxShadow: h ? "0 8px 40px rgba(0,0,0,0.3)" : "none",
    }}>
      {children}
      {label && <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#334155", letterSpacing: "0.12em", textTransform: "uppercase" }}>{label}</span>}
    </div>
  );
}

function Sw({ hex, label, big }: { hex: string; label?: string; big?: boolean }) {
  const dk = ["#0B1120", "#0F172A", "#111827", "#1E293B"].includes(hex);
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
      <div style={{ width: big ? 64 : 44, height: big ? 64 : 44, borderRadius: big ? 16 : 10, background: hex, border: dk ? "1px solid #1E293B" : "none", transition: "transform 0.2s ease" }}
        onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.1)"} onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"} />
      {label && <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#475569" }}>{label}</span>}
      <span style={{ fontFamily: "var(--fm)", fontSize: 7, color: "#334155" }}>{hex}</span>
    </div>
  );
}

export default function BrandGuidePage() {
  const [tab, setTab] = useState(0);
  const [k, sK] = useState(0);
  const replay = () => sK(n => n + 1);

  return (
    <div style={{ "--fd": "'Outfit', system-ui, sans-serif", "--fm": "'Red Hat Mono', monospace", fontFamily: "var(--fd)", background: "#0B1120", color: "#F1F5F9", minHeight: "100vh" } as React.CSSProperties}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Red+Hat+Mono:wght@400;500;600;700&display=swap');
        @keyframes arcD{to{stroke-dashoffset:0}}
        @keyframes lineD{to{stroke-dashoffset:0}}
        @keyframes up{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        @keyframes si{from{opacity:0;transform:scale(0.9)}to{opacity:1;transform:scale(1)}}
        @keyframes pulse{0%,100%{opacity:0.3}50%{opacity:0.7}}
        @keyframes orb{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
      `}</style>

      <header style={{ position: "sticky", top: 0, zIndex: 100, height: 52, background: "rgba(11,17,32,0.8)", backdropFilter: "blur(20px)", borderBottom: "1px solid rgba(30,41,59,0.5)", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Mark size={22} color="#10B981" />
          <span style={{ fontSize: 14, fontWeight: 600, letterSpacing: "-0.03em" }}><span style={{ color: "#10B981" }}>c</span>BIM</span>
        </div>
        <div style={{ display: "flex", gap: 1, background: "#0F172A", borderRadius: 10, padding: 3, border: "1px solid #1E293B" }}>
          {TABS.map((t, i) => (
            <button key={t} onClick={() => { setTab(i); replay(); }} style={{ padding: "6px 18px", borderRadius: 8, border: "none", cursor: "pointer", background: tab === i ? "#1E293B" : "transparent", color: tab === i ? "#F1F5F9" : "#475569", fontFamily: "var(--fm)", fontSize: 10, fontWeight: 600, letterSpacing: "0.03em", transition: "all 0.2s ease" }}>{t}</button>
          ))}
        </div>
      </header>

      {tab === 0 && (
        <div key={k}>
          <section style={{ minHeight: "calc(100vh - 52px)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", width: 500, height: 500, borderRadius: "50%", background: "radial-gradient(circle, rgba(16,185,129,0.04) 0%, transparent 60%)", pointerEvents: "none" }} />
            <div style={{ position: "absolute", width: 200, height: 200, animation: "orb 30s linear infinite" }}>
              <div style={{ position: "absolute", top: 0, left: "50%", width: 3, height: 3, borderRadius: "50%", background: "#10B981", boxShadow: "0 0 16px rgba(16,185,129,0.5)", transform: "translateX(-50%)" }} />
            </div>
            <div style={{ animation: "si 0.9s cubic-bezier(0.4,0,0.2,1) both" }}>
              <Mark size={220} color="#10B981" animate delay={0.3} />
            </div>
            <div style={{ marginTop: 44, textAlign: "center", animation: "up 0.7s ease 0.9s both" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, justifyContent: "center" }}>
                <span style={{ fontFamily: "var(--fm)", fontSize: 9, fontWeight: 600, color: "#334155", padding: "3px 10px", borderRadius: 6, border: "1px solid #1E293B", letterSpacing: "0.1em" }}>BKS</span>
                <span style={{ fontSize: 44, fontWeight: 600, letterSpacing: "-0.04em", lineHeight: 1 }}>
                  <span style={{ color: "#10B981" }}>c</span>BIM
                  <span style={{ fontFamily: "var(--fm)", fontSize: 14, fontWeight: 500, color: "#475569", marginLeft: 4, letterSpacing: "0.06em" }}>AI</span>
                </span>
              </div>
              <div style={{ fontFamily: "var(--fm)", fontSize: 11, color: "#334155", letterSpacing: "0.2em", textTransform: "uppercase", marginTop: 14 }}>Autonomous Carbon Analytics</div>
            </div>
          </section>

          <section style={{ padding: "72px 56px", borderTop: "1px solid #1E293B" }}>
            <span style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#10B981", letterSpacing: "0.14em" }}>ANATOMY</span>
            <h2 style={{ fontSize: 28, fontWeight: 600, letterSpacing: "-0.03em", margin: "8px 0 48px", color: "#F1F5F9" }}>Two elements. One idea.</h2>
            <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 64, alignItems: "center" }}>
              <div style={{ display: "flex", justifyContent: "center" }}><Mark size={260} color="#10B981" /></div>
              <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <div style={{ width: 28, height: 3, borderRadius: 2, background: "#10B981" }} />
                    <span style={{ fontSize: 17, fontWeight: 600 }}>The Arc</span>
                  </div>
                  <p style={{ fontSize: 14, color: "#64748B", lineHeight: 1.75, maxWidth: 440 }}>A 295° arc forming the letter "c" — carbon, cBIM, cycle. The opening represents the carbon lifecycle gap that better design can close.</p>
                </div>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <div style={{ width: 3, height: 22, borderRadius: 2, background: "#10B981" }} />
                    <span style={{ fontSize: 17, fontWeight: 600 }}>The Column</span>
                  </div>
                  <p style={{ fontSize: 14, color: "#64748B", lineHeight: 1.75, maxWidth: 440 }}>A vertical rising from the arc's interior — the building, the structure. Carbon embracing the built environment. Thinner stroke creates visual hierarchy.</p>
                </div>
                <div style={{ padding: "14px 18px", borderRadius: 12, background: "rgba(16,185,129,0.04)", border: "1px solid rgba(16,185,129,0.08)" }}>
                  <p style={{ fontFamily: "var(--fm)", fontSize: 11, color: "#475569", lineHeight: 1.7, margin: 0 }}>Together: the embodied carbon envelope around the built environment. Drawn in 2 seconds. Recognized at any scale.</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      )}

      {tab === 1 && (
        <div key={k} style={{ padding: "48px 40px 80px" }}>
          <span style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#10B981", letterSpacing: "0.14em" }}>LOCKUPS</span>
          <h2 style={{ fontSize: 28, fontWeight: 600, letterSpacing: "-0.03em", margin: "8px 0 40px" }}>Every context.</h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
            <Box label="Primary — Dark" bg="#111827">
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <Mark size={50} color="#10B981" />
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span style={{ fontFamily: "var(--fm)", fontSize: 8.5, fontWeight: 600, color: "#334155", padding: "2px 8px", borderRadius: 5, border: "1px solid #1E293B", letterSpacing: "0.1em" }}>BKS</span><Type sz={0.75} dark /></div>
                  <div style={{ fontFamily: "var(--fm)", fontSize: 8, color: "#334155", letterSpacing: "0.16em", textTransform: "uppercase", marginTop: 4 }}>Autonomous Carbon Analytics</div>
                </div>
              </div>
            </Box>
            <Box label="Primary — Light" bg="#FAFBFC" border="#E5E7EB">
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <Mark size={50} color="#047857" />
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span style={{ fontFamily: "var(--fm)", fontSize: 8.5, fontWeight: 600, color: "#94A3B8", padding: "2px 8px", borderRadius: 5, border: "1px solid #E5E7EB", letterSpacing: "0.1em" }}>BKS</span><Type sz={0.75} dark={false} /></div>
                  <div style={{ fontFamily: "var(--fm)", fontSize: 8, color: "#94A3B8", letterSpacing: "0.16em", textTransform: "uppercase", marginTop: 4 }}>Autonomous Carbon Analytics</div>
                </div>
              </div>
            </Box>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 16 }}>
            <Box label="Stacked"><Mark size={68} color="#10B981" /><Type sz={0.6} dark full /></Box>
            <Box label="Mono White" bg="#0B1120"><Mark size={76} color="#E2E8F0" /></Box>
            <Box label="Mono Black" bg="#FFFFFF" border="#E5E7EB"><Mark size={76} color="#0F172A" /></Box>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Box label="Mark Only"><Mark size={88} color="#10B981" /></Box>
            <Box label="Scaling">
              <div style={{ display: "flex", alignItems: "flex-end", gap: 24 }}>
                {[56, 40, 28, 20, 14].map(s => (
                  <div key={s} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
                    <Mark size={s} color="#10B981" />
                    <span style={{ fontFamily: "var(--fm)", fontSize: 8, color: "#334155" }}>{s}px</span>
                  </div>
                ))}
              </div>
            </Box>
          </div>
        </div>
      )}

      {tab === 2 && (
        <div key={k} style={{ padding: "48px 40px 80px" }}>
          <span style={{ fontFamily: "var(--fm)", fontSize: 10, color: "#10B981", letterSpacing: "0.14em" }}>SYSTEM</span>
          <h2 style={{ fontSize: 28, fontWeight: 600, letterSpacing: "-0.03em", margin: "8px 0 48px" }}>Colors & Type</h2>

          <div style={{ display: "flex", flexDirection: "column", gap: 32, marginBottom: 56 }}>
            <div>
              <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#475569", letterSpacing: "0.12em" }}>PRIMARY</span>
              <div style={{ display: "flex", gap: 14, marginTop: 12 }}>
                {[["50","#ECFDF5"],["200","#A7F3D0"],["400","#34D399"],["500","#10B981"],["600","#059669"],["700","#047857"],["800","#065F46"]].map(([l,h]) => <Sw key={l} hex={h} label={l} big={l==="500"||l==="600"} />)}
              </div>
            </div>
            <div>
              <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#475569", letterSpacing: "0.12em" }}>SURFACES</span>
              <div style={{ display: "flex", gap: 14, marginTop: 12 }}>
                {[["Base","#0B1120"],["Surface","#111827"],["Elevated","#1E293B"],["Muted","#475569"],["Text","#F1F5F9"]].map(([l,h]) => <Sw key={l} hex={h} label={l} />)}
              </div>
            </div>
            <div>
              <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#475569", letterSpacing: "0.12em" }}>EN 15978</span>
              <div style={{ display: "flex", gap: 14, marginTop: 12 }}>
                {[["A1–A3","#3B82F6"],["A4–A5","#60A5FA"],["B1–B5","#F59E0B"],["B6–B7","#EA580C"],["C1–C4","#6B7280"],["D","#10B981"]].map(([l,h]) => <Sw key={l} hex={h} label={l} />)}
              </div>
            </div>
          </div>

          <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#475569", letterSpacing: "0.12em" }}>TYPOGRAPHY</span>
          <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 16, marginBottom: 48 }}>
            {[
              { r: "Display", f: "var(--fd)", s: 40, w: 600, t: "cBIM AI", c: "#F1F5F9", ls: "-0.04em" },
              { r: "Heading", f: "var(--fd)", s: 22, w: 600, t: "Whole Life Carbon Assessment", c: "#F1F5F9", ls: "-0.02em" },
              { r: "Body", f: "var(--fd)", s: 15, w: 400, t: "Embodied and operational carbon analytics for construction.", c: "#94A3B8", ls: "0" },
              { r: "Data", f: "var(--fm)", s: 13, w: 500, t: "847,300 kgCO₂e  ·  412 kgCO₂e/m²  ·  LETI Band B", c: "#64748B", ls: "0.02em" },
              { r: "Label", f: "var(--fm)", s: 10, w: 600, t: "AUTONOMOUS CARBON ANALYTICS", c: "#334155", ls: "0.16em" },
            ].map((t, i) => (
              <div key={i} style={{ padding: "18px 24px", borderRadius: 14, background: "#111827", border: "1px solid #1E293B", display: "flex", alignItems: "center", gap: 20 }}>
                <span style={{ fontFamily: "var(--fm)", fontSize: 8, color: "#334155", letterSpacing: "0.1em", width: 60, flexShrink: 0, textTransform: "uppercase" }}>{t.r}</span>
                <span style={{ fontFamily: t.f, fontSize: t.s, fontWeight: t.w, color: t.c, letterSpacing: t.ls, lineHeight: 1.3 }}>{t.t}</span>
              </div>
            ))}
          </div>

          <span style={{ fontFamily: "var(--fm)", fontSize: 9, color: "#475569", letterSpacing: "0.12em" }}>MOTION</span>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginTop: 16 }}>
            <Box label="Draw-on"><Mark size={72} color="#10B981" animate delay={0} key={k + "a"} /></Box>
            <Box label="Ambient">
              <div style={{ position: "relative" }}>
                <div style={{ position: "absolute", inset: -20, borderRadius: "50%", background: "radial-gradient(circle, rgba(16,185,129,0.06) 0%, transparent 70%)", animation: "pulse 3s ease infinite" }} />
                <Mark size={72} color="#10B981" />
              </div>
            </Box>
            <Box label="Orbital">
              <div style={{ position: "relative", width: 72, height: 72 }}>
                <Mark size={72} color="#10B981" />
                <div style={{ position: "absolute", inset: -14, animation: "orb 12s linear infinite" }}>
                  <div style={{ position: "absolute", top: 0, left: "50%", transform: "translateX(-50%)", width: 3, height: 3, borderRadius: "50%", background: "#34D399", boxShadow: "0 0 10px rgba(52,211,153,0.5)" }} />
                </div>
              </div>
            </Box>
          </div>
          <div style={{ textAlign: "center", marginTop: 16 }}>
            <button onClick={replay} style={{ padding: "7px 20px", borderRadius: 8, background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.1)", color: "#34D399", fontFamily: "var(--fm)", fontSize: 10, fontWeight: 600, cursor: "pointer", letterSpacing: "0.06em" }}>↻ Replay</button>
          </div>
        </div>
      )}
    </div>
  );
}
