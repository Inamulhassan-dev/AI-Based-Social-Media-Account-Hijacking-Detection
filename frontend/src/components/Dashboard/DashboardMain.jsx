import { useEffect, useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FiAlertTriangle, FiCheckCircle, FiClock, FiGlobe, FiMapPin, FiShield } from "react-icons/fi";
import toast from "react-hot-toast";

import { alertAPI, dashboardAPI } from "../../services/api";
import { useAuth } from "../../context/AuthContext";

export default function DashboardMain() {
  const [data, setData] = useState(null);
  const [feed, setFeed] = useState([]);
  const [securityScore, setSecurityScore] = useState({ security_score: 100, weekly_trend: [], tips: [] });
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const load = () => {
      Promise.all([dashboardAPI.getSummary(), alertAPI.getLiveFeed(10), alertAPI.getSecurityScore()])
        .then(([summaryRes, feedRes, scoreRes]) => {
          setData(summaryRes.data);
          setFeed(feedRes.data.events || []);
          setSecurityScore(scoreRes.data || { security_score: 100, weekly_trend: [], tips: [] });
        })
        .catch(() => setData(null))
        .finally(() => setLoading(false));
    };

    load();
    const timer = setInterval(load, 8000);
    return () => clearInterval(timer);
  }, []);

  const triggerDemo = async () => {
    try {
      await alertAPI.createDemoScenario("new_device");
      toast.success("Demo event injected to feed");
      const [feedRes, scoreRes] = await Promise.all([alertAPI.getLiveFeed(10), alertAPI.getSecurityScore()]);
      setFeed(feedRes.data.events || []);
      setSecurityScore(scoreRes.data || { security_score: 100, weekly_trend: [], tips: [] });
    } catch {
      toast.error("Could not create demo event");
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="skeleton h-28" />
          <div className="skeleton h-28" />
          <div className="skeleton h-28" />
          <div className="skeleton h-28" />
        </div>
        <div className="skeleton h-80" />
      </div>
    );
  }

  if (!data) {
    return <p className="text-slate-300">Unable to load dashboard.</p>;
  }

  const riskTrendData = (data.behavior?.risk_trend || [])
    .map((item) => ({
      date: new Date(item.date).toLocaleDateString(),
      risk: Number((item.risk_score * 100).toFixed(0)),
    }))
    .reverse();

  const sampleTrendData = [
    { date: "Mon", risk: 18 },
    { date: "Tue", risk: 14 },
    { date: "Wed", risk: 22 },
    { date: "Thu", risk: 16 },
    { date: "Fri", risk: 11 },
  ];

  const chartData = riskTrendData.length ? riskTrendData : sampleTrendData;
  const scoreTrend = securityScore.weekly_trend?.length
    ? securityScore.weekly_trend
    : [
        { week: "W-4", score: 84 },
        { week: "W-3", score: 86 },
        { week: "W-2", score: 88 },
        { week: "W-1", score: 90 },
        { week: "Now", score: 91 },
      ];

  const countryDistribution = data.behavior?.location_distribution || {};
  const bubbleCountries = Object.entries(countryDistribution)
    .map(([country, count]) => ({ country, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const fallbackCountries = [
    { country: "Bangladesh", count: 22 },
    { country: "India", count: 9 },
    { country: "Germany", count: 4 },
    { country: "United States", count: 6 },
  ];

  const mapBubbles = bubbleCountries.length ? bubbleCountries : fallbackCountries;
  const maxBubble = Math.max(...mapBubbles.map((item) => item.count), 1);

  const countryCoords = {
    Bangladesh: [23.685, 90.3563],
    India: [20.5937, 78.9629],
    Germany: [51.1657, 10.4515],
    "United States": [37.0902, -95.7129],
    Canada: [56.1304, -106.3468],
    Pakistan: [30.3753, 69.3451],
    "United Kingdom": [55.3781, -3.436],
    France: [46.2276, 2.2137],
    Australia: [-25.2744, 133.7751],
    Japan: [36.2048, 138.2529],
  };

  const resolveCoords = (activity) => {
    if (!activity) return null;
    if (typeof activity.latitude === "number" && typeof activity.longitude === "number" && (activity.latitude !== 0 || activity.longitude !== 0)) {
      return [activity.latitude, activity.longitude];
    }
    return countryCoords[activity.country] || null;
  };

  const haversineKm = (lat1, lon1, lat2, lon2) => {
    const toRad = (deg) => (deg * Math.PI) / 180;
    const earth = 6371;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return earth * c;
  };

  const activities = data.behavior?.recent_activities || [];
  const currentActivity = activities[0];
  const previousActivity = activities[1];

  const currentCoords = resolveCoords(currentActivity);
  const previousCoords = resolveCoords(previousActivity);

  let impossibleTravel = null;
  if (currentActivity && previousActivity && currentCoords && previousCoords) {
    const distanceKm = haversineKm(previousCoords[0], previousCoords[1], currentCoords[0], currentCoords[1]);
    const hours = Math.max(0.01, (new Date(currentActivity.login_time) - new Date(previousActivity.login_time)) / (1000 * 60 * 60));
    const speed = distanceKm / hours;
    const suspicious = speed > 900;
    impossibleTravel = {
      from: `${previousActivity.city || "Unknown"}, ${previousActivity.country || "Unknown"}`,
      to: `${currentActivity.city || "Unknown"}, ${currentActivity.country || "Unknown"}`,
      distanceKm,
      hours,
      speed,
      suspicious,
    };
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
        <h1 className="text-3xl font-bold">Security Dashboard</h1>
        <p className="text-slate-300 mt-1">Welcome back, {user?.full_name || user?.username}</p>
        </div>
        <button onClick={triggerDemo} className="cyber-btn">Start demo simulation</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="cyber-card p-4">
          <p className="metric-label">Total Logins (30d)</p>
          <p className="metric-value text-sky-300">{data.behavior.total_logins_30d}</p>
        </div>
        <div className="cyber-card p-4">
          <p className="metric-label">Suspicious Logins</p>
          <p className="metric-value text-rose-300">{data.behavior.suspicious_logins_30d}</p>
        </div>
        <div className="cyber-card p-4">
          <p className="metric-label">Unread Alerts</p>
          <p className="metric-value text-amber-300">{data.alert_stats.unread}</p>
        </div>
        <div className="cyber-card p-4">
          <p className="metric-label">Current Risk</p>
          <p className="metric-value text-emerald-300">{Math.round((data.user?.risk_score || 0) * 100)}%</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="cyber-card p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold mb-3">Risk Score Trend</h3>
          {!riskTrendData.length && (
            <p className="text-xs text-slate-400 mb-2">No historical risk events yet. Showing sample trend preview.</p>
          )}
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#23344f" />
              <XAxis dataKey="date" stroke="#9fb1d1" fontSize={10} />
              <YAxis stroke="#9fb1d1" fontSize={10} />
              <Tooltip contentStyle={{ background: "#0e1729", border: "1px solid #365582", color: "#e7eefc" }} />
              <Area type="monotone" dataKey="risk" stroke="#6ce6ff" fill="#4fa1ff33" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="cyber-card p-6">
          <h3 className="text-lg font-semibold">What happens next</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-200">
            <p className="flex items-start gap-2"><FiCheckCircle className="mt-0.5 text-emerald-400" /> Low-risk logins are accepted silently.</p>
            <p className="flex items-start gap-2"><FiClock className="mt-0.5 text-amber-400" /> Medium-risk actions trigger user warning.</p>
            <p className="flex items-start gap-2"><FiAlertTriangle className="mt-0.5 text-rose-400" /> High-risk actions create security alerts.</p>
            <p className="flex items-start gap-2"><FiShield className="mt-0.5 text-sky-300" /> Critical risk can auto-lock account.</p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="cyber-card p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold mb-2">Live Security Feed</h3>
          <p className="text-xs text-slate-400 mb-4">Auto-refresh every 8 seconds with latest risk-tagged events.</p>
          <div className="space-y-2">
            {(feed.length ? feed : [{ event_time: new Date().toISOString(), title: "No live events yet", status: "normal", risk_score: 0.1 }]).map((item, idx) => (
              <div key={`${item.event_time}-${idx}`} className="cyber-card p-3 flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-100">{item.title}</p>
                  <p className="text-xs text-slate-400 mt-1">{new Date(item.event_time).toLocaleString()}</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs px-2 py-1 rounded-full border ${
                    item.status === "critical"
                      ? "text-rose-300 border-rose-400/40"
                      : item.status === "high"
                        ? "text-amber-300 border-amber-400/40"
                        : item.status === "warning"
                          ? "text-sky-300 border-sky-400/40"
                          : "text-emerald-300 border-emerald-400/40"
                  }`}>
                    {(item.status || "normal").toUpperCase()}
                  </span>
                  <p className="text-xs text-slate-400 mt-1">Risk {Math.round((item.risk_score || 0) * 100)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="cyber-card p-6">
          <h3 className="text-lg font-semibold">Personal Security Score</h3>
          <p className="metric-value text-sky-300 mt-2">{securityScore.security_score ?? 100}</p>
          <p className="text-xs text-slate-400">Weekly trust trend</p>
          <div className="mt-3 h-36">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={scoreTrend}>
                <XAxis dataKey="week" stroke="#9fb1d1" fontSize={10} />
                <YAxis stroke="#9fb1d1" fontSize={10} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "#0e1729", border: "1px solid #365582", color: "#e7eefc" }} />
                <Area type="monotone" dataKey="score" stroke="#4fa1ff" fill="#4fa1ff33" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-2 text-xs text-slate-300">
            {(securityScore.tips?.length ? securityScore.tips : ["Enable 2FA", "Review unknown devices", "Rotate passwords regularly"]).slice(0, 3).map((tip) => (
              <p key={tip}>- {tip}</p>
            ))}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="cyber-card p-6 lg:col-span-2">
          <div className="flex items-center gap-2 mb-2">
            <FiGlobe className="text-sky-300" />
            <h3 className="text-lg font-semibold">Threat Map (Country Bubbles)</h3>
          </div>
          <p className="text-xs text-slate-400 mb-4">Login origin intensity over recent activity window.</p>

          <div className="min-h-[180px] rounded-xl border border-slate-600/30 bg-slate-900/30 p-4 flex flex-wrap items-center gap-3">
            {mapBubbles.map((item) => {
              const size = 34 + Math.round((item.count / maxBubble) * 44);
              return (
                <div key={item.country} className="flex flex-col items-center gap-1">
                  <div
                    className="rounded-full border border-sky-300/40 bg-sky-400/20 flex items-center justify-center text-[11px] font-semibold text-sky-100"
                    style={{ width: `${size}px`, height: `${size}px` }}
                    title={`${item.country}: ${item.count} logins`}
                  >
                    {item.count}
                  </div>
                  <p className="text-[11px] text-slate-300 max-w-[88px] text-center leading-tight">{item.country}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="cyber-card p-6">
          <div className="flex items-center gap-2 mb-2">
            <FiMapPin className="text-amber-300" />
            <h3 className="text-lg font-semibold">Impossible Travel</h3>
          </div>
          {impossibleTravel ? (
            <div className="space-y-2 text-sm">
              <p className="text-slate-200"><span className="text-slate-400">From:</span> {impossibleTravel.from}</p>
              <p className="text-slate-200"><span className="text-slate-400">To:</span> {impossibleTravel.to}</p>
              <p className="text-slate-200"><span className="text-slate-400">Distance:</span> {impossibleTravel.distanceKm.toFixed(0)} km</p>
              <p className="text-slate-200"><span className="text-slate-400">Time gap:</span> {impossibleTravel.hours.toFixed(2)} h</p>
              <p className="text-slate-200"><span className="text-slate-400">Required speed:</span> {impossibleTravel.speed.toFixed(0)} km/h</p>
              <div className={`mt-3 inline-flex px-2 py-1 rounded-full border text-xs ${impossibleTravel.suspicious ? "text-rose-300 border-rose-400/40 bg-rose-500/10" : "text-emerald-300 border-emerald-400/40 bg-emerald-500/10"}`}>
                {impossibleTravel.suspicious ? "Suspicious travel pattern" : "Travel pattern plausible"}
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-300">
              <p>No enough geolocation pairs yet.</p>
              <p className="text-xs text-slate-400 mt-2">Run demo scenarios to populate travel intelligence.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
