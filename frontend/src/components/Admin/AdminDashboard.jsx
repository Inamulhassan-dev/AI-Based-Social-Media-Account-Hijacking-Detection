import { useEffect, useState } from "react";

import { adminAPI } from "../../services/api";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    Promise.all([adminAPI.getStats(), adminAPI.getUsers()]).then(([statsRes, usersRes]) => {
      setStats(statsRes.data);
      setUsers(usersRes.data.users || []);
    });
  }, []);

  if (!stats) {
    return <div className="w-12 h-12 border-4 border-neon-purple border-t-transparent rounded-full animate-spin" />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold font-['Orbitron']" style={{ textShadow: "0 0 20px #b700ff" }}>ADMIN CONTROL CENTER</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="cyber-card p-4">Total Users: {stats.total_users}</div>
        <div className="cyber-card p-4">Locked Accounts: {stats.locked_users}</div>
        <div className="cyber-card p-4">Today Logins: {stats.today_logins}</div>
        <div className="cyber-card p-4">Unresolved Alerts: {stats.unresolved_alerts}</div>
      </div>

      <div className="cyber-card p-6 overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b border-gray-800">
              <th className="py-2">User</th>
              <th>Email</th>
              <th>Role</th>
              <th>Risk</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b border-gray-800/40">
                <td className="py-2">{user.username}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{Math.round((user.risk_score || 0) * 100)}%</td>
                <td>{user.is_locked ? "Locked" : "Active"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
