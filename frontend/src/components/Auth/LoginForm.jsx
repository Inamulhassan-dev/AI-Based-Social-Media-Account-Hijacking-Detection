import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { FiEye, FiEyeOff, FiLock, FiShield, FiUser } from "react-icons/fi";
import toast from "react-hot-toast";

import { useAuth } from "../../context/AuthContext";

export default function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [typingData, setTypingData] = useState({ startTime: null, keystrokes: 0 });

  const { login } = useAuth();
  const navigate = useNavigate();

  const handlePasswordKeyDown = () => {
    if (!typingData.startTime) {
      setTypingData((prev) => ({ ...prev, startTime: Date.now() }));
    }
    setTypingData((prev) => ({ ...prev, keystrokes: prev.keystrokes + 1 }));
  };

  const calculateTypingSpeed = () => {
    if (typingData.startTime && typingData.keystrokes > 0) {
      const elapsed = (Date.now() - typingData.startTime) / 1000 / 60;
      return Math.round(typingData.keystrokes / elapsed);
    }
    return 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!username || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      const result = await login({ username, password, typing_speed: calculateTypingSpeed() });
      if (result.security_warning) {
        toast("Security alert: Some unusual activity detected");
      }
      toast.success("Login successful");
      navigate("/dashboard");
    } catch (error) {
      toast.error(error.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg mx-auto">
      <div className="glass rounded-2xl p-8 md:p-9 relative overflow-hidden">
        <div className="text-center mb-7">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-500/15 border border-sky-400/30 mb-4">
            <FiShield className="text-2xl text-sky-300" />
          </div>
          <h2 className="text-[40px] leading-tight font-bold">Welcome back</h2>
          <p className="text-slate-300 mt-2">Log in to continue monitoring account security.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="field-label">Username or email</label>
            <div className="relative">
            <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Username or Email"
              className="pro-input pro-input-icon"
              autoComplete="username"
            />
            </div>
          </div>

          <div>
            <label className="field-label">Password</label>
            <div className="relative">
            <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              onKeyDown={handlePasswordKeyDown}
              placeholder="Password"
              className="pro-input pro-input-icon"
              autoComplete="current-password"
            />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
              {showPassword ? <FiEyeOff /> : <FiEye />}
            </button>
            </div>
          </div>

          <button type="submit" disabled={loading} className="w-full cyber-btn py-3.5 text-sm disabled:opacity-50">
            {loading ? "Authenticating..." : "Sign in securely"}
          </button>

          <p className="text-xs text-slate-400">
            Your login behavior is analyzed for unusual activity (device, location, timing).
          </p>
        </form>

        <div className="mt-6 text-center">
          <p className="text-slate-300">
            Don&apos;t have an account? <Link to="/register" className="text-sky-300 hover:text-sky-200">Create one</Link>
          </p>
        </div>
      </div>
    </motion.div>
  );
}
