import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { FiChevronRight, FiLogOut, FiMenu, FiShield, FiX } from "react-icons/fi";

import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-[#070d1acc] backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3">
            <motion.div animate={{ rotateY: 360 }} transition={{ duration: 9, repeat: Infinity, ease: "linear" }}>
              <FiShield className="text-2xl text-[#7ed6ff]" />
            </motion.div>
            <div className="hidden sm:block">
              <p className="font-semibold tracking-wide text-white">ShieldAI</p>
              <p className="text-[11px] text-slate-400 -mt-0.5">Behavioral Threat Detection</p>
            </div>
          </Link>

          {user ? (
            <>
              <div className="hidden md:flex items-center gap-5">
                <Link to="/dashboard" className="text-sm text-slate-300 hover:text-white transition-colors">Dashboard</Link>
                <Link to="/alerts" className="text-sm text-slate-300 hover:text-white transition-colors">Alerts</Link>
                <Link to="/analytics" className="text-sm text-slate-300 hover:text-white transition-colors">Analytics</Link>
                {user.role === "admin" && <Link to="/admin" className="text-sm text-slate-300 hover:text-white transition-colors">Admin</Link>}
                <div className="h-6 w-px bg-white/15" />
                <div className="text-right">
                  <p className="text-sm text-white leading-none">{user.username}</p>
                  <p className="text-[11px] text-slate-400 mt-1 uppercase tracking-wide">{user.role}</p>
                </div>
                <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-red-400 transition-colors" title="Logout">
                  <FiLogOut />
                </button>
              </div>

              <button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden text-slate-100 text-2xl">
                {menuOpen ? <FiX /> : <FiMenu />}
              </button>
            </>
          ) : (
            <div className="flex gap-3">
              <Link to="/login" className="cyber-btn text-xs py-2 px-4">Log in</Link>
              <Link to="/register" className="cyber-btn btn-secondary text-xs py-2 px-4">Create account <FiChevronRight /></Link>
            </div>
          )}
        </div>

        {menuOpen && user && (
          <div className="md:hidden pb-4 space-y-2 text-slate-200">
            <Link to="/dashboard" onClick={() => setMenuOpen(false)} className="block">Dashboard</Link>
            <Link to="/alerts" onClick={() => setMenuOpen(false)} className="block">Alerts</Link>
            <Link to="/analytics" onClick={() => setMenuOpen(false)} className="block">Analytics</Link>
            {user.role === "admin" && <Link to="/admin" onClick={() => setMenuOpen(false)} className="block">Admin</Link>}
          </div>
        )}
      </div>
    </nav>
  );
}
