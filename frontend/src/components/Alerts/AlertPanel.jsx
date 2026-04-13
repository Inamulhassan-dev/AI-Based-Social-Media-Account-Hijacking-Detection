import { useEffect, useState } from "react";
import { FiBell } from "react-icons/fi";
import toast from "react-hot-toast";

import { alertAPI } from "../../services/api";

export default function AlertPanel() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  const loadAlerts = () => {
    return alertAPI
      .getAlerts()
      .then((response) => {
        setAlerts(response.data.alerts);
        setStats(response.data.stats);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const runScenario = async (scenario) => {
    try {
      await alertAPI.createDemoScenario(scenario);
      toast.success("Scenario generated");
      await loadAlerts();
    } catch {
      toast.error("Could not create scenario");
    }
  };

  const takeAction = async (id, action) => {
    try {
      await alertAPI.takeAction(id, action);
      toast.success("Action recorded");
      await loadAlerts();
    } catch {
      toast.error("Action failed");
    }
  };

  const getSeverityClass = (severity) => {
    if (severity === "critical") return "text-rose-300 border-rose-400/40 bg-rose-400/10";
    if (severity === "high") return "text-amber-300 border-amber-400/40 bg-amber-400/10";
    if (severity === "medium") return "text-sky-300 border-sky-400/40 bg-sky-400/10";
    return "text-slate-300 border-slate-400/30 bg-slate-400/10";
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-52" />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="skeleton h-16" />
          <div className="skeleton h-16" />
          <div className="skeleton h-16" />
          <div className="skeleton h-16" />
          <div className="skeleton h-16" />
        </div>
        <div className="skeleton h-40" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Security Alerts</h1>

      <div className="cyber-card p-4">
        <p className="metric-label mb-3">Demo Mode with realistic scenarios</p>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => runScenario("new_device")} className="cyber-btn">New device login</button>
          <button onClick={() => runScenario("impossible_travel")} className="cyber-btn">Impossible travel</button>
          <button onClick={() => runScenario("brute_force")} className="cyber-btn">Brute-force burst</button>
          <button onClick={() => runScenario("bot_takeover")} className="cyber-btn">Bot takeover</button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="cyber-card p-3"><p className="metric-label">Total</p><p className="text-xl font-semibold">{stats.total || 0}</p></div>
        <div className="cyber-card p-3"><p className="metric-label">Unread</p><p className="text-xl font-semibold">{stats.unread || 0}</p></div>
        <div className="cyber-card p-3"><p className="metric-label">Critical</p><p className="text-xl font-semibold">{stats.critical || 0}</p></div>
        <div className="cyber-card p-3"><p className="metric-label">High</p><p className="text-xl font-semibold">{stats.high || 0}</p></div>
        <div className="cyber-card p-3"><p className="metric-label">Resolved</p><p className="text-xl font-semibold">{stats.resolved || 0}</p></div>
      </div>

      <div className="space-y-3">
        {alerts.map((alert) => (
          <div key={alert.id} className="cyber-card p-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-semibold text-white">{alert.title}</h3>
              <span className={`text-xs px-2 py-1 border rounded-full ${getSeverityClass(alert.severity)}`}>
                {(alert.severity || "low").toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-slate-300 whitespace-pre-line mt-2">{alert.message}</p>
            <p className="text-xs text-slate-400 mt-2">{new Date(alert.created_at).toLocaleString()} | Risk: {Math.round((alert.risk_score || 0) * 100)}%</p>

            <div className="mt-3 p-3 rounded-lg border border-slate-500/30 bg-slate-900/40">
              <p className="text-xs text-slate-400 mb-2">Why flagged (top factors)</p>
              {(() => {
                let parsed = [];
                try {
                  parsed = JSON.parse(alert.details || "[]");
                } catch {
                  parsed = [];
                }
                const factors = parsed.slice(0, 3);
                return factors.length ? factors.map((factor, idx) => (
                  <p key={`${alert.id}-factor-${idx}`} className="text-xs text-slate-200">- {factor.factor}: {factor.detail}</p>
                )) : <p className="text-xs text-slate-300">No factor details available.</p>;
              })()}
            </div>

            <div className="mt-3">
              <p className="text-xs text-slate-400 mb-2">User Action Center</p>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => takeAction(alert.id, "this_was_me")} className="cyber-btn">This was me</button>
                <button onClick={() => takeAction(alert.id, "not_me")} className="cyber-btn">Not me</button>
                <button onClick={() => takeAction(alert.id, "lock_account")} className="cyber-btn">Lock account</button>
                <button onClick={() => takeAction(alert.id, "require_2fa")} className="cyber-btn">Require 2FA</button>
                <button onClick={() => takeAction(alert.id, "end_sessions")} className="cyber-btn">End sessions</button>
              </div>
            </div>
          </div>
        ))}

        {!alerts.length && (
          <div className="text-center py-16 text-slate-400 cyber-card">
            <FiBell className="text-5xl mx-auto mb-4 opacity-30" />
            <p className="font-medium">No alerts right now</p>
            <p className="text-sm mt-2">When suspicious events are detected, they will appear here with severity and action hints.</p>
          </div>
        )}
      </div>
    </div>
  );
}
