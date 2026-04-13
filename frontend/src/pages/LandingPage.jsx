import { Link } from "react-router-dom";
import { FiActivity, FiAlertTriangle, FiCheckCircle, FiMapPin, FiMonitor, FiShield } from "react-icons/fi";

import AnimatedBackground from "../components/3DBackground/AnimatedBackground";

export default function LandingPage() {
  const features = [
    { icon: FiMonitor, title: "Device Intelligence", desc: "Flags unusual devices, browser changes, and suspicious machine fingerprints." },
    { icon: FiMapPin, title: "Location Risk", desc: "Detects impossible travel, VPN behavior, and unusual geolocation patterns." },
    { icon: FiActivity, title: "Behavior AI", desc: "Combines rule-based scoring with ML models for reliable risk decisions." },
  ];

  const workflow = [
    "User logs in from web app",
    "System computes risk from behavior + ML",
    "Platform triggers allow, warning, alert, or lock",
  ];

  return (
    <div className="relative min-h-screen app-shell">
      <AnimatedBackground />
      <div className="relative z-10 px-4 pt-28 pb-16 md:pt-36">
        <section className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-10 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-sky-300/30 bg-sky-400/10 text-sky-200 text-xs mb-5">
              <FiShield /> Production-ready account protection
            </div>
            <h1 className="text-4xl md:text-6xl font-bold leading-tight">
              Protect user accounts with real-time hijacking detection.
            </h1>
            <p className="mt-5 text-slate-300 text-lg max-w-xl">
              ShieldAI monitors login behavior and blocks risky access using explainable AI risk scoring, alerts, and admin controls.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="cyber-btn px-6 py-3">Start free trial</Link>
              <Link to="/login" className="cyber-btn btn-secondary px-6 py-3">Sign in</Link>
            </div>
          </div>

          <div className="cyber-card p-6 md:p-7">
            <h2 className="text-xl font-semibold">What happens on risky login?</h2>
            <div className="mt-4 space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <FiCheckCircle className="mt-0.5 text-emerald-400" />
                <p><span className="font-semibold">Low risk:</span> login is allowed and tracked.</p>
              </div>
              <div className="flex items-start gap-3">
                <FiAlertTriangle className="mt-0.5 text-amber-400" />
                <p><span className="font-semibold">Medium risk:</span> warning shown and event flagged.</p>
              </div>
              <div className="flex items-start gap-3">
                <FiShield className="mt-0.5 text-rose-400" />
                <p><span className="font-semibold">High risk:</span> alert created for security review.</p>
              </div>
            </div>
            <div className="mt-6 p-4 rounded-lg border border-slate-500/30 bg-slate-900/50">
              <p className="metric-label">Sample response speed</p>
              <p className="metric-value text-sky-300">&lt; 120 ms</p>
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto mt-14 grid md:grid-cols-3 gap-4">
          {features.map((feature) => (
            <div key={feature.title} className="cyber-card p-5">
              <feature.icon className="text-sky-300 text-2xl" />
              <h3 className="mt-3 text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm text-slate-300">{feature.desc}</p>
            </div>
          ))}
        </section>

        <section className="max-w-6xl mx-auto mt-10 cyber-card p-6 md:p-7">
          <h3 className="text-xl font-semibold">How real users use this product</h3>
          <ol className="mt-4 space-y-3 text-slate-200 text-sm list-decimal pl-5">
            {workflow.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  );
}
